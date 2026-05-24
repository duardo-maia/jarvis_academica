# ── Agente de IA — loop ReAct com acesso ao banco via SQL ─────────────────────

import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from database.operacoes import executar_sql, get_schema

load_dotenv()

# ── Modelo ────────────────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("GEMMA_KEY"),
    base_url="https://llm.liaufms.org/v1/gemma-3-12b-it",
)
gemma_model = "google/gemma-3-12b-it"

# ── System prompt ─────────────────────────────────────────────────────────────
SCHEMA = get_schema()

SYSTEM = f"""Você é o Jarvis, um assistente de agenda pessoal inteligente. Você pode consultar o dia e horário atual.
Você tem acesso a um banco de dados SQLite com as seguintes tabelas:

{SCHEMA}

TABELA DE TAREFAS — regras específicas:
- Para ADICIONAR uma tarefa: INSERT INTO tarefas (titulo, descricao, prioridade) VALUES (...)
  * prioridade deve ser: 'baixa', 'normal' ou 'alta'
- Para LISTAR tarefas pendentes: SELECT * FROM tarefas WHERE status = 'pendente' ORDER BY prioridade DESC
- Para LISTAR todas as tarefas: SELECT * FROM tarefas ORDER BY status, prioridade DESC
- Para MARCAR como concluída: UPDATE tarefas SET status = 'concluida', data_conclusao = datetime('now','localtime') WHERE id = <id>
- Para REMOVER uma tarefa: DELETE FROM tarefas WHERE id = <id>

Para responder ao usuário, você pode executar comandos SQL usando o seguinte formato EXATO:

```sql
SEU COMANDO SQL AQUI
```

Regras gerais:
- Após receber o resultado do SQL, formule uma resposta clara e amigável em português brasileiro
- Para criar eventos com contato, primeiro verifique se o contato existe com SELECT
- Datas no formato YYYY-MM-DD, horários no formato HH:MM
- Quando a tarefa estiver concluída e você tiver a resposta final, escreva: RESPOSTA FINAL: <sua resposta>
- Não invente dados. Se não encontrar, diga que não encontrou.
- Ao listar tarefas, mostre o id, título, prioridade e status de forma organizada
"""


# ── Loop ReAct manual ─────────────────────────────────────────────────────────
def rodar_agente(pergunta: str, max_passos: int = 8) -> str:
    mensagens = [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": pergunta},
    ]

    for passo in range(max_passos):
        resposta = client.chat.completions.create(
            model=gemma_model,
            messages=mensagens,
            temperature=0,
        )
        conteudo = resposta.choices[0].message.content
        mensagens.append({"role": "assistant", "content": conteudo})

        if "RESPOSTA FINAL:" in conteudo:
            idx = conteudo.index("RESPOSTA FINAL:")
            return conteudo[idx + len("RESPOSTA FINAL:"):].strip()

        match = re.search(r"```sql\s*(.*?)```", conteudo, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()
            print(f"\n[Jarvis executando SQL]\n{sql}\n")
            resultado = executar_sql(sql)
            print(f"[Resultado]\n{resultado}\n")
            mensagens.append({"role": "user", "content": f"Resultado do SQL:\n{resultado}"})
        else:
            return conteudo.strip()

    return "Não consegui concluir a tarefa dentro do número máximo de passos."
