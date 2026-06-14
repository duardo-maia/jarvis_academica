# Arquitetura do Projeto — Jarvis — Assistente Acadêmico

## Visão Geral

O **Jarvis** é um assistente de IA com interface web que combina três domínios:

- **Agenda acadêmica**: consulta de tarefas, eventos, contatos e lembretes via banco de dados relacional.
- **Base de conhecimento**: consulta a materiais de estudo (PDFs sobre IA) via busca híbrida em banco vetorial.
- **Gerenciamento de tarefas**: CRUD visual de tarefas com prioridade e status na aba "Lista de Tarefas".

O usuário interage por uma interface Streamlit com duas abas: **Chat** (conversa com o agente) e **Lista de Tarefas** (gerenciamento visual).

---

## Estrutura de Módulos

Veja a árvore completa de diretórios no [README.md](README.md) da raiz do projeto.

---

## Fluxo de uma Pergunta (Chat)

```
Usuário (Streamlit)
       │
       ▼
   agente.py  ── Loop ReAct (máx. 8 passos)
       │
       ├── Pergunta sobre agenda/eventos?
       │         └── Gera SQL → executar_sql() → SQLite
       │
       └── Pergunta sobre IA/documentos?
                 └── [BUSCAR_DOCS] → consultar_documentos()
                           └── Busca híbrida (BM25 + ChromaDB)
                                     └── Chunks relevantes
       │
       ▼
  RESPOSTA FINAL → Streamlit exibe a resposta + chunks usados
```

> Tarefas são gerenciadas exclusivamente pela aba **Lista de Tarefas** — o chat foca em consultas de agenda e conteúdos de IA.

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

### Qwen2.5-14B-Instruct-AWQ
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

Veja a lista de tecnologias usadas no [README.md](README.md) da raiz do projeto.
