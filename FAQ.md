# ❓ FAQ - Perguntas Frequentes

## 📋 Geral

### P: Esta solução funciona com documentos de qualquer tamanho?
**R:** Sim! A solução foi projetada para funcionar com documentos de 10, 50, 90+ páginas. Para documentos muito grandes (>100 páginas), recomendamos usar `gpt-3.5-turbo` e o processador otimizado.

### P: Quais elementos do Word são preservados?
**R:** TUDO é preservado:
- ✅ Formatação de texto (negrito, itálico, sublinhado, cores, fontes)
- ✅ Imagens e fotos
- ✅ Gráficos do Word/Excel
- ✅ SmartArt
- ✅ Tabelas (com toda formatação)
- ✅ Cabeçalhos e rodapés
- ✅ Numeração de páginas
- ✅ Sumários
- ✅ Estilos personalizados
- ✅ Comentários e revisões

### P: A solução funciona offline?
**R:** Não. É necessário conexão com Azure OpenAI. A Azure Function pode rodar localmente, mas precisa de internet para acessar o serviço OpenAI.

---

## 💰 Custos

### P: Quanto custa processar um documento?
**R:** Depende do modelo e tamanho:

**GPT-4:**
- 10 páginas: ~$0.15-$0.30
- 50 páginas: ~$0.75-$1.50
- 90 páginas: ~$1.35-$2.70

**GPT-3.5-turbo:**
- 10 páginas: ~$0.02-$0.05
- 50 páginas: ~$0.10-$0.20
- 90 páginas: ~$0.15-$0.30

### P: Azure Functions tem custo?
**R:** Primeiro 1 milhão de execuções/mês são GRATUITAS. Depois disso, ~$0.20 por milhão. Para uso normal, o custo da Function é praticamente zero.

### P: Como reduzir custos?
**R:** 
1. Use `gpt-3.5-turbo` em vez de `gpt-4` (90% mais barato)
2. Ative cache de correções (evita reprocessar parágrafos repetidos)
3. Use batch processing quando possível

---

## 🔧 Configuração

