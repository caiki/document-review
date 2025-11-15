# Word Correction Azure Function

Solução Azure Functions para correção ortográfica e eliminação de redundâncias em documentos Word usando Azure OpenAI.

## 📋 Características

- ✅ Correção ortográfica completa em português
- ✅ Eliminação de redundâncias e repetições
- ✅ Preserva formatação original (negrito, itálico, etc.)
- ✅ Mantém imagens, tabelas, gráficos e SmartArt intactos
- ✅ Processa documentos de qualquer tamanho (10, 50, 90+ páginas)
- ✅ API REST simples via HTTP

## 🏗️ Arquitetura

```
Documento Word (.docx)
        ↓
  HTTP POST Request
        ↓
   Azure Function
        ↓
  python-docx (extração)
        ↓
  Azure OpenAI (correção)
        ↓
  python-docx (reconstrução)
        ↓
  Documento Corrigido (.docx)
```

## 📦 Pré-requisitos

1. **Azure Functions Core Tools** (v4+)
   ```bash
   # Verificar instalação
   func --version
   ```

2. **Python** 3.8, 3.9, 3.10, 3.11 ou 3.12

3. **Azure OpenAI Service**
   - Resource endpoint
   - API Key
   - Deployment de modelo (recomendado: GPT-4 ou GPT-3.5-turbo)

## 🚀 Configuração Local

### 1. Instalar Dependências

```bash
cd word-correction-function
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Edite o arquivo `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AZURE_OPENAI_ENDPOINT": "https://SEU_RECURSO.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "sua_chave_api_aqui",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-4",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview"
  }
}
```

**Obter credenciais Azure OpenAI:**
1. Acesse o [Portal Azure](https://portal.azure.com)
2. Navegue até seu recurso Azure OpenAI
3. Em "Keys and Endpoint", copie:
   - Endpoint
   - Key 1 ou Key 2
4. Em "Model deployments", anote o nome do deployment

### 3. Executar Localmente

```bash
func start
```

A função estará disponível em: `http://localhost:7071`

## 📡 Uso da API

### Endpoint: Correção de Documento

**POST** `/api/correct-document`

**Content-Type:** `multipart/form-data`

**Parâmetros:**
- `file`: Arquivo .docx para correção

**Exemplo usando cURL:**

```bash
curl -X POST http://localhost:7071/api/correct-document \
  -F "file=@documento.docx" \
  -o documento_corrigido.docx
```

**Exemplo usando Python:**

```python
import requests

url = "http://localhost:7071/api/correct-document"
files = {"file": open("documento.docx", "rb")}

response = requests.post(url, files=files)

if response.status_code == 200:
    with open("documento_corrigido.docx", "wb") as f:
        f.write(response.content)
    print("Documento corrigido com sucesso!")
else:
    print(f"Erro: {response.json()}")
```

**Exemplo usando PowerShell:**

```powershell
$uri = "http://localhost:7071/api/correct-document"
$filePath = "C:\caminho\para\documento.docx"

$form = @{
    file = Get-Item -Path $filePath
}

Invoke-RestMethod -Uri $uri -Method Post -Form $form -OutFile "documento_corrigido.docx"
```

### Endpoint: Health Check

**GET** `/api/health`

Verifica o status da função e configuração do Azure OpenAI.

```bash
curl http://localhost:7071/api/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "service": "word-correction-function",
  "azure_openai_configured": true
}
```

## 🌐 Deploy no Azure

### 1. Criar Function App no Azure

```bash
# Login no Azure
az login

# Criar Resource Group
az group create --name rg-word-correction --location eastus

# Criar Storage Account
az storage account create \
  --name stwordcorrection \
  --resource-group rg-word-correction \
  --location eastus \
  --sku Standard_LRS

# Criar Function App
az functionapp create \
  --resource-group rg-word-correction \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-word-correction \
  --storage-account stwordcorrection \
  --os-type Linux
```

### 2. Configurar Variáveis de Ambiente no Azure

