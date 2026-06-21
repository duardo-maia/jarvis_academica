# ── Tarefas — CRUD da lista de tarefas ─────────────────────────────────────────

from core.logging_config import get_logger
from database.operacoes import _conectar

logger = get_logger(__name__)


def listar_tarefas(status: str = None) -> list[dict]:
    """Retorna lista de tarefas. status pode ser 'pendente', 'concluida' ou None (todas)."""
    conn = _conectar()
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
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tarefas (titulo, descricao, prioridade) VALUES (?, ?, ?)",
            (titulo, descricao, prioridade)
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
