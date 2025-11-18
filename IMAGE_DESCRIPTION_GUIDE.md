# 🖼️ Descrição Automática de Imagens

## ✅ Funcionalidade Implementada!

A Azure Function agora **descreve automaticamente todas as imagens** dos documentos Word usando **Azure OpenAI Vision (GPT-4o)**.

---

## 🎯 O que faz?

### Antes (sem descrição):
```
[Imagem de gráfico]

Próximo parágrafo do documento...
```

### Depois (com descrição automática inserida no texto):
```
[Imagem de gráfico]

Gráfico de barras com evolução de vendas entre 2020 e 2024. 
Crescimento de R$ 100 mil para R$ 450 mil, com pico em 2023.

Próximo parágrafo do documento...
```

**Características da descrição:**
- ✅ Inserida como **parágrafo de texto** após a imagem
- ✅ Formatada em **itálico** para diferenciar do conteúdo original
- ✅ **Pontual e objetiva** - sem redundâncias (2-3 frases curtas)
- ✅ Foca no **essencial**: tipo + conteúdo + dados relevantes

---

## 🚀 Como Funciona?

### 1. Detecção de Imagens
```python
# A função detecta automaticamente todas as imagens no documento
Imagens encontradas no documento: 5
```

### 2. Análise com GPT-4o Vision
Para cada imagem:
- 📸 Extrai a imagem do documento Word
- 🤖 Envia para GPT-4o Vision API
- 📝 Recebe descrição **pontual e objetiva** em português
- ✍️ **Insere como parágrafo de texto** logo após a imagem
- 🎨 Aplica **formatação em itálico** para destacar

### 3. Descrição Pontual (SEM Redundâncias)
```python
# Sistema instrui o GPT-4o para descrições CURTAS
- Máximo 2-3 frases
- SEM frases como "A imagem mostra...", "Podemos ver..."
- Inicia DIRETAMENTE com a descrição
- Apenas o essencial: tipo + conteúdo + dados
```

---

## 📊 Exemplo Real

### Documento com imagens:
```
Parágrafo: "No último trimestre observamos..."

[IMAGEM: Gráfico de barras]

Parágrafo original seguinte: "Esses resultados demonstram..."
```

### Após processamento:
```
Parágrafo: "No último trimestre observamos..."

[IMAGEM: Gráfico de barras]

Gráfico de barras com receita trimestral de 2024. 
Q1: R$ 200k, Q2: R$ 350k, Q3: R$ 420k, Q4: R$ 510k.

Parágrafo original seguinte: "Esses resultados demonstram..."
```

### Logs durante processamento:
```
Processando documento com 45 parágrafos
Imagens encontradas no documento: 3
🖼️ Iniciando descrição de imagens...
✅ Imagem descrita: Gráfico de barras com receita trimestral...
  ✅ Imagem 1 descrita e inserida no texto
✅ Imagem descrita: Organograma da estrutura organizacional...
  ✅ Imagem 2 descrita e inserida no texto
✅ Imagem descrita: Fluxograma do processo de aprovação...
  ✅ Imagem 3 descrita e inserida no texto
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
# Linha ~260 (HTTP endpoint)
corrected_content = process_word_document(file_content, describe_images=False)

# Linha ~342 (Blob trigger)
corrected_content = process_word_document(file_content, describe_images=False)
```

### Personalizar Estilo da Descrição

Edite a função `describe_image()` em `function_app.py`:

```python
system_prompt = """Você é um especialista em descrição objetiva de imagens.

PERSONALIZE AQUI:
- Nível de detalhe (atualmente: 2-3 frases)
- Estilo (atualmente: pontual e objetivo)
- Tipo de informação prioritária
- Tom (técnico, coloquial, acadêmico)
"""
```

### Ajustar Formatação do Parágrafo de Descrição

Na função `process_word_document()`, linha ~218:

```python
# Atualmente: itálico aplicado
for run in new_para.runs:
    run.italic = True  # Remova esta linha para texto normal
    # run.bold = True  # Adicione para negrito
    # run.font.color.rgb = RGBColor(128, 128, 128)  # Cor cinza
```

### Mudar Comprimento das Descrições

Ajuste `max_tokens` na função `describe_image()`:

```python
max_tokens=300,  # Atual: descrições curtas (2-3 frases)
# max_tokens=150,  # Para descrições muito curtas (1 frase)
# max_tokens=600,  # Para descrições detalhadas (4-6 frases)
```

---

## 📝 Exemplos de Descrições Geradas

### Exemplo 1: Gráfico de Barras
**Imagem:** Gráfico de barras com vendas mensais

**Descrição Pontual Inserida no Texto:**
> *Gráfico de barras com vendas de janeiro a junho de 2024. Crescimento de R$ 50k para R$ 180k, com pico em maio.*

### Exemplo 2: Fluxograma
**Imagem:** Fluxograma de aprovação de documentos

**Descrição Pontual Inserida no Texto:**
> *Fluxograma de aprovação: Solicitação → Análise → Decisão → Aprovado (Publicação) ou Negado (Revisão).*

### Exemplo 3: Fotografia
**Imagem:** Foto de equipe em escritório

**Descrição Pontual Inserida no Texto:**
> *Equipe de 8 pessoas em escritório moderno com estações de trabalho individuais e luz natural.*

### Exemplo 4: Tabela/Infográfico
**Imagem:** Infográfico com dados estatísticos

**Descrição Pontual Inserida no Texto:**
> *Infográfico com três métricas principais: 85% satisfação do cliente, 42% aumento de vendas, 98% taxa de entrega.*

### Exemplo 5: Diagrama Técnico
**Imagem:** Diagrama de arquitetura de sistema

**Descrição Pontual Inserida no Texto:**
> *Arquitetura de três camadas: Frontend (React) → API (Node.js) → Banco de dados (PostgreSQL).*

**Características comuns:**
- ✅ **Curtas**: 1-3 frases
- ✅ **Diretas**: Sem "A imagem mostra...", "Podemos observar..."
- ✅ **Objetivas**: Apenas informações essenciais
- ✅ **Em itálico**: Diferenciadas do conteúdo original
- ✅ **Dados específicos**: Quando aplicável (valores, percentuais, quantidades)

---

## 🎯 Benefícios

### 1. Clareza e Objetividade
✅ Descrições pontuais facilitam leitura rápida
✅ SEM redundâncias ou informações desnecessárias
✅ Foco apenas no essencial da imagem

### 2. Integração no Documento
✅ Descrição aparece como **texto normal** no documento
✅ Formatada em **itálico** para diferenciar do conteúdo original
✅ Posicionada **logo após a imagem**
✅ Pode ser editada, copiada e formatada como qualquer texto

### 3. Acessibilidade
✅ Pessoas que não veem imagens entendem o conteúdo visual
✅ Útil quando imagens não carregam (email, impressão P&B)
✅ Facilita revisão sem precisar abrir cada imagem

### 4. Documentação
✅ Registro textual do conteúdo visual
✅ Facilita buscas no documento (Ctrl+F funciona)
✅ Melhor para arquivamento e referência futura

### 5. Automação
✅ Economiza tempo de descrição manual
✅ Consistência nas descrições
✅ Escalável para grandes volumes de documentos

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
