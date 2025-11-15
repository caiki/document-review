# Arquitetura da Solução - Correção de Documentos Word

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE / USUÁRIO                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Upload .docx
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AZURE FUNCTION                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  HTTP Trigger: /api/correct-document                     │  │
│  │  - Recebe documento Word                                 │  │
│  │  - Valida formato (.docx)                                │  │
│  │  - Extrai conteúdo preservando estrutura                 │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                                │
│                 ▼                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document Processor (python-docx)                        │  │
│  │  - Extrai parágrafos mantendo formatação                 │  │
│  │  - Extrai conteúdo de tabelas                            │  │
│  │  - Preserva imagens, gráficos, SmartArt                  │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                                │
│                 │ Texto por parágrafo                            │
│                 ▼                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Optimized Processor (opcional)                          │  │
│  │  - Cache de correções                                    │  │
│  │  - Processamento em batch                                │  │
│  │  - Estatísticas e logging                                │  │
│  └──────────────┬───────────────────────────────────────────┘  │
└─────────────────┼────────────────────────────────────────────────┘
                  │
                  │ API Call
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE OPENAI SERVICE                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  GPT-4 / GPT-3.5-turbo                                   │  │
│  │  - Correção ortográfica                                  │  │
│  │  - Correção gramatical                                   │  │
│  │  - Eliminação de redundâncias                            │  │
│  └──────────────┬───────────────────────────────────────────┘  │
└─────────────────┼────────────────────────────────────────────────┘
                  │
                  │ Texto corrigido
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AZURE FUNCTION                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document Reconstructor                                  │  │
│  │  - Aplica correções preservando formatação               │  │
│  │  - Mantém estrutura original                             │  │
│  │  - Reconstrói documento completo                         │  │
│  └──────────────┬───────────────────────────────────────────┘  │
└─────────────────┼────────────────────────────────────────────────┘
                  │
                  │ Download .docx corrigido
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE / USUÁRIO                        │
│                 Documento Word Corrigido                        │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo Alternativo: Blob Storage Trigger

```
┌─────────────────┐
│  User Upload    │
│   documento.docx│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Azure Blob Storage             │
│  Container: input-documents     │
└────────┬────────────────────────┘
         │
         │ Blob Created Event
         ▼
┌─────────────────────────────────┐
│  Azure Function                 │
│  Blob Trigger                   │
│  - Detecta novo arquivo         │
│  - Processa automaticamente     │
└────────┬────────────────────────┘
         │
         │ Azure OpenAI
         ▼
┌─────────────────────────────────┐
│  Azure Blob Storage             │
│  Container: corrected-documents │
│  documento_corrigido.docx       │
└─────────────────────────────────┘
```

## 🧩 Componentes Principais

### 1. function_app.py
**Responsabilidade:** Entry point da Azure Function
- HTTP trigger para receber documentos
- Validação de entrada
- Orquestração do processamento
- Retorno do documento corrigido

### 2. python-docx
**Responsabilidade:** Manipulação de documentos Word
- Leitura de .docx preservando estrutura
- Extração de parágrafos e tabelas
- Escrita mantendo formatação original
- **Preserva:** imagens, gráficos, SmartArt, estilos

### 3. Azure OpenAI
**Responsabilidade:** Processamento de linguagem natural
- Correção ortográfica
- Correção gramatical
- Eliminação de redundâncias
- **Modelos:** GPT-4, GPT-3.5-turbo

### 4. optimized_processor.py (Opcional)
**Responsabilidade:** Otimizações para documentos grandes
- Cache de correções repetidas
- Processamento em batch
- Logging e estatísticas
- Recuperação de erros

## 📊 Fluxo de Dados Detalhado

