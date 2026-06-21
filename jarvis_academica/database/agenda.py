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
