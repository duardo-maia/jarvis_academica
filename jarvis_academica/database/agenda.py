# ── Agenda — consulta de eventos ───────────────────────────────────────────────

from core.logging_config import get_logger
from database.operacoes import _conectar

logger = get_logger(__name__)


def listar_eventos_proximos(dias: int = 7) -> list[dict]:
    """Retorna eventos entre hoje e hoje + dias, ordenados por data/hora."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT * FROM eventos
            WHERE data_evento BETWEEN date('now', 'localtime') AND date('now', 'localtime', ?)
            ORDER BY data_evento ASC, hora_inicio ASC
            """,
            (f"+{dias} days",)
        )
        return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        logger.error("Erro ao listar eventos próximos: %s", e)
        return []
    finally:
        conn.close()


def adicionar_evento(
    titulo: str,
    data_evento: str,
    hora_inicio: str,
    descricao: str = None,
    hora_fim: str = None,
    local: str = None,
    contato_id: int = None,
) -> bool:
    """Adiciona um evento à agenda. Retorna True se sucesso.

    hora_inicio é obrigatório por regra de negócio (mesmo sendo nullable no
    schema) — garante que a regra não seja contornada por nenhum chamador.
    """
    if not hora_inicio:
        logger.error("Erro ao adicionar evento %r: hora_inicio é obrigatório", titulo)
        return False
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO eventos (titulo, descricao, data_evento, hora_inicio, hora_fim, local, contato_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (titulo, descricao, data_evento, hora_inicio, hora_fim, local, contato_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error("Erro ao adicionar evento %r: %s", titulo, e)
        return False
    finally:
        conn.close()


def deletar_evento(evento_id: int) -> bool:
    """Remove um evento do banco. Retorna True se sucesso."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error("Erro ao deletar evento %s: %s", evento_id, e)
        return False
    finally:
        conn.close()
