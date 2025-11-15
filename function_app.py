import azure.functions as func
import logging
import io
import os
from typing import Dict, List
from docx import Document
from openai import AzureOpenAI
import json

app = func.FunctionApp()

# Configuração do Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Inicializar cliente OpenAI
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)


def process_paragraph_text(text: str) -> str:
    """
    Processa um parágrafo usando Azure OpenAI para correção ortográfica e redundância.
    
    Args:
        text: Texto do parágrafo a ser corrigido
        
    Returns:
        Texto corrigido
    """
    if not text or len(text.strip()) == 0:
        return text
    
    try:
        system_prompt = """Você é um corretor ortográfico profissional em português.
Sua tarefa é:
1. Corrigir todos os erros ortográficos e gramaticais
2. Eliminar redundâncias e repetições desnecessárias
3. Manter o significado e o estilo original do texto
4. Retornar APENAS o texto corrigido, sem explicações ou comentários adicionais

IMPORTANTE: Retorne somente o texto corrigido, preservando a formatação quando possível."""

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Corrija este texto:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        corrected_text = response.choices[0].message.content.strip()
        return corrected_text
        
    except Exception as e:
        logging.error(f"Erro ao processar parágrafo com OpenAI: {str(e)}")
        return text  # Retorna texto original em caso de erro


def process_word_document(file_content: bytes) -> bytes:
    """
    Processa documento Word completo mantendo formatação, imagens, tabelas, etc.
    
    Args:
        file_content: Conteúdo binário do documento Word
        
    Returns:
        Conteúdo binário do documento corrigido
    """
    # Carregar documento da memória
    doc_stream = io.BytesIO(file_content)
    doc = Document(doc_stream)
    
    logging.info(f"Processando documento com {len(doc.paragraphs)} parágrafos")
    
    # Processar cada parágrafo mantendo formatação
    paragraphs_processed = 0
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():  # Apenas processar parágrafos com texto
            try:
                original_text = paragraph.text
                corrected_text = process_paragraph_text(original_text)
                
                # Preservar formatação aplicando texto corrigido aos runs
                if corrected_text != original_text:
                    # Limpar runs existentes
                    for run in paragraph.runs:
                        run.text = ""
                    
                    # Adicionar texto corrigido ao primeiro run (preserva estilo base)
                    if paragraph.runs:
                        paragraph.runs[0].text = corrected_text
                    else:
                        paragraph.add_run(corrected_text)
                    
                    paragraphs_processed += 1
                    
            except Exception as e:
                logging.error(f"Erro ao processar parágrafo: {str(e)}")
                continue
    
    logging.info(f"Total de parágrafos corrigidos: {paragraphs_processed}")
    
    # Processar tabelas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if paragraph.text.strip():
                        try:
                            original_text = paragraph.text
                            corrected_text = process_paragraph_text(original_text)
                            
                            if corrected_text != original_text:
                                for run in paragraph.runs:
                                    run.text = ""
                                if paragraph.runs:
                                    paragraph.runs[0].text = corrected_text
                                else:
                                    paragraph.add_run(corrected_text)
                                    
                        except Exception as e:
                            logging.error(f"Erro ao processar célula de tabela: {str(e)}")
                            continue
    
    # Salvar documento processado em memória
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    
    return output_stream.getvalue()


@app.route(route="correct-document", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def correct_document(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP endpoint para correção de documentos Word.
    
    Endpoint: POST /api/correct-document
    Content-Type: multipart/form-data
    
    Parâmetros:
        - file: Arquivo .docx para correção (upload)
        
    Retorna:
        - Arquivo .docx corrigido
    """
    logging.info('Recebida requisição para correção de documento Word')
    
    try:
        # Validar variáveis de ambiente
        if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
            return func.HttpResponse(
                json.dumps({
                    "error": "Configuração do Azure OpenAI não encontrada. Verifique as variáveis de ambiente."
                }),
                status_code=500,
                mimetype="application/json"
            )
        
        # Obter arquivo do request
        file = req.files.get('file')
        
        if not file:
            return func.HttpResponse(
                json.dumps({
                    "error": "Nenhum arquivo foi enviado. Use o campo 'file' no multipart/form-data"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Verificar extensão do arquivo
        filename = file.filename
        if not filename.lower().endswith('.docx'):
            return func.HttpResponse(
                json.dumps({
                    "error": "Apenas arquivos .docx são suportados"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Ler conteúdo do arquivo
        file_content = file.read()
        logging.info(f"Arquivo recebido: {filename} ({len(file_content)} bytes)")
        
        # Processar documento
        corrected_content = process_word_document(file_content)
        logging.info(f"Documento processado com sucesso ({len(corrected_content)} bytes)")
        
        # Retornar arquivo corrigido
        corrected_filename = filename.replace('.docx', '_corrigido.docx')
        
        return func.HttpResponse(
            body=corrected_content,
            status_code=200,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{corrected_filename}"'
            }
        )
        
    except Exception as e:
        logging.error(f"Erro ao processar documento: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": f"Erro ao processar documento: {str(e)}"
            }),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint de health check para verificar status da função.
    """
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "word-correction-function",
            "azure_openai_configured": bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY)
        }),
        status_code=200,
        mimetype="application/json"
    )


@app.blob_trigger(arg_name="inputblob", 
                  path="documentos/input/{name}",
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob",
                 path="documentos/output/{name}",
                 connection="AzureWebJobsStorage")
def blob_correct_document(inputblob: func.InputStream, outputblob: func.Out[bytes]) -> None:
    """
    Blob Trigger: Processa automaticamente documentos Word quando carregados no container.
    
    Trigger: Blob Upload em 'documentos/input/'
    Output: Blob em 'documentos/output/' com documento corrigido
    
    Exemplo:
    - Upload: documentos/input/documento.docx
    - Output: documentos/output/documento.docx (corrigido)
    """
    logging.info(f'🔔 Blob Trigger ativado!')
    logging.info(f'📄 Processando blob: {inputblob.name}')
    logging.info(f'📊 Tamanho: {inputblob.length} bytes')
    
    # Verificar se é um arquivo .docx
    if not inputblob.name.lower().endswith('.docx'):
        logging.warning(f'⚠️ Arquivo ignorado (não é .docx): {inputblob.name}')
        return
    
    try:
        # Validar configuração do Azure OpenAI
        if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
            logging.error("❌ Azure OpenAI não configurado!")
            return
        
        # Ler conteúdo do blob
        file_content = inputblob.read()
        logging.info(f'✅ Arquivo lido: {len(file_content)} bytes')
        
        # Processar documento
        logging.info('⚙️ Iniciando processamento com Azure OpenAI...')
        corrected_content = process_word_document(file_content)
        
        # Escrever no blob de saída
        outputblob.set(corrected_content)
        
        logging.info(f'✅ Documento processado com sucesso!')
        logging.info(f'📤 Salvo em: documentos/output/{inputblob.name.split("/")[-1]}')
        logging.info(f'📊 Tamanho final: {len(corrected_content)} bytes')
        
    except Exception as e:
        logging.error(f'❌ Erro ao processar {inputblob.name}: {str(e)}', exc_info=True)