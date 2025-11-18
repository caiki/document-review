import azure.functions as func
import logging
import io
import os
import base64
from typing import Dict, List, Optional
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from openai import AzureOpenAI
import json
from PIL import Image

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


def describe_image(image_bytes: bytes, context: str = "") -> str:
    """
    Gera descrição pontual de imagem usando Azure OpenAI Vision (GPT-4o).
    A descrição será inserida no texto do documento após a imagem.
    
    Args:
        image_bytes: Bytes da imagem
        context: Contexto adicional sobre a imagem (opcional)
        
    Returns:
        Descrição pontual da imagem em português
    """
    try:
        # Converter imagem para base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determinar tipo MIME da imagem
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img_format = img.format.lower()
            mime_type = f"image/{img_format}" if img_format in ['jpeg', 'jpg', 'png', 'gif', 'webp'] else "image/jpeg"
        except:
            mime_type = "image/jpeg"
        
        system_prompt = """Você é um especialista em descrição objetiva de imagens.

REGRAS:
1. Seja PONTUAL e OBJETIVO - máximo 2-3 frases curtas
2. SEM redundâncias ou repetições
3. Descreva apenas o essencial: tipo de imagem + conteúdo principal + dados relevantes
4. Se for gráfico/tabela: cite valores ou tendências principais
5. Se for diagrama: descreva o fluxo ou estrutura
6. Se for foto/ilustração: identifique elementos principais
7. NÃO use frases como "A imagem mostra", "Podemos ver", "Observa-se"
8. Inicie DIRETAMENTE com a descrição
9. Use linguagem clara e técnica quando apropriado

Formato: 1-3 frases diretas e objetivas em português."""

        user_prompt = "Descreva esta imagem de forma pontual e objetiva."
        if context:
            user_prompt += f"\n\nContexto: {context}"
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.2
        )
        
        description = response.choices[0].message.content.strip()
        logging.info(f"✅ Imagem descrita: {description[:80]}...")
        return description
        
    except Exception as e:
        logging.error(f"Erro ao descrever imagem: {str(e)}")
        return "[Descrição indisponível]"


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


def process_word_document(file_content: bytes, describe_images: bool = True) -> bytes:
    """
    Processa documento Word completo mantendo formatação, imagens, tabelas, etc.
    Adiciona descrições automáticas às imagens usando Azure OpenAI Vision.
    
    Args:
        file_content: Conteúdo binário do documento Word
        describe_images: Se True, adiciona descrições às imagens
        
    Returns:
        Conteúdo binário do documento corrigido
    """
    # Carregar documento da memória
    doc_stream = io.BytesIO(file_content)
    doc = Document(doc_stream)
    
    logging.info(f"Processando documento com {len(doc.paragraphs)} parágrafos")
    
    # Contar imagens no documento
    images_count = 0
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            images_count += 1
    logging.info(f"Imagens encontradas no documento: {images_count}")
    
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
    
    # Processar e descrever imagens
    if describe_images and images_count > 0:
        logging.info("🖼️ Iniciando descrição de imagens...")
        images_described = 0
        
        try:
            # Coletar parágrafos com imagens (iterar em ordem reversa para inserir descrições)
            paragraphs_with_images = []
            for idx, paragraph in enumerate(doc.paragraphs):
                has_image = False
                image_data = None
                
                for run in paragraph.runs:
                    if 'graphic' in run._element.xml:
                        try:
                            blip_elements = run._element.xpath('.//a:blip')
                            if blip_elements:
                                for blip in blip_elements:
                                    embed = blip.get(qn('r:embed'))
                                    if embed:
                                        image_part = doc.part.related_parts[embed]
                                        image_bytes = image_part.blob
                                        
                                        # Coletar contexto dos parágrafos vizinhos
                                        context_parts = []
                                        if idx > 0:
                                            context_parts.append(doc.paragraphs[idx - 1].text[:100])
                                        if paragraph.text:
                                            context_parts.append(paragraph.text[:100])
                                        if idx < len(doc.paragraphs) - 1:
                                            context_parts.append(doc.paragraphs[idx + 1].text[:100])
                                        context = " ".join(context_parts)
                                        
                                        # Gerar descrição
                                        description = describe_image(image_bytes, context)
                                        
                                        paragraphs_with_images.append((idx, paragraph._element, description))
                                        has_image = True
                                        break
                        except Exception as e:
                            logging.warning(f"  ⚠️ Erro ao processar imagem: {str(e)}")
                    
                    if has_image:
                        break
            
            # Inserir descrições após as imagens (ordem reversa para não afetar índices)
            for idx, para_element, description in reversed(paragraphs_with_images):
                try:
                    # Criar novo parágrafo com a descrição
                    parent = para_element.getparent()
                    
                    # Criar elemento de parágrafo usando python-docx
                    new_para = doc.add_paragraph()
                    new_para.text = description
                    # Opcional: aplicar estilo itálico à descrição
                    for run in new_para.runs:
                        run.italic = True
                        run.font.size = run.font.size  # Mantém tamanho original
                    
                    new_para_element = new_para._element
                    
                    # Inserir logo após o parágrafo da imagem
                    parent.insert(parent.index(para_element) + 1, new_para_element)
                    
                    images_described += 1
                    logging.info(f"  ✅ Imagem {images_described} descrita e inserida no texto")
                    
                except Exception as e:
                    logging.warning(f"  ⚠️ Erro ao inserir descrição: {str(e)}")
            
            logging.info(f"✅ Total de imagens descritas: {images_described}")
            
        except Exception as e:
            logging.error(f"Erro ao processar imagens: {str(e)}")
    
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