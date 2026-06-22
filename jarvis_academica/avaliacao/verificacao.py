# ── Verificação automática determinística — sinaliza possíveis alucinações ────
# sem substituir a classificação manual (correta/parcialmente correta/incorreta).

import re

from core.constantes import TOPICOS_IA
from database.agenda import listar_eventos_proximos
from database.tarefas import listar_tarefas


def detectar_conflito_de_escopo(pergunta: str, resposta: str) -> list[str]:
    """Verifica se a resposta menciona tópicos de TOPICOS_IA como se fossem
    conteúdo relevante para um assunto da pergunta que não está nessa lista."""
    pergunta_lower = pergunta.lower()
    assunto_esta_na_lista = any(
        topico.lower() in pergunta_lower or any(p in pergunta_lower for p in palavras)
        for topico, palavras in TOPICOS_IA.items()
    )
    if assunto_esta_na_lista:
        return []

    resposta_lower = resposta.lower()
    topicos_citados = [
        topico for topico, palavras in TOPICOS_IA.items()
        if any(p in resposta_lower for p in palavras)
    ]
    if topicos_citados:
        return [
            f"Resposta cita tópico(s) de IA ({', '.join(topicos_citados)}) não "
            "relacionados ao assunto da pergunta, que não está na lista fechada."
        ]
    return []


def detectar_entidades_fabricadas(resposta: str) -> list[str]:
    """Cruza ids (#N / ID: N) e datas (YYYY-MM-DD) citados na resposta contra
    os dados reais de tarefas/eventos no momento da execução."""
    avisos = []

    ids_citados = {int(m) for m in re.findall(r"(?:#|ID:\s*)(\d+)", resposta)}
    if ids_citados:
        ids_reais = {t["id"] for t in listar_tarefas()} | {
            e["id"] for e in listar_eventos_proximos(dias=3650)
        }
        for id_citado in sorted(ids_citados - ids_reais):
            avisos.append(f"ID #{id_citado} citado na resposta não corresponde a nenhuma tarefa/evento real.")

    datas_citadas = set(re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", resposta))
    if datas_citadas and re.search(r"\b(prova|evento|compromisso)\b", resposta, re.IGNORECASE):
        datas_reais = {e["data_evento"] for e in listar_eventos_proximos(dias=3650)}
        for data_citada in sorted(datas_citadas - datas_reais):
            avisos.append(f"Data {data_citada} citada na resposta não corresponde a nenhum evento real.")

    return avisos


def verificar_caso(caso: dict, resultado: dict) -> list[str]:
    """Roda os checks aplicáveis e retorna lista de avisos (vazia = nada suspeito)."""
    if caso["tipo"] != "agente":
        return []
    avisos = []
    avisos += detectar_conflito_de_escopo(caso["pergunta"], resultado["resposta"])
    avisos += detectar_entidades_fabricadas(resultado["resposta"])
    return avisos
