# 📝 Azure Function - Revisão Pedagógica SENAC/SC

Sistema serverless para revisão pedagógica automática de documentos Word usando Azure OpenAI, seguindo os padrões de qualidade didática do SENAC/SC.

## 🎯 Objetivo

Transformar materiais didáticos em conteúdo pedagógico de alta qualidade, com:
- **Linguagem dialógica** e tom conversacional
- **Simplificação de termos técnicos** mantendo precisão
- **Parágrafos e frases curtas** para melhor compreensão
- **Descrição detalhada de imagens** de forma pedagógica
- **Formatações padronizadas** (itálico para termos estrangeiros, negrito para alternativas corretas)
- **Preservação total** de estrutura, tabelas, imagens, tokens de mídia

## ✨ Funcionalidades Principais

### 1. Revisão Textual Pedagógica
- ✅ **Linguagem dialógica**: Transforma texto formal em tom de aula conversacional
- ✅ **Interações com aluno**: Adiciona "Você sabia?", "Reflita...", "Vamos entender..."
- ✅ **Simplificação técnica**: Explica termos complexos em linguagem acessível
- ✅ **Parágrafos curtos**: Divide textos longos em blocos de 5-6 linhas
- ✅ **Frases claras**: Converte frases longas em estruturas mais diretas
- ✅ **Correção ortográfica e gramatical**: Elimina erros e redundâncias

### 2. Descrição Pedagógica de Imagens
- ✅ **Análise visual com IA**: Usa GPT-4o Vision para interpretar imagens
- ✅ **Descrições detalhadas**: Gráficos, tabelas, diagramas, fotos explicados pedagogicamente
- ✅ **Inserção no texto**: Descrição adicionada como parágrafo após cada imagem
- ✅ **Contexto considerado**: Usa texto ao redor para descrição mais relevante
- ✅ **Tom didático**: Explicações claras como se estivesse ensinando para um aluno

### 3. Formatações Especiais
- ✅ **Itálico automático**: Palavras estrangeiras em itálico
- ✅ **Negrito em alternativas corretas**: Marca respostas de questões automaticamente
- ✅ **Preservação de tokens**: Mantém [[FIG1]], [[TAB1]], [[SA1]] intactos
- ✅ **Processamento de marcadores**: Interpreta <<ALT_CORRETA_INICIO>> ... <<ALT_CORRETA_FIM>>

### 4. Preservação de Estrutura
- ✅ **Imagens, gráficos, SmartArt**: Mantidos integralmente
- ✅ **Tabelas**: Processadas célula por célula, estrutura preservada
- ✅ **Listas e numerações**: Mantidas conforme original
- ✅ **Referências bibliográficas**: Preservadas sem alterações
- ✅ **Nomes fictícios**: Cria e mantém consistência de exemplos

### 5. Processamento Flexível
- ✅ **Documentos de qualquer tamanho**: 10, 50, 90+ páginas
- ✅ **HTTP REST API**: Upload via POST multipart/form-data
- ✅ **Blob Trigger automático**: Processa automaticamente ao fazer upload no Azure Storage
- ✅ **Cliente Python incluído**: Scripts prontos para uso

## 🏗️ Arquitetura

```
Documento Word (.docx)
        ↓
  HTTP POST ou Blob Upload
        ↓
   Azure Function (Python)
        ↓
  ┌──────────────────────────────┐
  │  Processamento Pedagógico    │
  ├──────────────────────────────┤
  │ 1. Extração (python-docx)    │
  │ 2. Revisão Textual (GPT-4o)  │
  │ 3. Descrição Imagens (Vision)│
  │ 4. Formatações Especiais     │
  │ 5. Reconstrução do Documento │
  └──────────────────────────────┘
        ↓
  Documento Revisado (.docx)
```

## 📊 Conformidade com Padrões SENAC

A solução implementa requisitos dos **7 EIXOS** de qualidade pedagógica:

### ✅ EIXO 1 — Linguagem e Estilo Comunicativo
- Linguagem dialógica e motivadora
- Tom conversacional (1ª pessoa do plural: "vamos", "veremos")
- Perguntas reflexivas e interações
- Elementos pedagógicos ("Observe que...", "Note que...")

### ✅ EIXO 2 — Estrutura de Frases e Parágrafos
- Parágrafos curtos (máximo 5-6 linhas)
- Frases diretas e claras
- Pontuação corrigida
- Texto menos denso

### ✅ EIXO 3 — As Palavras
- Simplificação de termos técnicos com explicações
- Palavras estrangeiras em itálico
- Remoção de linguagem excessivamente formal
- Correções ortográficas e gramaticais

