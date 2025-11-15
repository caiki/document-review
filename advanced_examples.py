"""
Exemplos de uso avançado da Azure Function de correção de documentos.

Este arquivo demonstra diferentes cenários e personalizações.
"""

# =============================================================================
# EXEMPLO 1: Cliente Python com Retry e Progress Bar
# =============================================================================

from typing import Optional
import requests
import time
from tqdm import tqdm


class AdvancedWordCorrectionClient:
    """Cliente avançado com retry logic e progress bar."""
    
    def __init__(self, endpoint: str, max_retries: int = 3):
        self.endpoint = endpoint.rstrip('/')
        self.max_retries = max_retries
    
    def correct_document_with_retry(self, input_path: str, output_path: str) -> bool:
        """Corrige documento com retry automático em caso de falha."""
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Tentativa {attempt}/{self.max_retries}...")
                
                with open(input_path, 'rb') as f:
                    files = {'file': f}
                    
                    # Progress bar simulada
                    with tqdm(total=100, desc="Processando", unit="%") as pbar:
                        response = requests.post(
                            f"{self.endpoint}/api/correct-document",
                            files=files,
                            timeout=600
                        )
                        pbar.update(100)
                
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ Sucesso!")
                    return True
                else:
                    print(f"⚠️ Erro: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout na tentativa {attempt}")
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
            except Exception as e:
                print(f"❌ Erro: {e}")
                return False
        
        print("❌ Falha após todas as tentativas")
        return False


# =============================================================================
# EXEMPLO 2: Processamento em Lote com Paralelização
# =============================================================================

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def process_document_batch_parallel(files: list[str], 
                                     endpoint: str,
                                     max_workers: int = 3) -> dict:
    """
    Processa múltiplos documentos em paralelo.
    
    Args:
        files: Lista de caminhos dos arquivos
        endpoint: URL da Azure Function
        max_workers: Número de threads paralelas
        
    Returns:
        Dicionário com resultados
    """
    results = {"success": [], "failed": []}
    
    def process_single(file_path):
        client = AdvancedWordCorrectionClient(endpoint)
        output = str(Path(file_path).with_suffix('')) + '_corrigido.docx'
        success = client.correct_document_with_retry(file_path, output)
        return file_path, success
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single, f): f for f in files}
        
        for future in tqdm(as_completed(futures), total=len(files), desc="Processando lote"):
            file_path, success = future.result()
            if success:
                results["success"].append(file_path)
            else:
                results["failed"].append(file_path)
    
    return results


# =============================================================================
# EXEMPLO 3: Personalização de Prompts por Tipo de Documento
# =============================================================================

CUSTOM_PROMPTS = {
    "tecnico": """Você é um revisor técnico especializado.
    - Mantenha termos técnicos em inglês (API, endpoint, etc.)
    - Use linguagem formal e precisa
    - Preserve nomenclaturas de código e comandos
    - Corrija apenas ortografia e gramática portuguesa""",
    
    "academico": """Você é um revisor acadêmico.
    - Use linguagem formal acadêmica
    - Mantenha citações e referências intactas
    - Corrija conforme normas ABNT
    - Preserve termos científicos latinos""",
    
    "juridico": """Você é um revisor jurídico.
    - Mantenha termos jurídicos precisos
    - Preserve citações de leis e artigos
    - Use linguagem formal jurídica
    - Não simplifique termos técnicos do direito""",
    
    "marketing": """Você é um revisor de marketing.
    - Mantenha tom persuasivo
    - Preserve chamadas para ação (CTAs)
    - Corrija mantendo impacto emocional
    - Não altere slogans ou frases de efeito"""
}


def create_custom_prompt_function(document_type: str) -> str:
    """
    Cria prompt customizado baseado no tipo de documento.
    
    Uso no function_app.py:
    
    ```python
    def process_paragraph_text(text: str, doc_type: str = "geral") -> str:
        if doc_type in CUSTOM_PROMPTS:
            system_prompt = CUSTOM_PROMPTS[doc_type]
        else:
            system_prompt = CUSTOM_PROMPTS["geral"]
        
        # ... resto da função
    ```
    """
    return CUSTOM_PROMPTS.get(document_type, CUSTOM_PROMPTS["geral"])


# =============================================================================
# EXEMPLO 4: Integração com Azure Blob Storage
# =============================================================================

from azure.storage.blob import BlobServiceClient
import io


class BlobStorageIntegration:
    """Integração com Azure Blob Storage para input/output."""
    
    def __init__(self, connection_string: str, function_endpoint: str):
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        self.function_endpoint = function_endpoint
    
    def process_blob_to_blob(self, 
                             input_container: str,
                             input_blob: str,
                             output_container: str,
                             output_blob: str) -> bool:
        """
        Baixa documento do Blob, processa, e salva resultado no Blob.
        """
        try:
            # Download do blob
            print(f"📥 Baixando {input_blob}...")
            blob_client = self.blob_service.get_blob_client(
                container=input_container,
                blob=input_blob
            )
            blob_data = blob_client.download_blob().readall()
            
            # Processar via Function
            print(f"⚙️ Processando...")
            files = {'file': (input_blob, blob_data)}
            response = requests.post(
                f"{self.function_endpoint}/api/correct-document",
                files=files,
                timeout=600
            )
            
            if response.status_code != 200:
                print(f"❌ Erro ao processar: {response.status_code}")
                return False
            
            # Upload do resultado
            print(f"📤 Enviando {output_blob}...")
            output_blob_client = self.blob_service.get_blob_client(
                container=output_container,
                blob=output_blob
            )
            output_blob_client.upload_blob(response.content, overwrite=True)
            
            print("✅ Concluído!")
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def process_container(self, 
                         input_container: str,
                         output_container: str,
                         pattern: str = "*.docx") -> dict:
        """Processa todos os documentos de um container."""
        
        container_client = self.blob_service.get_container_client(input_container)
        blobs = container_client.list_blobs()
        
        results = {"success": 0, "failed": 0}
        
        for blob in blobs:
            if blob.name.endswith('.docx'):
                output_name = blob.name.replace('.docx', '_corrigido.docx')
                success = self.process_blob_to_blob(
                    input_container, blob.name,
                    output_container, output_name
                )
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
        
        return results


