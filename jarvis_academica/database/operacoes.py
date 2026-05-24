# ── Funções de acesso ao banco de dados ───────────────────────────────────────

import sqlite3
from pathlib import Path

DB_PATH     = Path(__file__).parent / "agenda_jarvis.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# Cria o banco automaticamente se ainda não existir
if not DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()
    print("Banco criado com sucesso!")


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


def listar_tarefas(status: str = None) -> list[dict]:
    """Retorna lista de tarefas. status pode ser 'pendente', 'concluida' ou None (todas)."""
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
    """Adiciona uma tarefa. Retorna True se sucesso."""
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
