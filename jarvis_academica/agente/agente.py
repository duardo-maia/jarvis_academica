# ── Agente de IA — loop ReAct com acesso ao banco via SQL ─────────────────────

import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from database.operacoes import executar_sql, get_schema
from rag.consulta import consultar_documentos

load_dotenv()

# ── Modelo ────────────────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("GEMMA_KEY"),
    base_url="https://llm.liaufms.org/v1/gemma-3-12b-it",
)
gemma_model = "google/gemma-3-12b-it"

# ── System prompt ─────────────────────────────────────────────────────────────
SCHEMA = get_schema()

SYSTEM = f"""Você é o Jarvis, um assistente acadêmico inteligente. Você tem acesso a dois recursos:

1. BANCO DE DADOS (agenda): tarefas, eventos, contatos e lembretes — use SQL.
2. DOCUMENTOS ACADÊMICOS: PDFs sobre IA indexados em banco vetorial — use BUSCAR_DOCS.

Use SQL para perguntas sobre agenda, tarefas, eventos e contatos.
Use BUSCAR_DOCS para perguntas sobre conceitos e teoria (embeddings, RAG, LLMs, aprendizado de máquina, etc.).

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
- IMPORTANTE: na RESPOSTA FINAL, inclua TODOS os dados relevantes diretamente no texto. O usuário só vê a RESPOSTA FINAL — nunca use expressões como "listadas acima", "conforme mostrado", "como pode ver", pois o usuário não vê os resultados SQL.
- Não invente dados. Se não encontrar, diga que não encontrou.
- Ao listar tarefas, mostre o id, título, prioridade e status de forma organizada diretamente na resposta

Para buscar nos documentos acadêmicos, use EXATAMENTE este formato:
[BUSCAR_DOCS: sua pergunta aqui]
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

        match_sql = re.search(r"```sql\s*(.*?)```", conteudo, re.DOTALL | re.IGNORECASE)
        match_docs = re.search(r"\[BUSCAR_DOCS:\s*(.*?)\]", conteudo, re.DOTALL)

        if match_sql:
            sql = match_sql.group(1).strip()
            print(f"\n[Jarvis executando SQL]\n{sql}\n")
            resultado = executar_sql(sql)
            print(f"[Resultado]\n{resultado}\n")
            mensagens.append({"role": "user", "content": f"Resultado do SQL:\n{resultado}"})
        elif match_docs:
            consulta = match_docs.group(1).strip()
            print(f"\n[Jarvis buscando documentos]\n{consulta}\n")
            resultado = consultar_documentos(consulta)
            print(f"[Resultado]\n{resultado}\n")
            mensagens.append({"role": "user", "content": f"Resultado da busca nos documentos:\n{resultado}"})
        else:
            return conteudo.strip()

    return "Não consegui concluir a tarefa dentro do número máximo de passos."