### ⚠️ EIXO 4 — Organização e Estrutura do Conteúdo
**Implementado parcialmente:**
- Preservação de estrutura original
- Manutenção de ordem lógica

**Não implementado (requer esclarecimento do cliente):**
- Reorganização do simples para o complexo
- Criação de recursos gráficos adicionais
- Transições pedagógicas complexas

### ❌ EIXO 5 — Cálculos
**Não implementado (requer desenvolvimento especializado):**
- Decomposição de cálculos em etapas
- Explicações matemáticas passo a passo
- Geração de exercícios similares

Ver detalhes em: **[FEEDBACK_CLIENTE_IMPLEMENTACAO.md](FEEDBACK_CLIENTE_IMPLEMENTACAO.md)**

### ⚠️ EIXO 6 — Tabelas, Quadros e Fluxos
**Implementado:**
- Descrição pedagógica de imagens (gráficos, diagramas)
- Preservação de tabelas

**Não implementado (requer esclarecimento do cliente):**
- Explicação textual de dados em tabelas
- Orientação de leitura de recursos visuais

### ✅ EIXO 7 — Atividades Avaliativas
- Marcação de alternativas corretas em negrito
- Preservação de todas as alternativas
- Aplicação de formatações especiais

**Não implementado (requer desenvolvimento adicional):**
- Criação de perguntas reflexivas adicionais
- Feedback formativo expandido

## 🚀 Como Usar

### Via HTTP (Upload Manual)

```bash
# Usando o cliente Python incluído
python client.py documento.docx

# Resultado: documento_corrigido.docx
```

### Via Blob Storage (Automático)

```bash
# 1. Fazer upload do documento
python client.py --blob-upload documento.docx

# 2. Aguardar processamento automático (segundos)

# 3. Baixar documento revisado
python client.py --blob-download documento.docx
```

### API REST Direta

```bash
curl -X POST http://localhost:7071/api/correct-document \
  -F "file=@documento.docx" \
  -o documento_corrigido.docx
```

## 📦 Estrutura do Projeto

```
word-correction-function/
├── function_app.py                    # Azure Function principal
├── requirements.txt                   # Dependências Python
├── local.settings.json               # Configurações locais
├── client.py                         # Cliente Python completo
├── README.md                         # Esta documentação
├── FEEDBACK_CLIENTE_IMPLEMENTACAO.md # Análise detalhada de implementação
├── IMAGE_DESCRIPTION_GUIDE.md        # Guia de descrição de imagens
├── QUICKSTART.md                     # Início rápido (5 minutos)
└── docs/
    ├── ARCHITECTURE.md               # Arquitetura detalhada
    ├── FAQ.md                        # Perguntas frequentes
    └── BLOB_TRIGGER_GUIDE.md         # Guia de uso com Blob Storage
```

## 🔧 Configuração Rápida

### 1. Instalar Dependências

```bash
cd word-correction-function
pip install -r requirements.txt
```

### 2. Configurar Azure OpenAI

Edite `local.settings.json`:

```json
{
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://seu-endpoint.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "sua-chave-aqui",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-4o",
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=..."
  }
}
```

### 3. Executar Localmente

```bash
func start
```

### 4. Testar

```bash
python client.py seu-documento.docx
```

## 📚 Documentação Adicional

- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido (5 minutos)
- **[FEEDBACK_CLIENTE_IMPLEMENTACAO.md](FEEDBACK_CLIENTE_IMPLEMENTACAO.md)** - Análise completa da implementação dos 7 EIXOS
- **[IMAGE_DESCRIPTION_GUIDE.md](IMAGE_DESCRIPTION_GUIDE.md)** - Como funciona a descrição de imagens
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura técnica detalhada
- **[FAQ.md](FAQ.md)** - Perguntas frequentes e troubleshooting
- **[BLOB_TRIGGER_GUIDE.md](BLOB_TRIGGER_GUIDE.md)** - Processamento automático via Blob Storage

## 🎓 Prompt Pedagógico

O sistema usa um prompt especializado baseado nos padrões SENAC/SC:

```
Você é revisor pedagógico do SENAC/SC.

OBJETIVO:
Entregar o texto revisado, didático e padronizado, pronto para publicação.
O texto deve soar como uma AULA, em tom explicativo e próximo ao aluno.

REGRAS PRINCIPAIS:
1. Linguagem dialógica e conversacional
2. Simplificação de termos técnicos
3. Parágrafos curtos (máximo 5-6 linhas)
4. Frases claras e diretas
5. Preservação de estrutura e tokens de mídia
6. Formatações especiais (itálico, negrito)
7. Criação de nomes fictícios consistentes
...
```

Ver prompt completo em `function_app.py` → função `process_paragraph_text()`