# =============================================================================
# EXEMPLO 5: Logging Detalhado e Métricas
# =============================================================================

import logging
from datetime import datetime
import json


class DetailedLogger:
    """Logger com métricas detalhadas de processamento."""
    
    def __init__(self, log_file: str = "correction_metrics.json"):
        self.log_file = log_file
        self.metrics = []
    
    def log_correction(self, 
                      filename: str,
                      paragraphs_total: int,
                      paragraphs_corrected: int,
                      processing_time: float,
                      success: bool):
        """Registra métricas de uma correção."""
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "paragraphs_total": paragraphs_total,
            "paragraphs_corrected": paragraphs_corrected,
            "correction_rate": f"{(paragraphs_corrected/paragraphs_total*100):.1f}%",
            "processing_time_seconds": processing_time,
            "success": success
        }
        
        self.metrics.append(metric)
        
        # Salvar em arquivo
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
    
    def get_summary(self) -> dict:
        """Retorna resumo das métricas."""
        if not self.metrics:
            return {"message": "Nenhuma métrica registrada"}
        
        total_docs = len(self.metrics)
        successful = sum(1 for m in self.metrics if m["success"])
        avg_time = sum(m["processing_time_seconds"] for m in self.metrics) / total_docs
        
        return {
            "total_documents": total_docs,
            "successful": successful,
            "failed": total_docs - successful,
            "average_time_seconds": round(avg_time, 2),
            "total_paragraphs_corrected": sum(m["paragraphs_corrected"] for m in self.metrics)
        }


# =============================================================================
# EXEMPLO 6: Interface CLI Completa
# =============================================================================

import argparse
from enum import Enum


class DocumentType(Enum):
    TECNICO = "tecnico"
    ACADEMICO = "academico"
    JURIDICO = "juridico"
    MARKETING = "marketing"
    GERAL = "geral"


def create_cli():
    """Interface CLI avançada."""
    
    parser = argparse.ArgumentParser(
        description='Azure Function Word Correction - Advanced Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Processar um documento
  python advanced_examples.py documento.docx

  # Processar com tipo específico
  python advanced_examples.py documento.docx --type academico

  # Processar múltiplos documentos em paralelo
  python advanced_examples.py *.docx --parallel --workers 5

  # Processar container do Blob Storage
  python advanced_examples.py --blob-container input-docs --storage-connection "..."

  # Ver métricas
  python advanced_examples.py --metrics
        """
    )
    
    parser.add_argument('files', nargs='*', help='Arquivos .docx para processar')
    parser.add_argument('-e', '--endpoint', 
                       default='http://localhost:7071',
                       help='Endpoint da Azure Function')
    parser.add_argument('-t', '--type',
                       choices=[t.value for t in DocumentType],
                       default='geral',
                       help='Tipo de documento')
    parser.add_argument('-o', '--output-dir',
                       help='Diretório de saída')
    parser.add_argument('--parallel',
                       action='store_true',
                       help='Processar em paralelo')
    parser.add_argument('--workers',
                       type=int,
                       default=3,
                       help='Número de workers paralelos')
    parser.add_argument('--blob-container',
                       help='Container do Blob Storage')
    parser.add_argument('--storage-connection',
                       help='Connection string do Storage')
    parser.add_argument('--metrics',
                       action='store_true',
                       help='Mostrar métricas de processamento')
    
    return parser


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Exemplo 1: Cliente com retry
    print("=" * 60)
    print("EXEMPLO 1: Cliente com Retry")
    print("=" * 60)
    
    client = AdvancedWordCorrectionClient("http://localhost:7071")
    # client.correct_document_with_retry("documento.docx", "corrigido.docx")
    
    # Exemplo 2: Processamento paralelo
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Processamento Paralelo")
    print("=" * 60)
    
    # files = ["doc1.docx", "doc2.docx", "doc3.docx"]
    # results = process_document_batch_parallel(files, "http://localhost:7071")
    # print(f"Sucesso: {len(results['success'])}, Falhas: {len(results['failed'])}")
    
    # Exemplo 3: Logging
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Logging Detalhado")
    print("=" * 60)
    
    logger = DetailedLogger()
    # logger.log_correction("doc1.docx", 100, 45, 12.5, True)
    # logger.log_correction("doc2.docx", 200, 89, 25.3, True)
    # print(json.dumps(logger.get_summary(), indent=2))
    
    print("\n✅ Exemplos carregados com sucesso!")
    print("💡 Edite o código e mude 'if False:' para 'if True:' para testar")
