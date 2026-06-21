# ── Quiz — histórico de tentativas (active recall) ─────────────────────────────

from core.logging_config import get_logger
from database.operacoes import _conectar

logger = get_logger(__name__)

# Self-migration: garante a tabela mesmo em bancos criados antes desta feature
_conn = _conectar()
_conn.execute("""
    CREATE TABLE IF NOT EXISTS historico_quiz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topico TEXT NOT NULL,
        nota INTEGER NOT NULL CHECK(nota BETWEEN 0 AND 10),
        data_tentativa DATETIME DEFAULT (datetime('now', 'localtime'))
    )
""")
_conn.commit()
_conn.close()


def registrar_tentativa(topico: str, nota: int) -> bool:
    """Registra uma tentativa de quiz (tópico + nota de 0 a 10). Retorna True se sucesso."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO historico_quiz (topico, nota) VALUES (?, ?)",
            (topico, nota)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error("Erro ao registrar tentativa de quiz (%r, %s): %s", topico, nota, e)
        return False
    finally:
        conn.close()


def listar_historico(topico: str = None) -> list[dict]:
    """Retorna o histórico de tentativas do quiz, opcionalmente filtrado por tópico."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        if topico:
            cursor.execute(
                "SELECT * FROM historico_quiz WHERE topico = ? ORDER BY data_tentativa DESC",
                (topico,)
            )
        else:
            cursor.execute("SELECT * FROM historico_quiz ORDER BY data_tentativa DESC")
        return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        logger.error("Erro ao listar histórico de quiz: %s", e)
        return []
    finally:
        conn.close()


def media_por_topico() -> dict:
    """Retorna a média das notas por tópico, com base no histórico de tentativas."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT topico, AVG(nota) FROM historico_quiz GROUP BY topico")
        return {topico: media for topico, media in cursor.fetchall()}
    except Exception as e:
        logger.error("Erro ao calcular média por tópico: %s", e)
        return {}
    finally:
        conn.close()


def topicos_nao_revisados(topicos_disponiveis: list[str]) -> list[str]:
    """Retorna os tópicos disponíveis que ainda não têm nenhuma tentativa registrada."""
    revisados = set(media_por_topico().keys())
    return [t for t in topicos_disponiveis if t not in revisados]
