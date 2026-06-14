# Jarvis — Módulo do Agente

Agente de IA com interface web para consultar agenda acadêmica e conteúdos sobre Inteligência Artificial. O agente decide automaticamente se deve consultar o banco de dados (eventos, contatos) ou buscar nos documentos indexados.

## Estrutura

```
jarvis_academica/
├── agente/
│   ├── __init__.py
│   └── agente.py          # Loop ReAct: SQL para agenda, BUSCAR_DOCS para documentos
├── core/
│   ├── __init__.py
│   ├── constantes.py       # Tópicos de IA, sugestões e palavras-chave compartilhadas
│   └── logging_config.py   # Configuração do logger usado em todo o módulo
├── database/
│   ├── __init__.py
│   ├── operacoes.py        # Funções de acesso ao SQLite (tarefas, eventos, contatos)
│   ├── quiz_operacoes.py    # Registro e consulta de tentativas do quiz
│   ├── schema.sql           # Estrutura das tabelas e dados de exemplo
│   └── agenda_jarvis.db    # Banco gerado automaticamente na primeira execução
├── estudos/
│   ├── __init__.py
│   ├── planejador.py        # Monta o plano de estudos (usado por PLANO_ESTUDOS)
│   ├── quiz.py              # Gera perguntas e avalia respostas (active recall)
│   └── recomendacao.py      # Recomenda tópicos de revisão com base no histórico do quiz
├── rag/
│   ├── __init__.py
│   └── consulta.py          # Wrapper que conecta ao banco vetorial
├── avaliacao/                # Casos de teste para avaliação do agente
├── avaliar_sistema.py        # Script de avaliação automática do agente
└── requirements.txt          # Dependências específicas deste módulo
```

## Banco de Dados

O banco SQLite é criado automaticamente quando o app é iniciado pela primeira vez — não é necessário rodar nenhum script de setup.

A lista de tabelas e seus conteúdos está documentada em
[ARQUITETURA.md](../ARQUITETURA.md#banco-de-dados-relacional-sqlite).

Para resetar o banco, basta apagar o arquivo `database/agenda_jarvis.db` e reiniciar o app.

## Como o Agente Funciona

O agente usa um loop ReAct manual: recebe a pergunta, decide qual ferramenta usar, executa e formula a resposta. As ferramentas disponíveis são:

- **`[CONSULTAR_AGENDA]`** → próximos eventos da agenda
- **`[LISTAR_TAREFAS]`** → tarefas cadastradas (pendentes, concluídas ou todas)
- **`[ADICIONAR_TAREFA]`** → cria uma nova tarefa
- **`[CONCLUIR_TAREFA]`** → marca uma tarefa como concluída
- **`[BUSCAR_DOCS]`** → perguntas sobre IA, machine learning e os materiais indexados
- **`[PLANO_ESTUDOS]`** → monta um cronograma de estudos para a prova
- **`[PRIORIDADES_HOJE]`** → eventos de hoje e tarefas pendentes
- **SQL** → qualquer outra operação sobre agenda, tarefas, eventos e contatos

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
- Preencha título, descrição opcional e prioridade, depois clique em **Salvar tarefa**
- Filtre por **Pendentes**, **Concluídas** ou **Todas**
- Use os ícones em cada tarefa: **✔** para concluir, **↩** para reabrir, **🗑** para deletar

### Aba Quiz

- Veja as recomendações de revisão (tópicos nunca testados ou com nota média baixa)
- Escolha um tópico e a quantidade de perguntas, depois clique em **Gerar pergunta(s)**
- Responda no campo de texto e clique em **Responder** para receber nota (0-10) e feedback de cada pergunta
- Clique em **Próximas perguntas** para iniciar um novo lote