### P: Onde consigo as credenciais do Azure OpenAI?
**R:** 
1. Acesse [portal.azure.com](https://portal.azure.com)
2. Navegue até seu recurso Azure OpenAI
3. Em "Keys and Endpoint", copie:
   - Endpoint
   - Key 1 ou Key 2
4. Em "Model deployments", anote o nome do deployment

### P: Preciso do Azure Document Intelligence?
**R:** **NÃO!** A solução usa apenas Azure OpenAI. Document Intelligence é para OCR/extração, não para correção de texto.

### P: Preciso do Azure AI Search?
**R:** **NÃO!** AI Search é para indexação e busca. Não adiciona valor para correção ortográfica.

### P: Qual modelo OpenAI devo usar?
**R:** 
- **GPT-4**: Melhor qualidade, mais caro, mais lento
- **GPT-4-turbo**: Balanceado
- **GPT-3.5-turbo**: Mais rápido, mais barato, boa qualidade

Para documentos importantes (acadêmicos, jurídicos): GPT-4
Para documentos gerais ou grandes volumes: GPT-3.5-turbo

---

## 🚀 Uso

### P: Como processar múltiplos documentos?
**R:** Use o cliente Python:
```python
from client import WordCorrectionClient

client = WordCorrectionClient("http://localhost:7071")
files = ["doc1.docx", "doc2.docx", "doc3.docx"]
client.correct_multiple(files, output_dir="corrigidos")
```

### P: Posso processar automaticamente documentos que chegam?
**R:** Sim! Use o Blob Storage trigger (veja `blob_trigger_function.py`):
1. Faça upload no container `input-documents`
2. A função processa automaticamente
3. Resultado aparece em `corrected-documents`

### P: Quanto tempo leva para processar?
**R:**
- 10 páginas: ~30s - 1min
- 50 páginas: ~2-5min
- 90 páginas: ~5-10min

(Varia conforme modelo e carga do Azure OpenAI)

### P: Posso processar em paralelo?
**R:** Sim! Veja `advanced_examples.py` para exemplos de processamento paralelo.

---

## 🐛 Problemas Comuns

### P: Erro "Import could not be resolved"
**R:** 
```bash
pip install -r requirements.txt
```

### P: Erro "Azure OpenAI configuration not found"
**R:** Verifique `local.settings.json`:
```json
{
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://SEU-RECURSO.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "sua-chave-aqui",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-4"
  }
}
```

### P: Timeout ao processar documento grande
**R:** Aumente o timeout no `host.json`:
```json
{
  "functionTimeout": "00:10:00"
}
```

### P: Documento não está sendo corrigido
**R:** 
1. Verifique logs: `func start --verbose`
2. Confirme que o deployment do Azure OpenAI está ativo
3. Verifique quotas no Azure Portal
4. Teste com documento pequeno primeiro

### P: Erro 429 (Rate Limit)
**R:** Azure OpenAI tem limites de taxa. Soluções:
1. Aumente a quota no Azure Portal
2. Implemente retry com backoff (já incluído no `advanced_examples.py`)
3. Use batch processing para reduzir chamadas

---

## 🔐 Segurança

### P: É seguro processar documentos confidenciais?
**R:** 
- ✅ Azure OpenAI **NÃO** usa seus dados para treinar modelos
- ✅ Dados são processados em sua região Azure
- ✅ Suporte a redes virtuais e private endpoints
- ✅ Compliance com LGPD, GDPR, etc.

### P: Como proteger minhas credenciais?
**R:**
1. **NUNCA** commite `local.settings.json` com credenciais reais
2. Use Azure Key Vault em produção
3. Use Managed Identity quando possível
4. Configure autenticação via Azure AD

### P: Posso limitar acesso à função?
**R:** Sim!
- Altere `auth_level` para `ADMIN` no código
- Configure autenticação Azure AD
- Restrinja por IP no Azure Portal
- Use API Management para controle adicional

---

## 📊 Performance

### P: Como otimizar para documentos grandes?
**R:**
1. Use `optimized_processor.py` (batch processing + cache)
2. Troque para `gpt-3.5-turbo`
3. Aumente timeout
4. Considere dividir documento em partes

### P: Posso processar vários documentos ao mesmo tempo?
**R:** Sim! Azure Functions escala automaticamente. Limite é sua quota do OpenAI.

### P: Como monitorar performance?
**R:**
- Use Application Insights (já configurado)
- Veja logs: `func azure functionapp logstream`
- Use métricas no Azure Portal
- Implemente logging customizado (veja `advanced_examples.py`)

---

## 🌐 Deploy

### P: Como fazer deploy no Azure?
**R:** Use o script automatizado:
```powershell
.\deploy.ps1
```

### P: Posso usar em produção?
**R:** Sim! A solução inclui:
- ✅ Tratamento de erros robusto
- ✅ Retry logic
- ✅ Logging detalhado
- ✅ Timeout configurável
- ✅ Escalabilidade automática

### P: Como atualizar o código após deploy?
**R:**
```bash
func azure functionapp publish nome-da-sua-function
```

### P: Posso usar em Docker?
**R:** Sim! Azure Functions suporta containers. Crie um Dockerfile:
```dockerfile
FROM mcr.microsoft.com/azure-functions/python:4-python3.11
# ... seu código
```

---

## 🎯 Casos Específicos

### P: Funciona com documentos em outros idiomas?
**R:** Sim, mas foi otimizado para português. Para outros idiomas, ajuste o prompt em `function_app.py`.

### P: Posso personalizar o tipo de correção?
**R:** Sim! Veja `advanced_examples.py` para prompts customizados por tipo de documento (técnico, acadêmico, jurídico, etc.).

### P: Funciona com documentos .doc (antigos)?
**R:** Não diretamente. Converta para .docx primeiro:
- No Word: Salvar Como → .docx
- Programaticamente: Use bibliotecas como `pywin32` ou `libreoffice`

### P: Posso adicionar outras validações além de ortografia?
**R:** Sim! Edite o prompt em `process_paragraph_text()` para incluir:
- Verificação de tom
- Detecção de plágio
- Análise de legibilidade
- etc.

---

## 💡 Dicas

### Melhor desempenho
```json
"AZURE_OPENAI_DEPLOYMENT": "gpt-35-turbo"
```

### Melhor qualidade
```json
"AZURE_OPENAI_DEPLOYMENT": "gpt-4"
```

### Balanceado
```json
"AZURE_OPENAI_DEPLOYMENT": "gpt-4-turbo"
```

### Para documentos técnicos
Use prompts customizados (veja `advanced_examples.py`)

### Para grandes volumes
Configure Blob Storage trigger + processamento automático

---

## 📞 Suporte

### P: Onde encontro mais ajuda?
**R:**
- 📖 `README.md` - Documentação completa
- ⚡ `QUICKSTART.md` - Guia rápido
- 🏗️ `ARCHITECTURE.md` - Arquitetura detalhada
- 💻 `advanced_examples.py` - Exemplos de código

### P: Onde reportar problemas?
**R:**
1. Verifique os logs: `func start --verbose`
2. Consulte esta FAQ
3. Revise a documentação
4. Verifique configurações do Azure OpenAI

### P: Como contribuir com melhorias?
**R:** O código está documentado e pronto para extensões. Áreas sugeridas:
- Suporte a mais formatos (ODT, RTF)
- Interface web
- Integração com SharePoint
- Análise de sentimento
- Detecção de plágio

---

**Última atualização:** Novembro 2025
