# JARVIS Acadêmica — Assistente Inteligente para Estudantes

Assistente pessoal acadêmico desenvolvido como trabalho prático da disciplina. O sistema combina gerenciamento de agenda via linguagem natural com consulta a materiais de estudo usando RAG.

## Estrutura do Repositório

```
ia/
├── app.py                  # Entrada principal — interface web (Streamlit)
├── requirements.txt        # Dependências do projeto
├── .env                    # Chaves de API (não versionado)
│
├── jarvis_academica/       # Módulo do agente e banco de dados
│   ├── agente/             # Lógica do agente de IA (loop ReAct)
│   ├── database/           # Banco SQLite: tarefas, eventos, contatos
│   └── rag/                # Integração com o banco vetorial
│
└── banco_vetorial/         # Módulo de indexação e busca semântica
    ├── docs/               # PDFs e markdowns dos materiais
    ├── chunks/             # Divisão dos documentos em chunks
    ├── indexacao/          # Indexação com ChromaDB + BM25
    └── recuperacao/        # Busca híbrida e geração de resposta
```

## Pré-requisitos

- Python 3.10+
- Chave de acesso à API Gemma (`GEMMA_KEY`)

## Instalação

```bash
# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

Crie o arquivo `.env` na raiz com a chave da API:

```
GEMMA_KEY=sua_chave_aqui
```

## Executando

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

> O banco de dados SQLite é criado automaticamente na primeira execução. O banco vetorial precisa ser indexado antes do uso — veja o README em `banco_vetorial/`.

## Tecnologias

- **Streamlit** — interface web
- **Gemma 12B** — modelo de linguagem via API compatível com OpenAI
- **ChromaDB** — banco vetorial para busca semântica
- **BM25** — busca léxica para recuperação híbrida
- **SQLite** — armazenamento de agenda e tarefas

---

Trabalho em dupla — disciplina de Inteligência Artificial.
