# ── Recomendação de Revisão — identifica tópicos a revisar com base no quiz ──

from core.logging_config import get_logger
from database.quiz_operacoes import media_por_topico, topicos_nao_revisados

logger = get_logger(__name__)

NOTA_MINIMA = 6


def recomendar_revisao(topicos_disponiveis: list[str]) -> list[dict]:
    """
    Retorna os tópicos recomendados para revisão: primeiro os tópicos que o
    usuário nunca fez quiz, depois os tópicos com média de nota baixa.
    """
    recomendacoes = []

    for topico in topicos_nao_revisados(topicos_disponiveis):
        recomendacoes.append({"topico": topico, "motivo": "nunca revisado"})

    medias = media_por_topico()
    for topico in topicos_disponiveis:
        media = medias.get(topico)
        if media is not None and media < NOTA_MINIMA:
            recomendacoes.append({"topico": topico, "motivo": f"nota baixa ({media:.1f}/10)"})

    logger.info("Recomendação de revisão: %s", [r["topico"] for r in recomendacoes])
    return recomendacoes
