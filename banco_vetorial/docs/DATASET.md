# Dataset — Documentos Indexados no Banco Vetorial

## Origem

Os documentos foram coletados manualmente do site da **IBM** ([www.ibm.com](https://www.ibm.com)), que publica artigos explicativos sobre conceitos de Inteligência Artificial e tecnologia. Os textos foram salvos em formato PDF e inseridos no projeto para compor a base de conhecimento do Jarvis.

## Composição

- **Total de documentos:** 10 PDFs
- **Total de chunks gerados:** 457
- **Idioma:** inglês

| # | Tema | Tamanho do PDF | Chunks |
|---|---|---|---|
| DOC1 | Embedding | 136 KB | 38 |
| DOC2 | PLN (Processamento de Linguagem Natural) | 152 KB | 46 |
| DOC3 | RAG (Retrieval-Augmented Generation) | 148 KB | 33 |
| DOC4 | Banco Vetorial | 228 KB | 60 |
| DOC5 | Transformers | 292 KB | 52 |
| DOC6 | LLM (Large Language Models) | 188 KB | 52 |
| DOC7 | Quarto Chinês | 144 KB | 19 |
| DOC8 | Viés da IA | 116 KB | 29 |
| DOC9 | Deep Learning | 300 KB | 75 |
| DOC10 | Aprendizado de Máquina | 220 KB | 53 |

## Estratégia de Chunking

Os documentos são divididos em trechos menores usando **janela deslizante**, implementada em `chunks/chunking.py`:

| Parâmetro | Valor |
|---|---|
| Tamanho do chunk | 500 caracteres |
| Sobreposição | 100 caracteres |
| Passo efetivo | 400 caracteres |

A sobreposição garante que conceitos que aparecem na fronteira entre dois chunks não sejam perdidos na recuperação.

Cada chunk é armazenado com três campos:
- `id` — identificador único no formato `{nome-do-arquivo}-chunk-{n}`
- `text` — conteúdo textual do trecho
- `source` — nome do documento de origem (sem extensão)

## Limitações

- **Fonte única:** todos os documentos vêm da IBM, o que representa a perspectiva de uma única empresa de tecnologia. Conceitos podem ser apresentados com viés comercial ou terminologia específica da IBM.
- **Conteúdo estático:** os documentos foram coletados em um momento fixo. Atualizações, correções ou novos artigos publicados após a coleta não estão refletidos no índice.
- **Chunking por caractere:** a divisão por contagem de caracteres pode cortar no meio de frases ou parágrafos, gerando chunks sem contexto completo em alguns casos.
- **Idioma:** os documentos estão em inglês, enquanto o sistema responde em português. A tradução semântica é feita pelo modelo de embeddings e pelo LLM, o que pode introduzir imprecisões em termos técnicos.
