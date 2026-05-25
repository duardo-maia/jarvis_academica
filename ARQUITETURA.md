# Arquitetura do Projeto — Jarvis Acadêmica

## Visão Geral

O **Jarvis Acadêmica** é um assistente de IA com interface web que combina dois domínios:

- **Agenda acadêmica**: gerenciamento de tarefas, eventos, contatos e lembretes via banco de dados relacional.
- **Base de conhecimento**: consulta a materiais de estudo (PDFs sobre IA) via busca híbrida em banco vetorial.

O usuário interage por uma interface Streamlit com duas abas: **Chat** (conversa com o agente) e **Lista de Tarefas** (CRUD visual).

---

## Estrutura de Módulos

```
ia/
├── app.py                      # Entrypoint — interface Streamlit
├── jarvis_academica/
│   ├── agente/
│   │   └── agente.py           # Loop ReAct: orquestra SQL e busca vetorial
│   ├── database/
│   │   ├── operacoes.py        # Funções de acesso ao SQLite
│   │   └── schema.sql          # Definição das tabelas
│   └── rag/
│       └── consulta.py         # Wrapper para o banco vetorial
└── banco_vetorial/
    ├── docs/
    │   ├── pdfs/               # PDFs originais
    │   ├── markdown/           # PDFs convertidos para texto
    │   └── converter_pdf.py    # Etapa 1: PDF → Markdown
    ├── chunks/
    │   ├── chunking.py         # Etapa 2: Markdown → chunks
    │   └── chunks.json         # Chunks gerados
    ├── indexacao/
    │   ├── indexar.py          # Etapa 3: indexação ChromaDB + BM25
    │   └── bm25_index.pkl      # Índice BM25 serializado
    ├── recuperacao/
    │   └── recuperar.py        # Busca híbrida + geração de resposta
    └── data/                   # Arquivos internos do ChromaDB
```

---

## Fluxo de uma Pergunta

```
Usuário (Streamlit)
       │
       ▼
   agente.py  ── Loop ReAct (máx. 8 passos)
       │
       ├── Pergunta sobre agenda/tarefas?
       │         └── Gera SQL → executar_sql() → SQLite
       │
       └── Pergunta sobre teoria/documentos?
                 └── [BUSCAR_DOCS] → consultar_documentos()
                           └── Busca híbrida (BM25 + ChromaDB)
                                     └── Chunks relevantes
       │
       ▼
  RESPOSTA FINAL → Streamlit exibe a resposta + chunks usados
```

---

## Pipeline do Banco Vetorial

O pipeline é executado uma única vez (ou ao adicionar novos documentos):

```
PDFs  →  converter_pdf.py  →  Markdowns
                                  │
                             chunking.py  →  chunks.json
                                                 │
                                            indexar.py
                                           /           \
                                      ChromaDB        BM25
                                    (semântico)      (léxico)
```

### Busca Híbrida

Para cada consulta, dois scores são calculados e combinados:

| Componente | Método | Peso padrão |
|---|---|---|
| ChromaDB | Embeddings (similaridade semântica) | 60% |
| BM25 | Frequência de termos (léxico) | 40% |

Os resultados são diversificados (máximo 2 chunks por documento fonte) antes de serem enviados ao modelo.

---

## Banco de Dados Relacional (SQLite)

Criado automaticamente na primeira execução.

| Tabela | Conteúdo |
|---|---|
| `tarefas` | Título, descrição, prioridade (`baixa`/`normal`/`alta`) e status |
| `eventos` | Título, data, horário, local e contato vinculado |
| `contatos` | Nome, telefone, e-mail e observações |
| `lembretes` | Alertas associados a eventos |

---

## IAs Utilizadas

### Gemma 3 12B (`google/gemma-3-12b-it`)
- **Papel**: LLM principal do projeto.
- **Onde é usado**: no agente ReAct (`agente.py`) para interpretar perguntas, decidir qual ferramenta usar e formular respostas; e no módulo de recuperação (`recuperar.py`) para gerar respostas a partir dos chunks recuperados.
- **Acesso**: API compatível com OpenAI hospedada em `llm.liaufms.org`.

### Claude (Anthropic)
- **Papel**: suporte ao desenvolvimento — tirar dúvidas sobre arquitetura, Python e boas práticas.
- **Onde é usado**: fora do código, como ferramenta de apoio durante o desenvolvimento do projeto.

### GPT (OpenAI)
- **Papel**: suporte ao desenvolvimento — correção de bugs, sugestões de código e revisão de lógica.
- **Onde é usado**: fora do código, como ferramenta de apoio durante o desenvolvimento do projeto.

---

## Tecnologias Principais

| Tecnologia | Uso |
|---|---|
| Streamlit | Interface web |
| SQLite | Banco de dados relacional da agenda |
| ChromaDB | Banco vetorial para busca semântica |
| BM25 (rank-bm25) | Busca léxica |
| OpenAI SDK | Cliente para a API do Gemma |
| python-dotenv | Gerenciamento de variáveis de ambiente |
