import os
import sqlite3
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Modelo ────────────────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("GEMMA_KEY"),
    base_url="https://llm.liaufms.org/v1/gemma-3-12b-it",
)
gemma_model = "google/gemma-3-12b-it"

# ── Banco de dados ────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent.parent / "banco" / "agenda_jarvis.db"


def executar_sql(sql: str) -> str:
    """Executa qualquer SQL e retorna o resultado como texto."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        resultado = ""
        for stmt in statements:
            cursor.execute(stmt)
            tipo = stmt.strip().upper().split()[0]
            if tipo == "SELECT":
                rows = cursor.fetchall()
                if not rows:
                    resultado += "Nenhum registro encontrado.\n"
                else:
                    cols = rows[0].keys()
                    resultado += " | ".join(cols) + "\n"
                    resultado += "-" * 60 + "\n"
                    for row in rows:
                        resultado += " | ".join(str(v) if v is not None else "" for v in row) + "\n"
            else:
                conn.commit()
                resultado += f"Operação executada com sucesso. Linhas afetadas: {cursor.rowcount}\n"
        return resultado.strip()
    except Exception as e:
        return f"ERRO: {e}"
    finally:
        conn.close()


def get_schema() -> str:
    """Retorna o esquema do banco para o modelo entender a estrutura."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    schema = ""
    for name, ddl in tables:
        schema += f"\n-- Tabela: {name}\n{ddl}\n"
    return schema


# ── Funções diretas para tarefas (usadas pelo app.py) ────────────────────────

def listar_tarefas(status: str = None) -> list[dict]:
    """Retorna lista de tarefas como dicts. status pode ser 'pendente', 'concluida' ou None (todas)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if status:
        cursor.execute(
            "SELECT * FROM tarefas WHERE status = ? ORDER BY prioridade DESC, data_criacao ASC",
            (status,)
        )
    else:
        cursor.execute(
            "SELECT * FROM tarefas ORDER BY status ASC, prioridade DESC, data_criacao ASC"
        )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def adicionar_tarefa(titulo: str, descricao: str = None, prioridade: str = "normal") -> bool:
    """Adiciona uma tarefa diretamente. Retorna True se sucesso."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tarefas (titulo, descricao, prioridade) VALUES (?, ?, ?)",
            (titulo, descricao, prioridade)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def concluir_tarefa(tarefa_id: int) -> bool:
    """Marca uma tarefa como concluída. Retorna True se sucesso."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tarefas SET status = 'concluida', data_conclusao = datetime('now', 'localtime') WHERE id = ?",
            (tarefa_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()


def desconcluir_tarefa(tarefa_id: int) -> bool:
    """Volta uma tarefa concluída para pendente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tarefas SET status = 'pendente', data_conclusao = NULL WHERE id = ?",
            (tarefa_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()


def deletar_tarefa(tarefa_id: int) -> bool:
    """Remove uma tarefa do banco. Retorna True se sucesso."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()


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
        {"role": "system",    "content": SYSTEM},
        {"role": "user",      "content": pergunta},
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


# ── Interface de chat no terminal ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Jarvis - Assistente de Agenda  ")
    print("  Digite 'sair' para encerrar    ")
    print("=" * 60)

    while True:
        try:
            pergunta = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando...")
            break

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Até logo!")
            break

        if not pergunta:
            continue

        print("\nJarvis: ", end="", flush=True)
        resposta = rodar_agente(pergunta)
        print(resposta)


if __name__ == "__main__":
    main()