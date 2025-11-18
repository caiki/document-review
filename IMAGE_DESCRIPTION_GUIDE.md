# 🖼️ Descrição Automática de Imagens

## ✅ Funcionalidade Implementada!

A Azure Function agora **descreve automaticamente todas as imagens** dos documentos Word usando **Azure OpenAI Vision (GPT-4o)**.

---

## 🎯 O que faz?

### Antes (sem descrição):
```xml
<pic>
  <nvPicPr>
    <cNvPr id="1" name="Imagem1"/>
  </nvPicPr>
  <blip r:embed="rId4"/>
</pic>
```

### Depois (com descrição automática):
```xml
<pic>
  <nvPicPr>
    <cNvPr id="1" name="Imagem1" 
           descr="Gráfico de barras mostrando crescimento de vendas de 2020 a 2024"
           title="Gráfico de barras mostrando crescimento de vendas"/>
  </nvPicPr>
  <blip r:embed="rId4"/>
</pic>
```

---

## 🚀 Como Funciona?

### 1. Detecção de Imagens
```python
# A função detecta automaticamente todas as imagens no documento
Imagens encontradas no documento: 5
```

### 2. Análise com GPT-4o Vision
Para cada imagem:
- 📸 Extrai a imagem do documento
- 🤖 Envia para GPT-4o Vision
- 📝 Recebe descrição em português
- ✍️ Adiciona como alt text na imagem

### 3. Contexto Inteligente
```python
# Usa o texto ao redor da imagem como contexto
context = "Capítulo 3: Análise de Vendas..."
description = describe_image(image_bytes, context)
```

---

## 📊 Exemplo Real

### Documento com imagens:
```
Documento: Relatório Anual 2024
├── Parágrafo: "Análise de crescimento..."
├── Imagem 1: [gráfico de barras]
├── Parágrafo: "Nossa equipe..."
├── Imagem 2: [foto da equipe]
└── Parágrafo: "Resultados..."
    └── Imagem 3: [tabela de dados]
```

### Descrições geradas:
```
🖼️ Iniciando descrição de imagens...
  ✅ Imagem 1 descrita: "Gráfico de barras verticais mostrando crescimento..."
  ✅ Imagem 2 descrita: "Fotografia de grupo com aproximadamente 15 pessoas..."
  ✅ Imagem 3 descrita: "Tabela com dados financeiros divididos por trimestre..."
✅ Total de imagens descritas: 3
```

---

## 🎨 Tipos de Imagens Suportadas

✅ **Fotografias**
- Pessoas, lugares, objetos
- Descrição detalhada de elementos visuais

✅ **Gráficos e Diagramas**
- Gráficos de barras, pizza, linhas
- Fluxogramas, organigramas
- Diagramas técnicos

✅ **Tabelas e Dados Visuais**
- Tabelas complexas
- Infográficos
- Dashboards

✅ **Ilustrações e Ícones**
- Desenhos técnicos
- Símbolos e ícones
- Logotipos

✅ **Screenshots**
- Capturas de tela de software
- Interfaces de usuário
- Páginas web

✅ **Texto em Imagens**
- Cartazes
- Slides
- Documentos digitalizados (OCR)

---

## 🔧 Configuração

### Ativar/Desativar Descrição de Imagens

Por padrão, a descrição está **ATIVADA**.

Para desativar, edite `function_app.py`:
```python
# Linha ~208 (HTTP endpoint)
corrected_content = process_word_document(file_content, describe_images=False)

# Linha ~290 (Blob trigger)
corrected_content = process_word_document(file_content, describe_images=False)
```

### Personalizar Prompt de Descrição

Edite a função `describe_image()` em `function_app.py`:

```python
system_prompt = """Você é um especialista em descrição de imagens.

PERSONALIZE AQUI:
- Nível de detalhe
- Estilo de linguagem
- Foco específico (acessibilidade, técnico, etc.)
- Comprimento da descrição
"""
```

---

## 📝 Exemplos de Descrições Geradas

### Exemplo 1: Gráfico
**Imagem:** Gráfico de pizza com fatias coloridas

**Descrição Gerada:**
> "Gráfico de pizza dividido em 4 segmentos representando diferentes categorias de produtos. O maior segmento (40%) é azul e representa eletrônicos, seguido por verde (30%) para vestuário, amarelo (20%) para alimentos e vermelho (10%) para outros."

### Exemplo 2: Diagrama
**Imagem:** Fluxograma de processo

**Descrição Gerada:**
> "Fluxograma mostrando o processo de aprovação de documentos. Inicia com 'Solicitação', passa por 'Análise', seguida de uma decisão 'Aprovado?'. Se sim, vai para 'Publicação', se não, retorna para 'Revisão'."

### Exemplo 3: Fotografia
**Imagem:** Foto de escritório

**Descrição Gerada:**
> "Ambiente de escritório moderno com mesas de trabalho compartilhadas, computadores, plantas decorativas e janelas com luz natural. Aproximadamente 6 pessoas trabalhando em estações individuais."

### Exemplo 4: Screenshot
**Imagem:** Captura de tela de aplicativo

**Descrição Gerada:**
> "Interface de um aplicativo de gerenciamento de tarefas mostrando uma lista de afazeres com caixas de seleção, datas de vencimento e botões de ação 'Editar' e 'Excluir'."

