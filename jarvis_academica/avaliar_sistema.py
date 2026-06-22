# ── Avaliação do sistema — RAG + agente completo (tool calling) — gera
# relatório com pergunta, documentos/ferramentas, resposta, verificação
# automática e espaço para classificação manual. Também gera a Análise de
# Erros, semeada com falhas reais encontradas em sessão de desenvolvimento. ──

from dotenv import load_dotenv
load_dotenv()

from agente.agente import rodar_agente
from avaliacao.casos_teste import CASOS_AGENTE, CASOS_RAG
from avaliacao.falhas import FALHAS, renderizar_analise_erros
from avaliacao.relatorio import (
    PLACEHOLDER,
    carregar_classificacoes_antigas,
    renderizar_caso_agente,
    renderizar_caso_rag,
)
from avaliacao.verificacao import verificar_caso
from database.agenda import deletar_evento, listar_eventos_proximos
from database.tarefas import deletar_tarefa, listar_tarefas
from rag.consulta import consultar_documentos

CAMINHO_RELATORIO = "resultados_avaliacao.md"


def executar_caso_rag(caso: dict) -> dict:
    try:
        resposta, chunks = consultar_documentos(caso["pergunta"])
        return {"resposta": resposta, "chunks": chunks, "passos": [], "erro": None}
    except Exception as e:
        return {"resposta": f"ERRO ao executar: {e}", "chunks": [], "passos": [], "erro": str(e)}


def _limpar_entidades_criadas(tarefas_antes: set, eventos_antes: set) -> None:
    for t in listar_tarefas():
        if t["id"] not in tarefas_antes:
            deletar_tarefa(t["id"])
    for e in listar_eventos_proximos(dias=3650):
        if e["id"] not in eventos_antes:
            deletar_evento(e["id"])


def executar_caso_agente(caso: dict) -> tuple:
    tarefas_antes = {t["id"] for t in listar_tarefas()}
    eventos_antes = {e["id"] for e in listar_eventos_proximos(dias=3650)}
    avisos = []
    try:
        resultado = rodar_agente(caso["pergunta"])
        resultado["erro"] = None
        avisos = verificar_caso(caso, resultado)
    except Exception as e:
        resultado = {"resposta": f"ERRO ao executar: {e}", "chunks": [], "passos": [], "erro": str(e)}
    finally:
        if caso.get("limpar_apos"):
            _limpar_entidades_criadas(tarefas_antes, eventos_antes)
    return resultado, avisos


def gerar_relatorio() -> None:
    classificacoes_antigas = carregar_classificacoes_antigas(CAMINHO_RELATORIO)
    blocos = ["# Avaliação do Sistema\n"]

    total = len(CASOS_RAG) + len(CASOS_AGENTE)
    numero = 1

    for caso in CASOS_RAG:
        print(f"[{numero}/{total}] (RAG) {caso['pergunta']}")
        resultado = executar_caso_rag(caso)
        antiga = classificacoes_antigas.get(caso["pergunta"])
        classificacao = antiga["classificacao"] if antiga else PLACEHOLDER
        justificativa = antiga["justificativa"] if antiga else None
        blocos.append(renderizar_caso_rag(numero, caso, resultado, classificacao, justificativa))
        numero += 1

    for caso in CASOS_AGENTE:
        print(f"[{numero}/{total}] (Agente) {caso['pergunta']}")
        resultado, avisos = executar_caso_agente(caso)
        antiga = classificacoes_antigas.get(caso["pergunta"])
        classificacao = antiga["classificacao"] if antiga else PLACEHOLDER
        justificativa = antiga["justificativa"] if antiga else None
        blocos.append(renderizar_caso_agente(numero, caso, resultado, avisos, classificacao, justificativa))
        numero += 1

    blocos.append(renderizar_analise_erros(FALHAS))

    with open(CAMINHO_RELATORIO, "w", encoding="utf-8") as f:
        f.write("\n".join(blocos))
    print(f"\nRelatório gerado em: {CAMINHO_RELATORIO}")


gerar_relatorio()
