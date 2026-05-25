# Jarvis — Módulo do Agente

Agente de IA com interface web para consultar agenda acadêmica e conteúdos sobre Inteligência Artificial. O agente decide automaticamente se deve consultar o banco de dados (eventos, contatos) ou buscar nos documentos indexados.

## Estrutura

```
jarvis_academica/
├── agente/
│   ├── __init__.py
│   └── agente.py        # Loop ReAct: SQL para agenda, BUSCAR_DOCS para documentos
├── database/
│   ├── __init__.py
│   ├── operacoes.py     # Funções de acesso ao SQLite
│   ├── schema.sql       # Estrutura das tabelas e dados de exemplo
│   └── agenda_jarvis.db # Banco gerado automaticamente na primeira execução
└── rag/
    ├── __init__.py
    └── consulta.py      # Wrapper que conecta ao banco vetorial
```

## Banco de Dados

O banco SQLite é criado automaticamente quando o app é iniciado pela primeira vez — não é necessário rodar nenhum script de setup.

As tabelas disponíveis são:

| Tabela | Conteúdo |
|---|---|
| `tarefas` | Título, descrição, prioridade e status |
| `eventos` | Título, data, horário, local e contato vinculado |
| `contatos` | Nome, telefone, e-mail e observações |
| `lembretes` | Alertas associados a eventos |

Para resetar o banco, basta apagar o arquivo `database/agenda_jarvis.db` e reiniciar o app.

## Como o Agente Funciona

O agente usa um loop ReAct manual: recebe a pergunta, decide qual ferramenta usar, executa e formula a resposta.

- **SQL** → consultas de agenda, eventos e contatos
- **`[BUSCAR_DOCS]`** → perguntas sobre IA, machine learning e os materiais indexados

## Como Usar

### Aba Chat

Use o chat para consultar sua agenda ou tirar dúvidas sobre os conteúdos de IA indexados.

**Agenda:**
- `Quais eventos tenho essa semana?`
- `Cria um evento Reunião de Projeto no dia 10/06 às 14h`
- `Quais são meus contatos?`

**Conteúdos de IA:**
- `O que é um embedding?`
- `Explica como funciona o RAG`
- `Qual a diferença entre LLM e um modelo de linguagem tradicional?`
- `Me explica como funciona um transformer`

### Aba Lista de Tarefas

- Clique em **➕ Adicionar nova tarefa** para abrir o formulário (clique novamente para fechar)
- Preencha título, descrição opcional e prioridade, depois clique em **✅ Salvar tarefa**
- Filtre por **Pendentes**, **Concluídas** ou **Todas**
- Use os ícones em cada tarefa: **✔** para concluir, **↩** para reabrir, **🗑** para deletar