```
Input Document (.docx)
    │
    ├─► Metadata (preservado)
    │   ├─ Autor
    │   ├─ Data
    │   └─ Propriedades
    │
    ├─► Estrutura (preservada)
    │   ├─ Seções
    │   ├─ Cabeçalhos/Rodapés
    │   └─ Numeração de páginas
    │
    ├─► Conteúdo de Texto (PROCESSADO)
    │   ├─ Parágrafos → Azure OpenAI → Corrigido
    │   └─ Tabelas → Azure OpenAI → Corrigido
    │
    └─► Elementos Visuais (preservados intactos)
        ├─ Imagens
        ├─ Gráficos
        ├─ SmartArt
        └─ Formas

Output Document (.docx)
    └─► Mesmo conteúdo, texto corrigido
```

## 🎯 Decisões de Arquitetura

### Por que Azure Functions?
✅ Serverless - sem gerenciamento de infraestrutura
✅ Escalabilidade automática
✅ Pagamento por uso
✅ Suporte nativo para Python
✅ Fácil integração com Azure OpenAI

### Por que python-docx?
✅ Preserva formatação original
✅ Não depende de Microsoft Word instalado
✅ Trabalha diretamente com formato OOXML
✅ Suporte completo para tabelas, imagens, etc.
✅ Open source e bem mantido

### Por que Azure OpenAI?
✅ Modelos de linguagem avançados (GPT-4)
✅ Segurança e compliance empresarial
✅ Baixa latência (região Azure)
✅ Controle de custos e quotas
✅ Integração nativa com Azure

### Por que não usar Azure Document Intelligence?
- Document Intelligence é mais focado em OCR e extração
- Para correção de texto, OpenAI é mais adequado
- python-docx já fornece extração estruturada eficiente
- Evita custo adicional de serviço não necessário

### Por que não usar Azure AI Search?
- Search é para indexação e busca
- Não adiciona valor para correção ortográfica
- OpenAI já provê capacidades de NLP necessárias
- Mantém arquitetura simples e eficiente

## 🔧 Configurações e Tuning

### Para Documentos Pequenos (< 20 páginas)
```python
AZURE_OPENAI_DEPLOYMENT = "gpt-4"
BATCH_SIZE = 1  # Processar individualmente
USE_CACHE = False  # Não necessário
```

### Para Documentos Médios (20-50 páginas)
```python
AZURE_OPENAI_DEPLOYMENT = "gpt-4-turbo"
BATCH_SIZE = 3
USE_CACHE = True
```

### Para Documentos Grandes (> 50 páginas)
```python
AZURE_OPENAI_DEPLOYMENT = "gpt-35-turbo"
BATCH_SIZE = 5
USE_CACHE = True
TIMEOUT = 600  # 10 minutos
```

## 💰 Estimativa de Custos por Componente

### Azure Functions (Consumption Plan)
- Primeiras 1M execuções/mês: **GRÁTIS**
- Depois: ~$0.20 por milhão de execuções
- **Custo médio:** < $1/mês para uso moderado

### Azure OpenAI (GPT-4)
- Input: $0.03 por 1K tokens
- Output: $0.06 por 1K tokens
- **Doc 50 páginas:** ~$1.00-$1.50

### Azure Storage (se usar Blob Trigger)
- 5GB storage: **GRÁTIS**
- **Custo médio:** < $0.50/mês

### Total Estimado
- **Desenvolvimento/Teste:** < $2/mês
- **Produção (100 docs/mês):** $50-$150/mês
- **Uso intenso (1000 docs/mês):** $500-$1500/mês

## 🚀 Escalabilidade

### Vertical (Por Documento)
- Timeouts configuráveis (até 10 min)
- Processamento otimizado com cache
- Batch processing para eficiência

### Horizontal (Múltiplos Documentos)
- Azure Functions escala automaticamente
- Suporta processamento paralelo
- Sem limite de concorrência (exceto quotas OpenAI)

### Limites Conhecidos
- Documento individual: 2MB (limitação python-docx)
- Timeout máximo: 10 minutos (consumption plan)
- Rate limits Azure OpenAI: configurável por deployment

---

**Desenvolvido para SENAC-IA** | Arquitetura v1.0
