"""
Cliente Python avançado para Azure Function de correção de documentos Word.

Funcionalidades:
- Correção via HTTP endpoint
- Upload/download de Blob Storage
- Processamento em lote
- Progress tracking
- Retry logic
- Monitoramento de status

Uso:
    # Correção simples via HTTP
    python client.py documento.docx
    
    # Processar múltiplos documentos
    python client.py *.docx --output-dir corrigidos
    
    # Via Blob Storage
    python client.py --blob-upload documento.docx
    
    # Monitorar blob storage
    python client.py --blob-monitor
"""

import requests
import argparse
import os
import json
import time
import sys
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class WordCorrectionClient:
    """Cliente para interagir com Azure Function de correção de documentos."""
    
    def __init__(self, endpoint: str = "http://localhost:7071", max_retries: int = 3):
        """
        Inicializa o cliente.
        
        Args:
            endpoint: URL base da Azure Function
            max_retries: Número máximo de tentativas em caso de falha
        """
        self.endpoint = endpoint.rstrip('/')
        self.max_retries = max_retries
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
    
    def health_check(self) -> Dict:
        """
        Verifica o status da função.
        
        Returns:
            Dicionário com informações de status
        """
        try:
            response = requests.get(f"{self.endpoint}/api/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def correct_document(self, 
                        input_path: str, 
                        output_path: Optional[str] = None,
                        verbose: bool = True) -> bool:
        """
        Envia documento para correção via HTTP.
        
        Args:
            input_path: Caminho do documento a ser corrigido
            output_path: Caminho para salvar documento corrigido (opcional)
            verbose: Mostrar mensagens de progresso
            
        Returns:
            True se sucesso, False caso contrário
        """
        # Validar arquivo de entrada
        if not os.path.exists(input_path):
            if verbose:
                print(f"❌ Erro: Arquivo não encontrado: {input_path}")
            return False
        
        if not input_path.lower().endswith('.docx'):
            if verbose:
                print(f"❌ Erro: Apenas arquivos .docx são suportados")
            return False
        
        # Definir output path se não fornecido
        if not output_path:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_corrigido.docx")
        
        if verbose:
            print(f"📤 Enviando: {input_path}")
            print(f"📥 Salvando em: {output_path}")
        
        # Tentar com retry
        for attempt in range(1, self.max_retries + 1):
            try:
                if verbose and attempt > 1:
                    print(f"   Tentativa {attempt}/{self.max_retries}...")
                
                # Abrir e enviar arquivo
                with open(input_path, 'rb') as f:
                    files = {
                        'file': (os.path.basename(input_path), f, 
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    }
                    
                    if verbose:
                        print("⏳ Processando... (isso pode levar alguns minutos)")
                    
                    response = requests.post(
                        f"{self.endpoint}/api/correct-document",
                        files=files,
                        timeout=600  # 10 minutos
                    )
                
                # Verificar resposta
                if response.status_code == 200:
                    # Salvar documento corrigido
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    file_size_kb = len(response.content) / 1024
                    if verbose:
                        print(f"✅ Sucesso! Documento corrigido ({file_size_kb:.2f} KB)")
                        print(f"📂 Arquivo: {output_path}")
                    
                    self.stats["success"] += 1
                    return True
                else:
                    if verbose:
                        print(f"⚠️ Erro: Status {response.status_code}")
                        try:
                            error_data = response.json()
                            print(f"   Mensagem: {error_data.get('error', 'Erro desconhecido')}")
                        except:
                            print(f"   Resposta: {response.text[:200]}")
                    
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        if verbose:
                            print(f"   Aguardando {wait_time}s antes de tentar novamente...")
                        time.sleep(wait_time)
                    
            except requests.exceptions.Timeout:
                if verbose:
                    print(f"⏱️ Timeout na tentativa {attempt}")
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    if verbose:
                        print(f"   Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
                    
            except requests.exceptions.ConnectionError:
                if verbose:
                    print(f"❌ Erro: Não foi possível conectar a {self.endpoint}")
                    print("   💡 Verifique se a função está rodando: func start")
                return False
                
            except Exception as e:
                if verbose:
                    print(f"❌ Erro inesperado: {str(e)}")
                return False
        
        self.stats["failed"] += 1
        if verbose:
            print("❌ Falha após todas as tentativas")
        return False
    
    def correct_multiple(self, 
                        input_paths: List[str], 
                        output_dir: Optional[str] = None,
                        verbose: bool = True) -> Dict:
        """
        Corrige múltiplos documentos.
        
        Args:
            input_paths: Lista de caminhos dos documentos
            output_dir: Diretório para salvar documentos corrigidos
            verbose: Mostrar mensagens de progresso
            
        Returns:
            Dicionário com estatísticas do processamento
        """
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            if verbose:
                print(f"📁 Diretório criado: {output_dir}")
        
        self.stats["total"] = len(input_paths)
        self.stats["start_time"] = datetime.now()
        
        results = {
            "files": [],
            "summary": {}
        }
        
        for i, input_path in enumerate(input_paths, 1):
            if verbose:
                print(f"\n{'='*60}")
                print(f"Processando {i}/{self.stats['total']}: {os.path.basename(input_path)}")
                print(f"{'='*60}")
            
            output_path = None
            if output_dir:
                filename = Path(input_path).name
                output_path = os.path.join(output_dir, filename.replace('.docx', '_corrigido.docx'))
            
            success = self.correct_document(input_path, output_path, verbose=verbose)
            
            results["files"].append({
                "input": input_path,
                "output": output_path,
                "status": "success" if success else "failed"
            })
        
        self.stats["end_time"] = datetime.now()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        # Resumo
        if verbose:
            print(f"\n{'='*60}")
            print("📊 RESUMO DO PROCESSAMENTO")
            print(f"{'='*60}")
            print(f"Total de arquivos: {self.stats['total']}")
            print(f"✅ Sucesso: {self.stats['success']}")
            print(f"❌ Falhas: {self.stats['failed']}")
            print(f"⏱️ Tempo total: {duration:.1f}s")
            if self.stats['success'] > 0:
                avg_time = duration / self.stats['success']
                print(f"⚡ Tempo médio: {avg_time:.1f}s por documento")
        
        results["summary"] = self.stats.copy()
        return results
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do processamento."""
        return self.stats.copy()


class BlobStorageClient:
    """Cliente para interagir com Azure Blob Storage."""
    
    def __init__(self, connection_string: str = None):
        """
        Inicializa cliente do Blob Storage.
        
        Args:
            connection_string: Connection string do Azure Storage
        """
        try:
            from azure.storage.blob import BlobServiceClient
            
            if not connection_string:
                # Tentar ler de local.settings.json
                try:
                    with open('local.settings.json', 'r') as f:
                        settings = json.load(f)
                        connection_string = settings.get('Values', {}).get('AzureWebJobsStorage')
                except:
                    pass
            
            if not connection_string:
                raise ValueError("Connection string não fornecida")
            
            self.blob_service = BlobServiceClient.from_connection_string(connection_string)
            self.container_name = "documentos"
            
        except ImportError:
            raise ImportError("azure-storage-blob não instalado. Execute: pip install azure-storage-blob")
    
    def upload_document(self, file_path: str, verbose: bool = True) -> bool:
        """
        Faz upload de documento para Blob Storage.
        
        Args:
            file_path: Caminho do arquivo
            verbose: Mostrar mensagens
            
        Returns:
            True se sucesso
        """
        try:
            filename = os.path.basename(file_path)
            blob_name = f"input/{filename}"
            
            if verbose:
                print(f"📤 Fazendo upload: {filename}")
                print(f"📍 Destino: {self.container_name}/{blob_name}")
            
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            if verbose:
                print(f"✅ Upload concluído!")
                print(f"💡 O documento será processado automaticamente pela Azure Function")
                print(f"📥 Resultado estará em: {self.container_name}/output/{filename}")
            
            return True
            
        except Exception as e:
            if verbose:
                print(f"❌ Erro no upload: {e}")
            return False
    
    def download_document(self, blob_name: str, output_path: str, verbose: bool = True) -> bool:
        """
        Baixa documento do Blob Storage.
        
        Args:
            blob_name: Nome do blob (ex: output/documento.docx)
            output_path: Caminho para salvar
            verbose: Mostrar mensagens
            
        Returns:
            True se sucesso
        """
        try:
            if verbose:
                print(f"📥 Baixando: {blob_name}")
            
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            with open(output_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            if verbose:
                file_size = os.path.getsize(output_path) / 1024
                print(f"✅ Download concluído ({file_size:.2f} KB)")
                print(f"📂 Arquivo: {output_path}")
            
            return True
            
        except Exception as e:
            if verbose:
                print(f"❌ Erro no download: {e}")
            return False
    
    def list_files(self, prefix: str = "", verbose: bool = True) -> List[str]:
        """
        Lista arquivos no Blob Storage.
        
        Args:
            prefix: Prefixo para filtrar (ex: "input/", "output/")
            verbose: Mostrar mensagens
            
        Returns:
            Lista de nomes de blobs
        """
        try:
            container_client = self.blob_service.get_container_client(self.container_name)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            blob_list = []
            if verbose:
                print(f"📁 Arquivos em {self.container_name}/{prefix}:")
            
            for blob in blobs:
                blob_list.append(blob.name)
                if verbose:
                    size_kb = blob.size / 1024
                    print(f"  - {blob.name} ({size_kb:.2f} KB)")
            
            if not blob_list and verbose:
                print("  (vazio)")
            
            return blob_list
            
        except Exception as e:
            if verbose:
                print(f"❌ Erro ao listar: {e}")
            return []
    
    def monitor_output(self, interval: int = 5, max_wait: int = 300):
        """
        Monitora pasta output/ aguardando novos documentos processados.
        
        Args:
            interval: Intervalo entre verificações (segundos)
            max_wait: Tempo máximo de espera (segundos)
        """
        print(f"👀 Monitorando documentos/output/ ...")
        print(f"   Verificando a cada {interval}s (máximo {max_wait}s)")
        print("   Pressione Ctrl+C para parar\n")
        
        seen_files = set(self.list_files("output/", verbose=False))
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < max_wait:
                current_files = set(self.list_files("output/", verbose=False))
                new_files = current_files - seen_files
                
                if new_files:
                    print(f"\n🆕 Novos arquivos detectados:")
                    for file in new_files:
                        print(f"   ✅ {file}")
                    seen_files = current_files
                
                time.sleep(interval)
                print(".", end="", flush=True)
            
            print(f"\n⏱️ Tempo máximo de espera atingido ({max_wait}s)")
            
        except KeyboardInterrupt:
            print("\n\n⛔ Monitoramento interrompido pelo usuário")


def main():
    """Função principal para uso via linha de comando."""
    parser = argparse.ArgumentParser(
        description='Cliente para Azure Function de correção de documentos Word',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Processar um documento via HTTP
  python client.py documento.docx

  # Processar múltiplos documentos
  python client.py *.docx --output-dir corrigidos

  # Especificar endpoint customizado
  python client.py documento.docx -e https://func-word-correction.azurewebsites.net

  # Verificar status da função
  python client.py --health

  # Fazer upload para Blob Storage
  python client.py --blob-upload documento.docx

  # Baixar de Blob Storage
  python client.py --blob-download output/documento.docx -o documento_corrigido.docx

  # Listar arquivos no Blob Storage
  python client.py --blob-list input/

  # Monitorar processamento no Blob Storage
  python client.py --blob-monitor
        """
    )
    
    # Argumentos principais
    parser.add_argument('files', nargs='*', help='Arquivo(s) .docx para processar')
    parser.add_argument('-e', '--endpoint', 
                       default='http://localhost:7071',
                       help='URL da Azure Function (default: http://localhost:7071)')
    parser.add_argument('-o', '--output', 
                       help='Arquivo ou diretório de saída')
    parser.add_argument('--output-dir',
                       help='Diretório de saída para múltiplos arquivos')
    parser.add_argument('--health', 
                       action='store_true',
                       help='Verificar status da função')
    parser.add_argument('--retries',
                       type=int,
                       default=3,
                       help='Número de tentativas em caso de falha (default: 3)')
    parser.add_argument('-q', '--quiet',
                       action='store_true',
                       help='Modo silencioso (menos mensagens)')
    
    # Argumentos Blob Storage
    blob_group = parser.add_argument_group('Blob Storage')
    blob_group.add_argument('--blob-upload',
                           metavar='FILE',
                           help='Fazer upload de arquivo para Blob Storage')
    blob_group.add_argument('--blob-download',
                           metavar='BLOB',
                           help='Baixar arquivo do Blob Storage')
    blob_group.add_argument('--blob-list',
                           metavar='PREFIX',
                           nargs='?',
                           const='',
                           help='Listar arquivos no Blob Storage')
    blob_group.add_argument('--blob-monitor',
                           action='store_true',
                           help='Monitorar pasta output/ por novos arquivos')
    blob_group.add_argument('--connection-string',
                           help='Connection string do Azure Storage')
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    # Health check
    if args.health:
        client = WordCorrectionClient(args.endpoint)
        print("🔍 Verificando status da função...")
        health = client.health_check()
        print(f"\nStatus: {health.get('status')}")
        print(f"Service: {health.get('service', 'N/A')}")
        if 'azure_openai_configured' in health:
            status = '✅' if health['azure_openai_configured'] else '❌'
            print(f"Azure OpenAI: {status}")
        if health.get('status') == 'error':
            print(f"Erro: {health.get('message')}")
            return 1
        return 0
    
    # Operações Blob Storage
    if args.blob_upload or args.blob_download or args.blob_list is not None or args.blob_monitor:
        try:
            blob_client = BlobStorageClient(args.connection_string)
            
            if args.blob_upload:
                success = blob_client.upload_document(args.blob_upload, verbose=verbose)
                return 0 if success else 1
            
            elif args.blob_download:
                output = args.output or os.path.basename(args.blob_download)
                success = blob_client.download_document(args.blob_download, output, verbose=verbose)
                return 0 if success else 1
            
            elif args.blob_list is not None:
                blob_client.list_files(args.blob_list, verbose=verbose)
                return 0
            
            elif args.blob_monitor:
                blob_client.monitor_output()
                return 0
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return 1
    
    # Processar arquivos via HTTP
    if not args.files:
        parser.print_help()
        return 0
    
    client = WordCorrectionClient(args.endpoint, max_retries=args.retries)
    
    if len(args.files) == 1:
        # Arquivo único
        output = args.output or args.output_dir
        success = client.correct_document(args.files[0], output, verbose=verbose)
        return 0 if success else 1
    else:
        # Múltiplos arquivos
        output_dir = args.output_dir or args.output or "corrigidos"
        results = client.correct_multiple(args.files, output_dir, verbose=verbose)
        return 0 if results["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
