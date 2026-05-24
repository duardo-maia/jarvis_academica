# Jarvis Acadêmica

Assistente de agenda inteligente com interface web. Permite conversar com um agente de IA para gerenciar eventos, contatos, lembretes e tarefas acadêmicas, com visualização e gerenciamento direto pela interface.

## Funcionalidades

- **Chat com Jarvis** — converse em linguagem natural para criar eventos, consultar agenda, gerenciar contatos e tarefas
- **Lista de Tarefas** — adicione, conclua e delete tarefas com prioridade (alta, normal, baixa) diretamente pela interface
- **Banco de dados local** — tudo salvo em SQLite, sem necessidade de servidor externo

## Estrutura do projeto

```
JarvisAcademica/
├── app.py                    # Interface web (Streamlit)
├── agent_tarefas_agenda.py   # Agente de IA + funções do banco
├── criar_agenda.py           # Script para criar o banco de dados
├── agenda.sql                # Estrutura das tabelas e dados de exemplo
├── agenda_jarvis.db          # Banco de dados (gerado pelo criar_agenda.py)
└── requirements.txt          # Dependências
```

## Pré-requisitos

- Python 3.10 ou superior
- Chave de acesso à API Gemma (`GEMMA_KEY`)

## Instalação

**1. Crie o ambiente virtual e instale as dependências:**

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# ou
.venv\Scripts\activate           # Windows

pip install streamlit langchain langchain-openai python-dotenv
```

**2. Crie o arquivo `.env` na raiz do projeto com a chave da API:**

```
GEMMA_KEY=sua_chave_aqui
```

**3. Crie o banco de dados:**

```bash
python criar_agenda.py
```

Esse comando cria as tabelas de contatos, eventos, lembretes e tarefas, e insere alguns dados de exemplo.

## Executando

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

## Como usar

### Aba Chat

Digite perguntas ou comandos em linguagem natural. Exemplos:

- `Quais são minhas tarefas pendentes?`
- `Adiciona a tarefa Estudar Álgebra com prioridade alta`
- `Quais eventos tenho essa semana?`
- `Cria um evento Reunião de Projeto no dia 10/06 às 14h`

### Aba Lista de Tarefas

- Clique em **Adicionar nova tarefa** para criar uma tarefa com título, descrição e prioridade
- Use os filtros para ver tarefas **Pendentes**, **Concluídas** ou **Todas**
- Clique em **Concluir** ou **Deletar** em cada tarefa

## Banco de dados

As tabelas criadas pelo `agenda.sql` são:

| Tabela | Descrição |
|---|---|
| `contatos` | Nome, telefone, e-mail e observações |
| `eventos` | Título, data, horário, local e contato vinculado |
| `lembretes` | Alertas associados a eventos |
| `tarefas` | Título, descrição, prioridade e status |