```bash
az functionapp config appsettings set \
  --name func-word-correction \
  --resource-group rg-word-correction \
  --settings \
    "AZURE_OPENAI_ENDPOINT=https://SEU_RECURSO.openai.azure.com/" \
    "AZURE_OPENAI_API_KEY=sua_chave_api" \
    "AZURE_OPENAI_DEPLOYMENT=gpt-4" \
    "AZURE_OPENAI_API_VERSION=2024-02-15-preview"
```

### 3. Deploy da Função

```bash
func azure functionapp publish func-word-correction
```

### 4. Testar no Azure

```bash
curl -X POST https://func-word-correction.azurewebsites.net/api/correct-document \
  -F "file=@documento.docx" \
  -o documento_corrigido.docx
```

## 🔧 Configuração Avançada

### Ajustar Modelo de Correção

Edite a função `process_paragraph_text()` em `function_app.py` para personalizar o comportamento:

```python
system_prompt = """Você é um corretor ortográfico profissional em português.
Sua tarefa é:
1. Corrigir todos os erros ortográficos e gramaticais
2. Eliminar redundâncias e repetições desnecessárias
3. Manter o significado e o estilo original do texto
4. [ADICIONE SUAS REGRAS AQUI]
"""
```

### Otimização para Documentos Grandes

Para documentos muito grandes (>90 páginas), considere:

1. **Processar em lote:** Agrupe múltiplos parágrafos pequenos em uma única chamada
2. **Usar modelo mais rápido:** Troque `gpt-4` por `gpt-3.5-turbo` para maior velocidade
3. **Aumentar timeout:** Configure timeout maior no `host.json`

```json
{
  "functionTimeout": "00:10:00"
}
```

## 📊 Estimativa de Custos

**Azure OpenAI (GPT-4):**
- Documento de 10 páginas (~500 parágrafos): ~$0.15 - $0.30
- Documento de 50 páginas (~2500 parágrafos): ~$0.75 - $1.50
- Documento de 90 páginas (~4500 parágrafos): ~$1.35 - $2.70

**Azure Functions (Consumption Plan):**
- Primeiros 1 milhão de execuções: Gratuito
- Cobrado por tempo de execução

💡 **Dica:** Use GPT-3.5-turbo para reduzir custos em até 90%

## 🐛 Troubleshooting

### Erro: "Import could not be resolved"
```bash
pip install -r requirements.txt
```

### Erro: "Azure OpenAI configuration not found"
Verifique se as variáveis de ambiente estão configuradas corretamente em `local.settings.json`

### Documento não está sendo corrigido
1. Verifique os logs: `func start --verbose`
2. Confirme que o deployment do Azure OpenAI está ativo
3. Verifique quotas e limites no Azure Portal

### Timeout em documentos grandes
Aumente o timeout no `host.json`:
```json
{
  "functionTimeout": "00:10:00"
}
```

## 📝 Estrutura do Projeto

```
word-correction-function/
├── function_app.py          # Código principal da Azure Function
├── requirements.txt         # Dependências Python
├── host.json               # Configuração do Functions Host
├── local.settings.json     # Configurações locais (não commitar!)
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Este arquivo
```

## 🔐 Segurança

⚠️ **IMPORTANTE:** Nunca commite `local.settings.json` com credenciais reais!

- Use Azure Key Vault para armazenar secrets em produção
- Configure autenticação via Azure AD quando possível
- Limite o acesso da Function App apenas a IPs confiáveis

## 🤝 Contribuindo

Melhorias sugeridas:
- [ ] Adicionar suporte para batch processing via Blob Storage
- [ ] Implementar cache de correções
- [ ] Adicionar métricas e telemetria
- [ ] Suporte para outros idiomas

## 📄 Licença

Este projeto é fornecido como exemplo educacional.

## 📞 Suporte

Para questões sobre Azure OpenAI:
- [Documentação Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)

Para questões sobre Azure Functions:
- [Documentação Azure Functions](https://learn.microsoft.com/azure/azure-functions/)

---

**Desenvolvido com ❤️ para SENAC-IA**
