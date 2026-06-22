# ── Tarefas — CRUD da lista de tarefas ─────────────────────────────────────────

from core.logging_config import get_logger
from database.operacoes import _conectar

logger = get_logger(__name__)

# Self-migration: garante a coluna mesmo em bancos criados antes desta feature
_conn = _conectar()
_colunas = [c[1] for c in _conn.execute("PRAGMA table_info(tarefas)").fetchall()]
if "evento_id" not in _colunas:
    _conn.execute("ALTER TABLE tarefas ADD COLUMN evento_id INTEGER REFERENCES eventos(id)")
    _conn.commit()
_conn.close()


def listar_tarefas(status: str = None) -> list[dict]:
    """Retorna lista de tarefas (com título/data do evento vinculado, se houver).
    status pode ser 'pendente', 'concluida' ou None (todas)."""
    conn = _conectar()
    cursor = conn.cursor()
    base_sql = """
        SELECT t.*, e.titulo AS evento_titulo, e.data_evento AS evento_data
        FROM tarefas t
        LEFT JOIN eventos e ON t.evento_id = e.id
    """
    if status:
        cursor.execute(
            base_sql + " WHERE t.status = ? ORDER BY t.prioridade DESC, t.data_criacao ASC",
            (status,)
        )
    else:
        cursor.execute(
            base_sql + " ORDER BY t.status ASC, t.prioridade DESC, t.data_criacao ASC"
        )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def adicionar_tarefa(
    titulo: str, descricao: str = None, prioridade: str = "normal", evento_id: int = None
) -> bool:
    """Adiciona uma tarefa, opcionalmente vinculada a um evento da agenda. Retorna True se sucesso."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tarefas (titulo, descricao, prioridade, evento_id) VALUES (?, ?, ?, ?)",
            (titulo, descricao, prioridade, evento_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error("Erro ao adicionar tarefa %r: %s", titulo, e)
        return False
    finally:
        conn.close()


def concluir_tarefa(tarefa_id: int) -> bool:
    """Marca uma tarefa como concluída. Retorna True se sucesso."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tarefas SET status = 'concluida', data_conclusao = datetime('now', 'localtime') WHERE id = ?",
            (tarefa_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error("Erro ao concluir tarefa %s: %s", tarefa_id, e)
        return False
    finally:
        conn.close()


def desconcluir_tarefa(tarefa_id: int) -> bool:
    """Volta uma tarefa concluída para pendente."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tarefas SET status = 'pendente', data_conclusao = NULL WHERE id = ?",
            (tarefa_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error("Erro ao reabrir tarefa %s: %s", tarefa_id, e)
        return False
    finally:
        conn.close()


def deletar_tarefa(tarefa_id: int) -> bool:
    """Remove uma tarefa do banco. Retorna True se sucesso."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error("Erro ao deletar tarefa %s: %s", tarefa_id, e)
        return False
    finally:
        conn.close()
