# 📦 Guia de Uso - Blob Storage Trigger

## ✅ O que foi configurado?

A Azure Function agora tem **2 modos de operação**:

### 1. HTTP Endpoint (já funcionando)
```bash
curl -X POST http://localhost:7071/api/correct-document \
  -F "file=@documento.docx" \
  -o documento_corrigido.docx
```

### 2. **Blob Trigger (NOVO!)** ⭐
- **Upload automático**: Coloque um .docx em `documentos/input/`
- **Processamento automático**: A função detecta e processa
- **Resultado automático**: Documento corrigido aparece em `documentos/output/`

---

## 🚀 Como Usar o Blob Trigger

### Passo 1: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 2: Configurar containers (primeira vez)

```bash
python setup_blob_storage.py
```

Isso cria a estrutura:
```
documentos/
├── input/    ← Faça upload aqui
└── output/   ← Documentos corrigidos aparecem aqui
```

### Passo 3: Iniciar a função

```bash
func start
```

### Passo 4: Fazer upload de um documento

#### **Opção A: Via Azure Portal**
1. Acesse [portal.azure.com](https://portal.azure.com)
2. Vá para Storage Account `stiaeadprdbrs001`
3. Containers → `documentos`
4. Clique em "Upload"
5. Selecione pasta virtual: `input`
6. Faça upload do seu .docx

#### **Opção B: Via Azure Storage Explorer**
1. Abra Azure Storage Explorer
2. Conecte ao Storage Account `stiaeadprdbrs001`
3. Navegue para `documentos/input/`
4. Arraste e solte seu .docx

#### **Opção C: Via CLI**
```bash
az storage blob upload \
  --account-name stiaeadprdbrs001 \
  --container-name documentos \
  --name "input/meu_documento.docx" \
  --file "meu_documento.docx" \
  --auth-mode login
```

#### **Opção D: Via Python**
```python
from azure.storage.blob import BlobServiceClient

connection_string = "SUA_CONNECTION_STRING"
blob_service = BlobServiceClient.from_connection_string(connection_string)

# Upload
blob_client = blob_service.get_blob_client(
    container="documentos",
    blob="input/meu_documento.docx"
)

with open("meu_documento.docx", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

print("✅ Upload concluído!")
```

### Passo 5: Monitorar processamento

Observe os logs da função:
```
🔔 Blob Trigger ativado!
📄 Processando blob: input/meu_documento.docx
📊 Tamanho: 45678 bytes
✅ Arquivo lido: 45678 bytes
⚙️ Iniciando processamento com Azure OpenAI...
✅ Documento processado com sucesso!
📤 Salvo em: documentos/output/meu_documento.docx
```

### Passo 6: Baixar documento corrigido

#### **Via Azure Portal**
1. Vá para `documentos/output/`
2. Encontre seu arquivo
3. Clique em "Download"

#### **Via CLI**
```bash
az storage blob download \
  --account-name stiaeadprdbrs001 \
  --container-name documentos \
  --name "output/meu_documento.docx" \
  --file "meu_documento_corrigido.docx" \
  --auth-mode login
```

#### **Via Python**
```python
blob_client = blob_service.get_blob_client(
    container="documentos",
    blob="output/meu_documento.docx"
)

with open("documento_corrigido.docx", "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())

print("✅ Download concluído!")
```

---

## 📊 Estrutura do Blob Storage

```
stiaeadprdbrs001 (Storage Account)
└── documentos/ (Container)
    ├── input/                           ← UPLOAD AQUI
    │   ├── documento1.docx
    │   ├── documento2.docx
    │   └── documento3.docx
    │
    └── output/                          ← RESULTADO AQUI
        ├── documento1.docx (corrigido)
        ├── documento2.docx (corrigido)
        └── documento3.docx (corrigido)
```

---

## 🔄 Fluxo Completo

```
1. Usuário faz upload
   documentos/input/documento.docx
   
2. Blob Trigger detecta
   🔔 Novo arquivo detectado!
   
3. Função processa
   ⚙️ Azure OpenAI corrige texto
   
4. Resultado salvo automaticamente
   documentos/output/documento.docx
   
5. Usuário baixa resultado
   ✅ Documento corrigido!
```

---

## 🧪 Testar Configuração

```bash
# Verificar se containers existem
python setup_blob_storage.py --test

# Ou manualmente
az storage blob list \
  --account-name stiaeadprdbrs001 \
  --container-name documentos \
  --auth-mode login
```

---

## 🐛 Troubleshooting

### Problema: "Blob trigger não está funcionando"

**Soluções:**

1. **Verificar se a função está rodando**
   ```bash
   func start --verbose
   ```

2. **Verificar connection string**
   - Abra `local.settings.json`
   - Confirme que `AzureWebJobsStorage` está configurado

3. **Verificar containers**
   ```bash
   python setup_blob_storage.py --test
   ```

4. **Verificar extensão bundle**
   - Abra `host.json`
   - Confirme: `"version": "[4.*, 5.0.0)"`

5. **Reinstalar dependências**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Problema: "Arquivo não está sendo processado"

**Verificar:**
- ✅ Arquivo é .docx (não .doc)
- ✅ Upload foi para `documentos/input/`
- ✅ Azure OpenAI está configurado
- ✅ Função está rodando (sem erros nos logs)

### Problema: "Não vejo o arquivo em output/"

**Possíveis causas:**
- Erro no processamento (veja logs)
- Timeout (documento muito grande)
- Quota do Azure OpenAI excedida
- Permissões do Storage Account

**Verificar logs:**
```bash
func start --verbose
```

---

## 💡 Dicas

### Processar vários documentos
```bash
# Upload em lote via CLI
for file in *.docx; do
  az storage blob upload \
    --account-name stiaeadprdbrs001 \
    --container-name documentos \
    --name "input/$file" \
    --file "$file" \
    --auth-mode login
done
```

### Monitorar em tempo real
```bash
# Terminal 1: Executar função
func start --verbose

# Terminal 2: Watch do container output
az storage blob list \
  --account-name stiaeadprdbrs001 \
  --container-name documentos \
  --prefix "output/" \
  --auth-mode login
```

### Automatizar download dos resultados
```python
from azure.storage.blob import BlobServiceClient
import os

connection_string = os.environ.get("AzureWebJobsStorage")
blob_service = BlobServiceClient.from_connection_string(connection_string)

container_client = blob_service.get_container_client("documentos")
blobs = container_client.list_blobs(name_starts_with="output/")

for blob in blobs:
    filename = blob.name.replace("output/", "")
    blob_client = container_client.get_blob_client(blob.name)
    
    with open(f"corrigidos/{filename}", "wb") as f:
        f.write(blob_client.download_blob().readall())
    
    print(f"✅ Baixado: {filename}")
```

---

## 🚀 Deploy no Azure

Quando fizer deploy no Azure, o Blob Trigger funciona automaticamente:

```bash
func azure functionapp publish func-word-correction
```

**Vantagens:**
- ✅ Processamento 24/7 automático
- ✅ Escalabilidade infinita
- ✅ Sem necessidade de manter func rodando localmente

---

## 📞 Referências

- [Documentação Blob Trigger](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-blob-trigger)
- [Azure Storage Explorer](https://azure.microsoft.com/features/storage-explorer/)
- [Azure CLI - Blob Storage](https://learn.microsoft.com/cli/azure/storage/blob)

---

**Agora sua função processa documentos automaticamente! 🎉**
