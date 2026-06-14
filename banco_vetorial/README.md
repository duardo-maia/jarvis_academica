# Banco Vetorial — Módulo de Indexação e Busca

Módulo responsável por indexar PDFs acadêmicos e recuperar trechos relevantes usando busca híbrida (semântica + léxica). É utilizado pelo Jarvis quando o usuário faz perguntas sobre os materiais de estudo.

## Documentos Indexados

A lista dos 10 documentos indexados, com origem, composição e estratégia de chunking,
está documentada em [`docs/DATASET.md`](docs/DATASET.md).

## Estrutura

```
banco_vetorial/
├── docs/
│   ├── pdfs/            # PDFs originais dos materiais
│   ├── markdown/        # Versão em texto dos documentos (gerada pelo converter_pdf.py)
│   └── converter_pdf.py # Converte PDFs para markdown
├── chunks/
│   ├── chunking.py      # Divide os documentos em trechos menores
│   └── chunks.json      # Resultado: lista de chunks com id, texto e fonte
├── indexacao/
│   ├── indexar.py       # Indexa os chunks no ChromaDB e no BM25
│   └── bm25_index.pkl   # Índice BM25 salvo em disco
├── recuperacao/
│   └── recuperar.py     # Busca híbrida + geração de resposta com Gemma
├── data/                # Arquivos internos do ChromaDB (gerado pelo indexar.py)
└── tests/
    └── teste.ipynb      # Notebook para experimentos
```

## Pipeline

O processo é feito em três etapas, executadas na ordem:

### 1. Converter PDFs para markdown

```bash
python banco_vetorial/docs/converter_pdf.py
```

Lê os PDFs de `docs/pdfs/` e gera os arquivos `.md` em `docs/markdown/`.

### 2. Dividir em chunks

```bash
python banco_vetorial/chunks/chunking.py
```

Lê os markdowns e gera `chunks/chunks.json` com os trechos divididos.

### 3. Indexar

```bash
python banco_vetorial/indexacao/indexar.py
```

Indexa os chunks no ChromaDB (busca semântica) e no BM25 (busca léxica). Gera os arquivos em `data/` e `indexacao/bm25_index.pkl`.

> Só é necessário reindexar quando novos documentos forem adicionados.

## Testando a Busca

Para testar a recuperação diretamente no terminal:

```bash
python banco_vetorial/recuperacao/recuperar.py
```

O script pedirá uma pergunta e retornará a resposta gerada pelo modelo com base nos documentos indexados.

## Como Funciona a Busca Híbrida

A busca combina scores do ChromaDB (semântico) e do BM25 (léxico), com diversificação
dos chunks por documento fonte. Detalhes da fórmula e dos pesos estão em
[ARQUITETURA.md](../ARQUITETURA.md#busca-híbrida).

## Adicionando Novos Documentos

1. Coloque o PDF em `docs/pdfs/`
2. Execute o pipeline completo (converter → chunking → indexar)
