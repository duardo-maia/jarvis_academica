# Jarvis — Assistente Acadêmico

Assistente pessoal acadêmico desenvolvido como trabalho prático da disciplina. O sistema combina gerenciamento de agenda via linguagem natural, consulta a materiais de estudo sobre IA usando RAG, e uma interface visual para gerenciamento de tarefas.

## Estrutura do Repositório

```
ia/
├── app.py                  # Entrada principal — interface web (Streamlit)
├── requirements.txt        # Dependências do projeto
├── ARQUITETURA.md          # Visão geral da arquitetura do sistema
├── .env.example            # Exemplos de chaves de API
├── .streamlit/config.toml  # Tema customizado da interface
├── logs/                   # Logs de execução (gerado)
│
├── jarvis_academica/       # Módulo do agente, banco de dados e estudos
│   ├── agente/             # Lógica do agente de IA (loop ReAct) e dispatch de ferramentas
│   ├── core/               # Constantes compartilhadas e configuração de logging
│   ├── database/           # Banco SQLite: agenda.py, tarefas.py, quiz.py e operacoes.py (conexão)
│   ├── estudos/            # Plano de estudos, geração/avaliação de quiz e recomendação de revisão
│   ├── rag/                # Integração com o banco vetorial
│   ├── avaliacao/          # Casos de teste (RAG + agente), verificação automática e análise de erros
│   ├── avaliar_sistema.py  # Script de avaliação automática (RAG e tool calling) — gera resultados_avaliacao.md
│   ├── resultados_avaliacao.md  # Relatório gerado: avaliação do sistema + análise de erros
│   └── requirements.txt    # Dependências específicas do módulo
│
└── banco_vetorial/         # Módulo de indexação e busca semântica
    ├── docs/               # PDFs, markdowns e DATASET.md
    ├── chunks/             # Divisão dos documentos em chunks
    ├── indexacao/          # Indexação com ChromaDB + BM25
    ├── recuperacao/        # Busca híbrida e geração de resposta
    ├── tests/              # Notebooks de teste
    └── data/               # Arquivos internos do ChromaDB (gerado)
```

## Pré-requisitos

- Python 3.10+
- Chave de acesso à API Qwen2.5-14B (`GEMMA_KEY`)

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

> O banco de dados SQLite é criado automaticamente na primeira execução. O banco vetorial já está indexado com os 10 documentos incluídos no repositório.

## Interface

O app possui uma sidebar e quatro abas:

- **Sidebar** — lista os próximos compromissos da agenda (próximos 7 dias), aberta por padrão
- **Chat com Jarvis** — converse para consultar/gerenciar sua agenda e tarefas, e tirar dúvidas sobre os conteúdos de IA indexados; um expander lista os 10 tópicos de IA disponíveis e sugestões clicáveis na tela inicial facilitam os primeiros testes. Cada resposta tem um expander **"🔧 Ver passos do agente"** mostrando, passo a passo, qual ferramenta foi chamada, com qual entrada e qual saída — tornando visível a decisão de tool calling da LLM
- **Lista de Tarefas** — adicione, conclua e remova tarefas visualmente; uma tarefa pode opcionalmente ser vinculada a um evento da agenda (campo "Vincular a um evento" no formulário), aparecendo no card como "📅 Vinculada a: \<evento\> (\<data\>)"
- **Agenda** — adicione e remova eventos visualmente (data, hora, local), além de consultar/gerenciar tudo via chat
- **Quiz** — active recall: escolha um tópico de IA, gere uma ou mais perguntas com base nos materiais indexados, responda e receba uma avaliação (nota de 0 a 10 e feedback) na hora; o Jarvis também recomenda tópicos para revisão com base no histórico de tentativas

## Tecnologias

- **Streamlit** — interface web
- **Qwen2.5-14B-Instruct-AWQ** — modelo de linguagem via API compatível com OpenAI
- **ChromaDB** — banco vetorial para busca semântica
- **BM25** — busca léxica para recuperação híbrida
- **SQLite** — armazenamento de agenda e tarefas

## Avaliação do Sistema e Análise de Erros

- [Avaliação do Sistema](https://docs.google.com/document/d/1B9lGyjpaM8oDmwE8KT9yKC4UHFiahfr9FF_9IT_OjWA/edit?usp=sharing)
- [Análise de Erros](https://docs.google.com/document/d/1QF7QNUcaRimMyLLR4VC2bqf_i_HslQSA1_tQSPwoG58/edit?usp=sharing)

O relatório também é gerado localmente em [`jarvis_academica/resultados_avaliacao.md`](jarvis_academica/resultados_avaliacao.md), produzido por `python avaliar_sistema.py`: 10 perguntas de RAG (documentos recuperados + resposta) e 8 cenários via o agente completo (ferramentas chamadas, entrada/saída e uma verificação automática que cruza datas/tarefas citadas com o banco real), seguido de uma seção de Análise de Erros com falhas reais documentadas. Classificações manuais já preenchidas são preservadas entre execuções do script.

---

Trabalho em dupla>:
Giovana da Silva M. Muhl
Eduardo S. Silva 

 — disciplina de Inteligência Artificial - Prof.: Dr. Edson Takashi / Faculdade de Computação, UFMS.
