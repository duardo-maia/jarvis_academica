# JARVIS Acadêmico — Assistente Inteligente para Estudantes

Assistente pessoal acadêmico desenvolvido como trabalho prático da disciplina. O sistema utiliza técnicas modernas de IA para ajudar estudantes a organizar rotinas e melhorar o desempenho nos estudos.

## Visão Geral

O JARVIS integra três pilares principais:

- **RAG** (Retrieval-Augmented Generation) — responde perguntas com base em materiais de estudo
- **Tool Calling** — a LLM decide dinamicamente quais ferramentas acionar
- **LLM** — modelo Gemma 12B como núcleo de raciocínio e geração de respostas

## Funcionalidades

| # | Funcionalidade | Entrega |
|---|---|---|
| 3.1 | Consulta a materiais de estudo via RAG | Trabalho 1 |
| 3.2 | Agenda acadêmica (aulas, provas, eventos) | Trabalho 1 |
| 3.3 | Lista de tarefas | Trabalho 1 |
| 3.4 | Planejamento de estudos integrado | Trabalho 2 |

## Tecnologias

- Python 3.10+
- Gemma 12B (via API compatível com OpenAI)
- ChromaDB — banco vetorial para o RAG
- LangChain ou equivalente — orquestração de pipeline

## Estrutura do Repositório

```
ia/
├── banco_vetorial/         # Módulo de busca semântica com ChromaDB
│   ├── docs/
│   │   └── documentos.txt # Documentos indexados no banco vetorial
│   ├── tests/
│   │   └── teste.ipynb    # Notebook para experimentos
│   └── main.py            # Carrega documentos no ChromaDB e consulta
├── .gitignore
└── README.md
```

> A estrutura será expandida conforme o desenvolvimento avança.

## Como Executar

```bash
# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute o módulo do banco vetorial
python banco_vetorial/main.py
```

## IAs Utilizadas no Desenvolvimento

- Claude Code — geração de documentacao e revisão do código

---

Trabalho em dupla — Entrega dividida em dois trabalhos.
