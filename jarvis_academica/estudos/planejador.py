# ── Plano de Estudos — combina agenda, tarefas e tópicos de IA ────────────────

from datetime import date

from core.constantes import TOPICOS_IA
from core.logging_config import get_logger
from database.agenda import listar_eventos_proximos
from database.tarefas import listar_tarefas
from estudos.recomendacao import recomendar_revisao

logger = get_logger(__name__)


def detectar_topicos(eventos: list[dict], tarefas: list[dict]) -> list[str]:
    """Detecta quais tópicos de IA (TOPICOS_IA) aparecem em eventos/tarefas, por palavra-chave."""
    texto = ""
    for item in eventos + tarefas:
        texto += " " + item.get("titulo", "")
        if item.get("descricao"):
            texto += " " + item["descricao"]
    texto = texto.lower()

    topicos_encontrados = []
    for topico, palavras_chave in TOPICOS_IA.items():
        for palavra in palavras_chave:
            if palavra in texto:
                topicos_encontrados.append(topico)
                break

    return topicos_encontrados


def montar_plano_estudos(dias: int = 7) -> str:
    """Monta um resumo textual com eventos próximos, tarefas pendentes e tópicos de
    estudo relacionados, para o agente usar na resposta final ao usuário."""
    eventos = listar_eventos_proximos(dias)
    tarefas = listar_tarefas("pendente")
    topicos = detectar_topicos(eventos, tarefas)

    logger.info(
        "Plano de estudos: %d evento(s), %d tarefa(s) pendente(s), tópicos detectados: %s",
        len(eventos), len(tarefas), topicos,
    )

    partes = []

    if eventos:
        linhas = []
        for e in eventos:
            linha = f"- {e['titulo']} em {e['data_evento']}"
            if e["hora_inicio"]:
                linha += f" às {e['hora_inicio']}"
            if e["local"]:
                linha += f" ({e['local']})"
            linhas.append(linha)
        partes.append(f"PRÓXIMOS EVENTOS (próximos {dias} dias):\n" + "\n".join(linhas))

        mais_proximo = min(eventos, key=lambda e: e["data_evento"])
        dias_restantes = (date.fromisoformat(mais_proximo["data_evento"]) - date.today()).days
        partes.append(
            f'DIAS RESTANTES até "{mais_proximo["titulo"]}": {dias_restantes} '
            "(0 = hoje, negativo = já passou)"
        )
    else:
        partes.append(f"Nenhum evento nos próximos {dias} dias.")

    if tarefas:
        linhas = []
        for t in tarefas:
            linha = f"- [{t['prioridade']}] {t['titulo']}"
            if t["descricao"]:
                linha += f": {t['descricao']}"
            linhas.append(linha)
        partes.append("TAREFAS PENDENTES (ordenadas por prioridade):\n" + "\n".join(linhas))
    else:
        partes.append("Nenhuma tarefa pendente.")

    if topicos:
        linhas = []
        for topico in topicos:
            linhas.append(f"- {topico}")
        partes.append("TÓPICOS DE ESTUDO RELACIONADOS (disponíveis nos materiais indexados):\n" + "\n".join(linhas))
    else:
        partes.append("Nenhum tópico de IA identificado diretamente nos eventos/tarefas atuais.")

    partes.append(
        "LISTA FECHADA DE TÓPICOS COM MATERIAL DISPONÍVEL NO SISTEMA (RAG): "
        + ", ".join(TOPICOS_IA.keys())
        + ". O sistema NÃO tem material indexado sobre nenhum outro assunto além desta lista."
    )

    recomendacoes = recomendar_revisao(list(TOPICOS_IA.keys()))
    if recomendacoes:
        linhas = []
        for r in recomendacoes:
            linhas.append(f"- {r['topico']} ({r['motivo']})")
        partes.append("TÓPICOS RECOMENDADOS PARA REVISÃO (com base no histórico do quiz):\n" + "\n".join(linhas))

    return "\n\n".join(partes)


def montar_prioridades_hoje() -> str:
    """Monta um resumo textual com os eventos de hoje e as tarefas pendentes,
    para o agente responder "o que devo priorizar hoje?"."""
    eventos = listar_eventos_proximos(0)
    tarefas = listar_tarefas("pendente")

    logger.info(
        "Prioridades de hoje: %d evento(s) hoje, %d tarefa(s) pendente(s)",
        len(eventos), len(tarefas),
    )

    partes = []

    if eventos:
        linhas = []
        for e in eventos:
            linha = f"- {e['titulo']} em {e['data_evento']}"
            if e["hora_inicio"]:
                linha += f" às {e['hora_inicio']}"
            if e["local"]:
                linha += f" ({e['local']})"
            linhas.append(linha)
        partes.append("EVENTOS DE HOJE:\n" + "\n".join(linhas))
    else:
        partes.append("Nenhum evento hoje.")

    if tarefas:
        linhas = []
        for t in tarefas:
            linha = f"- [{t['prioridade']}] {t['titulo']}"
            if t["descricao"]:
                linha += f": {t['descricao']}"
            linhas.append(linha)
        partes.append("TAREFAS PENDENTES (ordenadas por prioridade):\n" + "\n".join(linhas))
    else:
        partes.append("Nenhuma tarefa pendente.")

    return "\n\n".join(partes)