## 💰 Custos Estimados

### Azure OpenAI (GPT-4o)
- **Input:** $2.50 por 1M tokens
- **Output:** $10.00 por 1M tokens
- **Imagens (Vision):** ~1000 tokens por imagem

### Exemplos:
| Documento | Páginas | Imagens | Custo Aproximado |
|-----------|---------|---------|------------------|
| Pequeno   | 10      | 5       | ~$0.10 - $0.20   |
| Médio     | 50      | 20      | ~$0.50 - $1.00   |
| Grande    | 90      | 40      | ~$1.00 - $2.00   |

**Nota:** Custos variam conforme complexidade do texto e quantidade de tokens processados.

## 🔍 Exemplos de Transformação

### Antes (texto original):
```
A diluição de medicamentos constitui procedimento técnico 
que demanda conhecimento farmacológico especializado para 
assegurar a correta administração terapêutica.
```

### Depois (revisão pedagógica):
```
Vamos entender a diluição de medicamentos?

É um procedimento técnico que exige conhecimento sobre os remédios 
para garantir que você administre corretamente o tratamento ao paciente. 
Você sabia que uma diluição incorreta pode comprometer toda a eficácia 
do medicamento?
```

### Imagem → Descrição Pedagógica:
**Original:** [Gráfico de barras sem descrição]

**Descrição gerada e inserida no texto:**
```
Descrição da imagem: O gráfico de barras apresenta a evolução 
das vendas da Empresa TechSolutions entre 2020 e 2024. Observe 
que a barra azul representa o ano de 2020 com R$ 100 mil em vendas, 
crescendo progressivamente até 2024 (barra verde) com R$ 450 mil. 
Note o crescimento acentuado entre 2022 e 2023, período em que 
a empresa lançou novos produtos.
```

## 🐛 Troubleshooting

### Erro: "Azure OpenAI não configurado"
✅ Verifique `local.settings.json` com endpoint e chave corretos

### Imagens não sendo descritas
✅ Confirme que `describe_images=True` em `function_app.py`
✅ Verifique se Pillow está instalado: `pip install Pillow`

### Tokens [[FIG1]] sendo removidos
✅ Sistema detecta e restaura automaticamente
✅ Veja logs: "Token [[FIG1]] foi removido, restaurando..."

### Formatações não aplicadas
✅ Verifique se texto contém marcadores: `*palavra*` para itálico
✅ Confirme processamento de `<<ALT_CORRETA_INICIO>>` ... `<<ALT_CORRETA_FIM>>`

Ver mais soluções em **[FAQ.md](FAQ.md)**

## 📈 Próximos Passos (Roadmap)

### Fase 1 - Testes e Validação ✅ (Atual)
- [x] Implementar EIXO 1, 2, 3 completos
- [x] Descrição pedagógica de imagens
- [x] Formatações especiais
- [ ] Testar com documentos reais do cliente
- [ ] Coletar feedback sobre qualidade

### Fase 2 - Esclarecimentos do Cliente
- [ ] Reunião para detalhamento de EIXO 4, 5, 6, 7
- [ ] Coletar exemplos "antes" e "depois" desejados
- [ ] Definir prioridades de funcionalidades
- [ ] Estabelecer métricas de qualidade

### Fase 3 - Desenvolvimento Avançado (se aprovado)
- [ ] EIXO 6: Explicação de tabelas e quadros
- [ ] EIXO 7: Feedbacks formativos robustos
- [ ] EIXO 5: Processamento especializado de cálculos
- [ ] EIXO 4: Reorganização de conteúdo (se permitido)

Ver análise completa em **[FEEDBACK_CLIENTE_IMPLEMENTACAO.md](FEEDBACK_CLIENTE_IMPLEMENTACAO.md)**

## 🤝 Contribuindo

Para sugestões ou melhorias:
1. Testar com documentos variados
2. Reportar casos de falha
3. Sugerir ajustes no prompt pedagógico
4. Compartilhar exemplos de transformações esperadas

## 📄 Licença

Solução desenvolvida para SENAC/SC.

## 📞 Suporte

- **Documentação**: Veja arquivos `.md` na pasta do projeto
- **Logs**: Execute com `func start --verbose` para debug
- **Análise de Implementação**: [FEEDBACK_CLIENTE_IMPLEMENTACAO.md](FEEDBACK_CLIENTE_IMPLEMENTACAO.md)

---

**Versão:** 2.0 - Revisão Pedagógica Completa  
**Data:** Novembro 2025  
**Status:** ✅ Implementação EIXO 1, 2, 3 | ⚠️ EIXO 4, 6, 7 parcial | ❌ EIXO 5 pendente
