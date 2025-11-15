"""
Versão otimizada do processador de documentos para arquivos grandes.

Melhorias:
- Processamento em batch de parágrafos
- Cache de correções repetidas
- Estatísticas de processamento
- Tratamento de timeout
"""

import logging
from typing import List, Dict
from openai import AzureOpenAI
import hashlib


class OptimizedDocumentProcessor:
    """
    Processador otimizado para documentos Word grandes.
    """
    
    def __init__(self, openai_client: AzureOpenAI, deployment: str, batch_size: int = 5):
        """
        Args:
            openai_client: Cliente Azure OpenAI configurado
            deployment: Nome do deployment
            batch_size: Número de parágrafos pequenos para processar em batch
        """
        self.client = openai_client
        self.deployment = deployment
        self.batch_size = batch_size
        self.correction_cache: Dict[str, str] = {}
        self.stats = {
            "total_paragraphs": 0,
            "corrected": 0,
            "cached": 0,
            "unchanged": 0,
            "errors": 0
        }
    
    def _get_text_hash(self, text: str) -> str:
        """Gera hash para cache de correções."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def process_text(self, text: str, use_cache: bool = True) -> str:
        """
        Processa texto individual com cache opcional.
        
        Args:
            text: Texto para corrigir
            use_cache: Se True, usa cache para textos já corrigidos
            
        Returns:
            Texto corrigido
        """
        if not text or len(text.strip()) == 0:
            return text
        
        self.stats["total_paragraphs"] += 1
        
        # Verificar cache
        if use_cache:
            text_hash = self._get_text_hash(text)
            if text_hash in self.correction_cache:
                self.stats["cached"] += 1
                return self.correction_cache[text_hash]
        
        try:
            system_prompt = """Você é um corretor ortográfico profissional em português.
Corrija erros ortográficos, gramaticais e elimine redundâncias.
Retorne APENAS o texto corrigido, sem explicações."""

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Corrija:\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            corrected_text = response.choices[0].message.content.strip()
            
            # Salvar no cache
            if use_cache:
                self.correction_cache[text_hash] = corrected_text
            
            if corrected_text != text:
                self.stats["corrected"] += 1
            else:
                self.stats["unchanged"] += 1
            
            return corrected_text
            
        except Exception as e:
            logging.error(f"Erro ao processar texto: {str(e)}")
            self.stats["errors"] += 1
            return text
    
    def process_batch(self, texts: List[str]) -> List[str]:
        """
        Processa múltiplos textos em uma única chamada à API.
        
        Args:
            texts: Lista de textos para corrigir
            
        Returns:
            Lista de textos corrigidos
        """
        if not texts:
            return []
        
        try:
            # Combinar textos com separadores
            combined_text = "\n\n---SEPARADOR---\n\n".join(texts)
            
            system_prompt = """Você é um corretor ortográfico profissional em português.
Corrija os textos abaixo, separados por ---SEPARADOR---.
Retorne os textos corrigidos mantendo os mesmos separadores.
Não adicione explicações, apenas os textos corrigidos."""

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_text}
                ],
                temperature=0.3,
                max_tokens=8000
            )
            
            corrected_combined = response.choices[0].message.content.strip()
            corrected_texts = corrected_combined.split("---SEPARADOR---")
            
            # Limpar e validar
            corrected_texts = [t.strip() for t in corrected_texts]
            
            # Se não retornou o mesmo número, processar individualmente
            if len(corrected_texts) != len(texts):
                logging.warning("Batch retornou número diferente de textos, processando individualmente")
                return [self.process_text(t) for t in texts]
            
            self.stats["total_paragraphs"] += len(texts)
            self.stats["corrected"] += sum(1 for orig, corr in zip(texts, corrected_texts) if orig != corr)
            
            return corrected_texts
            
        except Exception as e:
            logging.error(f"Erro no processamento em batch: {str(e)}")
            # Fallback para processamento individual
            return [self.process_text(t) for t in texts]
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do processamento."""
        return {
            **self.stats,
            "cache_size": len(self.correction_cache),
            "efficiency": f"{(self.stats['cached'] / max(self.stats['total_paragraphs'], 1)) * 100:.1f}%"
        }
    
    def clear_cache(self):
        """Limpa o cache de correções."""
        self.correction_cache.clear()
        logging.info("Cache de correções limpo")


# Função auxiliar para usar no function_app.py
def create_optimized_processor(client: AzureOpenAI, deployment: str) -> OptimizedDocumentProcessor:
    """
    Cria um processador otimizado.
    
    Uso no function_app.py:
    
    ```python
    from optimized_processor import create_optimized_processor
    
    # Criar processador global
    processor = create_optimized_processor(client, AZURE_OPENAI_DEPLOYMENT)
    
    def process_word_document(file_content: bytes) -> bytes:
        doc = Document(io.BytesIO(file_content))
        
        # Coletar parágrafos para processamento em batch
        batch = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                if len(paragraph.text) < 200:  # Parágrafos pequenos em batch
                    batch.append(paragraph.text)
                    if len(batch) >= 5:  # Processar batch
                        corrected = processor.process_batch(batch)
                        # Aplicar correções...
                        batch = []
                else:  # Parágrafos grandes individualmente
                    corrected = processor.process_text(paragraph.text)
                    # Aplicar correção...
        
        # Processar batch restante
        if batch:
            corrected = processor.process_batch(batch)
        
        # Estatísticas
        stats = processor.get_statistics()
        logging.info(f"Estatísticas: {stats}")
        
        return doc_bytes
    ```
    """
    return OptimizedDocumentProcessor(client, deployment)


# Configuração recomendada para documentos grandes
LARGE_DOCUMENT_CONFIG = {
    "batch_size": 5,  # Processar até 5 parágrafos pequenos juntos
    "small_paragraph_threshold": 200,  # Caracteres
    "use_cache": True,  # Usar cache para parágrafos repetidos
    "timeout": 600,  # 10 minutos
    "max_retries": 3,  # Número de tentativas em caso de erro
}


def log_processing_progress(current: int, total: int, stats: Dict):
    """
    Loga progresso do processamento.
    
    Args:
        current: Parágrafo atual
        total: Total de parágrafos
        stats: Estatísticas do processador
    """
    if current % 10 == 0 or current == total:
        progress = (current / total) * 100
        logging.info(
            f"Progresso: {current}/{total} ({progress:.1f}%) | "
            f"Corrigidos: {stats['corrected']} | "
            f"Cache: {stats['cached']} | "
            f"Erros: {stats['errors']}"
        )
