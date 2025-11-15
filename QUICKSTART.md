# Guia Rápido - Azure Function para Correção de Documentos Word

## ⚡ Início Rápido (5 minutos)

### 1. Configurar Azure OpenAI

```bash
# Edite local.settings.json com suas credenciais
{
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://SEU-RECURSO.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "sua-chave-aqui",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-4"
  }
}
```

### 2. Instalar Dependências

```bash
cd word-correction-function
pip install -r requirements.txt
```

### 3. Executar Localmente

```bash
func start
```

### 4. Testar

```bash
# Usando o script de teste
python test_function.py

# OU usando curl
curl -X POST http://localhost:7071/api/correct-document \
  -F "file=@seu_documento.docx" \
  -o documento_corrigido.docx
```

## 📂 Estrutura de Arquivos

```
word-correction-function/
├── function_app.py              # ⭐ Função principal (HTTP endpoint)
├── blob_trigger_function.py     # 📦 Versão com Blob Storage (opcional)
├── optimized_processor.py       # 🚀 Processador otimizado (para docs grandes)
├── client.py                    # 🔧 Cliente Python para usar a função
├── test_function.py             # ✅ Script de teste
├── requirements.txt             # 📋 Dependências
├── local.settings.json          # ⚙️ Configurações locais
├── deploy.ps1                   # 🚀 Script de deploy automatizado
└── README.md                    # 📖 Documentação completa
```

## 🎯 Casos de Uso

### Uso 1: Corrigir um documento via HTTP

```python
import requests

url = "http://localhost:7071/api/correct-document"
files = {"file": open("documento.docx", "rb")}
response = requests.post(url, files=files)

with open("documento_corrigido.docx", "wb") as f:
    f.write(response.content)
```

### Uso 2: Corrigir múltiplos documentos

```python
from client import WordCorrectionClient

client = WordCorrectionClient("http://localhost:7071")
files = ["doc1.docx", "doc2.docx", "doc3.docx"]
client.correct_multiple(files, output_dir="corrigidos")
```

### Uso 3: Processamento automático via Blob Storage

1. Configure blob trigger (ver `blob_trigger_function.py`)
2. Faça upload no container `input-documents`
3. Documentos corrigidos aparecem em `corrected-documents`

## 🔧 Configurações

### Modelos Recomendados

| Modelo | Uso | Custo | Velocidade |
|--------|-----|-------|------------|
| GPT-4 | Documentos importantes | Alto | Lento |
| GPT-4-turbo | Balanceado | Médio | Médio |
| GPT-3.5-turbo | Documentos grandes/batch | Baixo | Rápido |

### Otimizações para Documentos Grandes

```python
# No local.settings.json, use GPT-3.5-turbo
"AZURE_OPENAI_DEPLOYMENT": "gpt-35-turbo"

# Ou use o processador otimizado
from optimized_processor import create_optimized_processor
processor = create_optimized_processor(client, deployment)
```

## 🚀 Deploy no Azure

### Opção 1: Deploy Automatizado (Recomendado)

```powershell
.\deploy.ps1
```

### Opção 2: Deploy Manual

```bash
# 1. Criar recursos
az group create --name rg-word-correction --location eastus
az functionapp create --name func-word-correction ...

# 2. Configurar variáveis
az functionapp config appsettings set ...

# 3. Publicar
func azure functionapp publish func-word-correction
```

## 💰 Estimativa de Custos (GPT-4)

| Documento | Parágrafos | Custo Estimado |
|-----------|-----------|----------------|
| 10 páginas | ~500 | $0.15 - $0.30 |
| 50 páginas | ~2500 | $0.75 - $1.50 |
| 90 páginas | ~4500 | $1.35 - $2.70 |

💡 **Dica:** Use GPT-3.5-turbo para reduzir custos em até 90%

## 🐛 Troubleshooting

### Problema: "Import could not be resolved"
```bash
pip install -r requirements.txt
```

### Problema: "Azure OpenAI configuration not found"
Verifique `local.settings.json` com credenciais corretas

### Problema: Timeout em documentos grandes
```json
// Em host.json
{
  "functionTimeout": "00:10:00"
}
```

### Problema: Erro de autenticação Azure OpenAI
1. Verifique endpoint (deve terminar com `/`)
2. Confirme que a chave está correta
3. Verifique que o deployment existe

## 📊 Monitoramento

### Ver logs em tempo real

```bash
# Local
func start --verbose

# Azure
func azure functionapp logstream func-word-correction
```

### Verificar estatísticas

```python
# Após processamento, veja os logs para:
# - Total de parágrafos processados
# - Parágrafos corrigidos
# - Erros encontrados
```

## 🔐 Segurança

⚠️ **IMPORTANTE:**
- Nunca commite `local.settings.json`
- Use Azure Key Vault em produção
- Configure autenticação via Azure AD
- Limite acesso a IPs confiáveis

## 📞 Recursos

- [Documentação Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)
- [Documentação Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
- [python-docx Documentation](https://python-docx.readthedocs.io/)

## 🎓 Exemplos Avançados

### Personalizar prompt de correção

Edite `process_paragraph_text()` em `function_app.py`:

```python
system_prompt = """Você é um corretor técnico especializado.
Além de corrigir ortografia:
1. Mantenha termos técnicos em inglês
2. Use linguagem formal acadêmica
3. Verifique concordância nominal e verbal
"""
```

### Adicionar detecção de idioma

```python
from langdetect import detect

def process_paragraph_text(text: str) -> str:
    lang = detect(text)
    if lang != 'pt':
        logging.warning(f"Texto em {lang}, esperado 'pt'")
    # ... resto da função
```

### Gerar relatório de correções

```python
corrections_log = []

def process_paragraph_text(text: str) -> str:
    corrected = # ... correção
    if text != corrected:
        corrections_log.append({
            "original": text[:50],
            "corrected": corrected[:50]
        })
    return corrected
```

---

**Desenvolvido para SENAC-IA** | Última atualização: Novembro 2025
