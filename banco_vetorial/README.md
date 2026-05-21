# banco_vetorial

Módulo responsável pela indexação e consulta de documentos usando [ChromaDB](https://www.trychroma.com/). É a base do componente RAG do JARVIS Acadêmico.

## Estrutura

```
banco_vetorial/
├── docs/
│   └── documentos.txt  # Documentos a serem indexados (um por linha)
├── tests/
│   └── teste.ipynb     # Notebook para experimentos e validações
└── main.py             # Indexa os documentos e exibe uma amostra
```

## O que o main.py faz

1. Lê cada linha de `docs/documentos.txt` como um documento separado
2. Cria uma coleção no ChromaDB em memória
3. Adiciona os documentos com IDs únicos e metadados de posição
4. Exibe uma amostra da coleção com `collection.peek()`

## Como executar

A partir da raiz do projeto, com o ambiente virtual ativo:

```bash
cd banco_vetorial
python main.py
```

## Dependências

```bash
pip install chromadb
```

## Adicionando documentos

Edite o arquivo `docs/documentos.txt` e adicione um documento por linha. Cada linha será tratada como um chunk independente no banco vetorial.
