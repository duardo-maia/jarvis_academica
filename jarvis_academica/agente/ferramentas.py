# ── Ferramentas do agente — dispatch das ações disponíveis ao loop ReAct ──────

import re

from core.logging_config import get_logger
from database.agenda import adicionar_evento, deletar_evento, listar_eventos_proximos
from database.operacoes import executar_sql
from database.tarefas import adicionar_tarefa, concluir_tarefa, listar_tarefas
from estudos.planejador import montar_plano_estudos, montar_prioridades_hoje
from rag.consulta import consultar_documentos

logger = get_logger(__name__)


def _log_chamada(nome: str, entrada, saida) -> None:
    """Registra de forma padronizada qual ferramenta foi chamada, com sua entrada e saída."""
    logger.info("ferramenta=%s | entrada=%s | saida=%s", nome, entrada, saida)


def _tratar_sql(match: re.Match):
    sql = match.group(1).strip()
    resultado = executar_sql(sql)
    _log_chamada("SQL", sql, resultado)
    passo = {"ferramenta": "SQL", "entrada": sql, "saida": resultado}
    return f"Resultado do SQL:\n{resultado}", [], passo


def _tratar_buscar_docs(match: re.Match):
    consulta = match.group(1).strip()
    resultado_texto, chunks = consultar_documentos(consulta)
    _log_chamada("BUSCAR_DOCS", consulta, resultado_texto)
    passo = {"ferramenta": "BUSCAR_DOCS", "entrada": consulta, "saida": resultado_texto}
    return f"Resultado da busca nos documentos:\n{resultado_texto}", chunks, passo


def _tratar_plano_estudos(match: re.Match):
    resultado = montar_plano_estudos()
    _log_chamada("PLANO_ESTUDOS", None, resultado)
    passo = {"ferramenta": "PLANO_ESTUDOS", "entrada": None, "saida": resultado}
    return f"Dados para o plano de estudos:\n{resultado}", [], passo


def _tratar_prioridades_hoje(match: re.Match):
    resultado = montar_prioridades_hoje()
    _log_chamada("PRIORIDADES_HOJE", None, resultado)
    passo = {"ferramenta": "PRIORIDADES_HOJE", "entrada": None, "saida": resultado}
    return f"Dados para as prioridades de hoje:\n{resultado}", [], passo


def _tratar_consultar_agenda(match: re.Match):
    bruto = (match.group(1) or "").strip()
    dias = int(bruto) if bruto.isdigit() else 7
    eventos = listar_eventos_proximos(dias)
    _log_chamada("CONSULTAR_AGENDA", {"dias": dias}, eventos)
    passo = {"ferramenta": "CONSULTAR_AGENDA", "entrada": {"dias": dias}, "saida": eventos}
    return f"Eventos da agenda (próximos {dias} dias):\n{eventos}", [], passo


def _tratar_adicionar_evento(match: re.Match):
    partes = [p.strip() for p in match.group(1).split("|")]
    titulo = partes[0]
    data_evento = partes[1] if len(partes) > 1 and partes[1] else None
    hora_inicio = partes[2] if len(partes) > 2 and partes[2] else None
    descricao = partes[3] if len(partes) > 3 and partes[3] else None
    hora_fim = partes[4] if len(partes) > 4 and partes[4] else None
    local = partes[5] if len(partes) > 5 and partes[5] else None
    sucesso = adicionar_evento(titulo, data_evento, hora_inicio, descricao, hora_fim, local)
    entrada = {
        "titulo": titulo, "data_evento": data_evento, "hora_inicio": hora_inicio,
        "descricao": descricao, "hora_fim": hora_fim, "local": local,
    }
    _log_chamada("ADICIONAR_EVENTO", entrada, sucesso)
    passo = {"ferramenta": "ADICIONAR_EVENTO", "entrada": entrada, "saida": sucesso}
    if sucesso:
        return f"Evento '{titulo}' adicionado com sucesso em {data_evento} às {hora_inicio}.", [], passo
    return f"Falha ao adicionar o evento '{titulo}' (verifique data e horário).", [], passo


def _tratar_remover_evento(match: re.Match):
    bruto = match.group(1).strip()
    try:
        evento_id = int(bruto)
    except ValueError:
        _log_chamada("REMOVER_EVENTO", bruto, "ERRO: id inválido")
        passo = {"ferramenta": "REMOVER_EVENTO", "entrada": bruto, "saida": "ERRO: id inválido"}
        return f"ERRO: id de evento inválido: {bruto!r}", [], passo
    sucesso = deletar_evento(evento_id)
    _log_chamada("REMOVER_EVENTO", {"id": evento_id}, sucesso)
    passo = {"ferramenta": "REMOVER_EVENTO", "entrada": {"id": evento_id}, "saida": sucesso}
    if sucesso:
        return f"Evento {evento_id} removido com sucesso.", [], passo
    return f"Não encontrei nenhum evento com id {evento_id}.", [], passo


