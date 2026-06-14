# ── Ferramentas do agente — dispatch das ações disponíveis ao loop ReAct ──────

import re

from core.logging_config import get_logger
from database.operacoes import (
    adicionar_tarefa,
    concluir_tarefa,
    executar_sql,
    listar_eventos_proximos,
    listar_tarefas,
)
from estudos.planejador import montar_plano_estudos, montar_prioridades_hoje
from rag.consulta import consultar_documentos

logger = get_logger(__name__)


def _log_chamada(nome: str, entrada, saida) -> None:
    """Registra de forma padronizada qual ferramenta foi chamada, com sua entrada e saída."""
    logger.info("ferramenta=%s | entrada=%s | saida=%s", nome, entrada, saida)


def executar_ferramenta(conteudo: str):
    """
    Detecta e executa a ferramenta pedida pelo modelo no texto `conteudo`.
    Retorna (texto_resultado, chunks) para ser anexado à conversa, ou None se
    nenhuma ferramenta foi reconhecida.
    """
    match_sql = re.search(r"```sql\s*(.*?)```", conteudo, re.DOTALL | re.IGNORECASE)
    match_docs = re.search(r"\[BUSCAR_DOCS:\s*(.*?)\]", conteudo, re.DOTALL)
    match_plano = re.search(r"\[PLANO_ESTUDOS\]", conteudo)
    match_prioridades = re.search(r"\[PRIORIDADES_HOJE\]", conteudo)
    match_agenda = re.search(r"\[CONSULTAR_AGENDA(?::\s*(.*?))?\]", conteudo)
    match_listar_tarefas = re.search(r"\[LISTAR_TAREFAS(?::\s*(.*?))?\]", conteudo)
    match_add_tarefa = re.search(r"\[ADICIONAR_TAREFA:\s*(.*?)\]", conteudo, re.DOTALL)
    match_concluir_tarefa = re.search(r"\[CONCLUIR_TAREFA:\s*(.*?)\]", conteudo)

    if match_sql:
        sql = match_sql.group(1).strip()
        resultado = executar_sql(sql)
        _log_chamada("SQL", sql, resultado)
        return f"Resultado do SQL:\n{resultado}", []

    if match_docs:
        consulta = match_docs.group(1).strip()
        resultado_texto, chunks = consultar_documentos(consulta)
        _log_chamada("BUSCAR_DOCS", consulta, resultado_texto)
        return f"Resultado da busca nos documentos:\n{resultado_texto}", chunks

    if match_plano:
        resultado = montar_plano_estudos()
        _log_chamada("PLANO_ESTUDOS", None, resultado)
        return f"Dados para o plano de estudos:\n{resultado}", []

    if match_prioridades:
        resultado = montar_prioridades_hoje()
        _log_chamada("PRIORIDADES_HOJE", None, resultado)
        return f"Dados para as prioridades de hoje:\n{resultado}", []

    if match_agenda:
        bruto = (match_agenda.group(1) or "").strip()
        dias = int(bruto) if bruto.isdigit() else 7
        eventos = listar_eventos_proximos(dias)
        _log_chamada("CONSULTAR_AGENDA", {"dias": dias}, eventos)
        return f"Eventos da agenda (próximos {dias} dias):\n{eventos}", []

    if match_listar_tarefas:
        status = (match_listar_tarefas.group(1) or "").strip() or None
        tarefas = listar_tarefas(status)
        _log_chamada("LISTAR_TAREFAS", {"status": status}, tarefas)
        return f"Tarefas (status={status or 'todas'}):\n{tarefas}", []

    if match_add_tarefa:
        partes = [p.strip() for p in match_add_tarefa.group(1).split("|")]
        titulo = partes[0]
        descricao = partes[1] if len(partes) > 1 and partes[1] else None
        prioridade = partes[2] if len(partes) > 2 and partes[2] else "normal"
        sucesso = adicionar_tarefa(titulo, descricao, prioridade)
        entrada = {"titulo": titulo, "descricao": descricao, "prioridade": prioridade}
        _log_chamada("ADICIONAR_TAREFA", entrada, sucesso)
        if sucesso:
            return f"Tarefa '{titulo}' adicionada com sucesso (prioridade: {prioridade}).", []
        return f"Falha ao adicionar a tarefa '{titulo}'.", []

    if match_concluir_tarefa:
        bruto = match_concluir_tarefa.group(1).strip()
        try:
            tarefa_id = int(bruto)
        except ValueError:
            _log_chamada("CONCLUIR_TAREFA", bruto, "ERRO: id inválido")
            return f"ERRO: id de tarefa inválido: {bruto!r}", []
        sucesso = concluir_tarefa(tarefa_id)
        _log_chamada("CONCLUIR_TAREFA", {"id": tarefa_id}, sucesso)
        if sucesso:
            return f"Tarefa {tarefa_id} marcada como concluída.", []
        return f"Não encontrei nenhuma tarefa com id {tarefa_id}.", []

    return None