---

## 🎯 Benefícios

### 1. Acessibilidade
✅ Pessoas com deficiência visual podem entender o conteúdo das imagens
✅ Leitores de tela conseguem narrar as descrições
✅ Conformidade com WCAG 2.1 (Web Content Accessibility Guidelines)

### 2. SEO e Indexação
✅ Documentos se tornam mais pesquisáveis
✅ Busca por conteúdo visual
✅ Melhor organização de arquivos

### 3. Documentação
✅ Histórico de imagens documentado
✅ Facilita revisões futuras
✅ Compartilhamento mais efetivo

### 4. Automação
✅ Economiza tempo de descrição manual
✅ Consistência nas descrições
✅ Escalabilidade para grandes volumes

---

## 💰 Considerações de Custo

### GPT-4o Vision Pricing
- **Input:** $2.50 por 1M tokens
- **Output:** $10.00 por 1M tokens
- **Imagens:** Aproximadamente 1000 tokens por imagem

### Exemplos de Custo:
| Documento | Imagens | Custo Aproximado |
|-----------|---------|------------------|
| 10 páginas | 5 imagens | ~$0.015 |
| 50 páginas | 20 imagens | ~$0.060 |
| 90 páginas | 40 imagens | ~$0.120 |

💡 **Nota:** O custo de descrição de imagens é adicional ao custo de correção de texto.

---

## 🔍 Logs e Monitoramento

Quando a função processa um documento com imagens, você verá:

```
Processando documento com 45 parágrafos
Imagens encontradas no documento: 3
Total de parágrafos corrigidos: 12
🖼️ Iniciando descrição de imagens...
✅ Imagem descrita: Gráfico de barras mostrando...
  ✅ Imagem 1 descrita
✅ Imagem descrita: Fotografia do time de...
  ✅ Imagem 2 descrita
✅ Imagem descrita: Diagrama de fluxo do processo...
  ✅ Imagem 3 descrita
✅ Total de imagens descritas: 3
✅ Documento processado com sucesso!
```

---

## 🧪 Testar Descrição de Imagens

### 1. Criar documento de teste com imagens
```python
from docx import Document
from docx.shared import Inches

doc = Document()
doc.add_heading('Documento de Teste - Imagens', 0)
doc.add_paragraph('Este documento contém imagens para teste.')

# Adicionar imagem
doc.add_picture('grafico.png', width=Inches(4))

doc.save('teste_com_imagens.docx')
```

### 2. Processar via HTTP
```bash
python client.py teste_com_imagens.docx
```

### 3. Processar via Blob Storage
```bash
python client.py --blob-upload teste_com_imagens.docx
```

### 4. Verificar resultado
Abra o documento processado no Word:
1. Clique com botão direito na imagem
2. "Formatar Imagem" → "Alt Text"
3. Veja a descrição gerada automaticamente

---

## 🔧 Troubleshooting

### Problema: "Imagens não estão sendo descritas"

**Verificar:**
1. GPT-4o está configurado no `local.settings.json`
2. `describe_images=True` na função
3. Documento realmente contém imagens inline
4. Pillow está instalado: `pip install Pillow`

### Problema: "Erro ao processar imagem"

**Soluções:**
- Verifique formato da imagem (JPG, PNG suportados)
- Confirme que imagem não está corrompida
- Veja logs detalhados: `func start --verbose`

### Problema: "Descrições muito genéricas"

**Melhorar:**
- Ajuste o `system_prompt` para mais detalhes
- Aumente `max_tokens` (atualmente 500)
- Forneça mais contexto do documento

---

## 📚 Documentação Técnica

### Estrutura XML das Imagens no Word

```xml
<w:drawing>
  <wp:inline>
    <wp:docPr id="1" name="Imagem1" descr="DESCRIÇÃO AQUI"/>
    <a:graphic>
      <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
        <pic:pic>
          <pic:blipFill>
            <a:blip r:embed="rId4"/>
          </pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

### Namespaces Utilizados
```python
from docx.oxml.ns import qn

qn('r:embed')  # Relacionamento da imagem
qn('wp:docPr')  # Propriedades do desenho
```

---

## 🎓 Melhores Práticas

### 1. Contexto é Importante
```python
# BOM: Fornece contexto
description = describe_image(image, "Capítulo sobre vendas 2024")

# RUIM: Sem contexto
description = describe_image(image, "")
```

### 2. Validar Descrições
- Revise descrições geradas em documentos críticos
- GPT-4o é muito preciso, mas não perfeito

### 3. Considerar Performance
- Descrição de imagens adiciona tempo de processamento
- Para documentos com muitas imagens (>50), considere processar em lote

### 4. Acessibilidade
- Descrições devem ser informativas, não decorativas
- Foque no conteúdo e propósito da imagem

---

## 🚀 Recursos Futuros

Possíveis melhorias:
- [ ] Detectar e pular imagens decorativas
- [ ] Diferentes níveis de detalhe (curto/médio/longo)
- [ ] Tradução automática de descrições
- [ ] OCR integrado para texto em imagens
- [ ] Classificação automática de imagens
- [ ] Geração de legendas numeradas

---

**Documentos agora são acessíveis e bem documentados automaticamente! 🎉**