def _tratar_listar_tarefas(match: re.Match):
    status = (match.group(1) or "").strip() or None
    tarefas = listar_tarefas(status)
    _log_chamada("LISTAR_TAREFAS", {"status": status}, tarefas)
    passo = {"ferramenta": "LISTAR_TAREFAS", "entrada": {"status": status}, "saida": tarefas}
    return f"Tarefas (status={status or 'todas'}):\n{tarefas}", [], passo


def _tratar_adicionar_tarefa(match: re.Match):
    partes = [p.strip() for p in match.group(1).split("|")]
    titulo = partes[0]
    descricao = partes[1] if len(partes) > 1 and partes[1] else None
    prioridade = partes[2] if len(partes) > 2 and partes[2] else "normal"
    bruto_evento_id = partes[3] if len(partes) > 3 and partes[3] else None
    evento_id = int(bruto_evento_id) if bruto_evento_id and bruto_evento_id.isdigit() else None
    sucesso = adicionar_tarefa(titulo, descricao, prioridade, evento_id)
    entrada = {"titulo": titulo, "descricao": descricao, "prioridade": prioridade, "evento_id": evento_id}
    _log_chamada("ADICIONAR_TAREFA", entrada, sucesso)
    passo = {"ferramenta": "ADICIONAR_TAREFA", "entrada": entrada, "saida": sucesso}
    if sucesso:
        return f"Tarefa '{titulo}' adicionada com sucesso (prioridade: {prioridade}).", [], passo
    return f"Falha ao adicionar a tarefa '{titulo}'.", [], passo


def _tratar_concluir_tarefa(match: re.Match):
    bruto = match.group(1).strip()
    try:
        tarefa_id = int(bruto)
    except ValueError:
        _log_chamada("CONCLUIR_TAREFA", bruto, "ERRO: id inválido")
        passo = {"ferramenta": "CONCLUIR_TAREFA", "entrada": bruto, "saida": "ERRO: id inválido"}
        return f"ERRO: id de tarefa inválido: {bruto!r}", [], passo
    sucesso = concluir_tarefa(tarefa_id)
    _log_chamada("CONCLUIR_TAREFA", {"id": tarefa_id}, sucesso)
    passo = {"ferramenta": "CONCLUIR_TAREFA", "entrada": {"id": tarefa_id}, "saida": sucesso}
    if sucesso:
        return f"Tarefa {tarefa_id} marcada como concluída.", [], passo
    return f"Não encontrei nenhuma tarefa com id {tarefa_id}.", [], passo


# Tabela de despacho: cada marcador que o LLM pode emitir, casado por regex,
# na ordem em que deve ser testado, junto da função que o trata.
_REGRAS = [
    (re.compile(r"```sql\s*(.*?)```", re.DOTALL | re.IGNORECASE), _tratar_sql),
    (re.compile(r"\[BUSCAR_DOCS:\s*(.*?)\]", re.DOTALL | re.IGNORECASE), _tratar_buscar_docs),
    (re.compile(r"\[PLANO_ESTUDOS\]", re.IGNORECASE), _tratar_plano_estudos),
    (re.compile(r"\[PRIORIDADES_HOJE\]", re.IGNORECASE), _tratar_prioridades_hoje),
    (re.compile(r"\[CONSULTAR_AGENDA(?::\s*(.*?))?\]", re.IGNORECASE), _tratar_consultar_agenda),
    (re.compile(r"\[ADICIONAR_EVENTO:\s*(.*?)\]", re.DOTALL | re.IGNORECASE), _tratar_adicionar_evento),
    (re.compile(r"\[REMOVER_EVENTO:\s*(.*?)\]", re.IGNORECASE), _tratar_remover_evento),
    (re.compile(r"\[LISTAR_TAREFAS(?::\s*(.*?))?\]", re.IGNORECASE), _tratar_listar_tarefas),
    (re.compile(r"\[ADICIONAR_TAREFA:\s*(.*?)\]", re.DOTALL | re.IGNORECASE), _tratar_adicionar_tarefa),
    (re.compile(r"\[CONCLUIR_TAREFA:\s*(.*?)\]", re.IGNORECASE), _tratar_concluir_tarefa),
]


def executar_ferramenta(conteudo: str):
    """
    Detecta e executa a ferramenta pedida pelo modelo no texto `conteudo`.
    Retorna (texto_resultado, chunks, passo) para ser anexado à conversa, onde
    passo é {"ferramenta": str, "entrada": Any, "saida": Any}, ou None se
    nenhuma ferramenta foi reconhecida.
    """
    for padrao, tratador in _REGRAS:
        match = padrao.search(conteudo)
        if match:
            return tratador(match)
    return None
