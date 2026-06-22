import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "jarvis_academica"))

import streamlit as st
from agente.agente import rodar_agente
from database.tarefas import (
    listar_tarefas,
    adicionar_tarefa,
    concluir_tarefa,
    desconcluir_tarefa,
    deletar_tarefa,
)
from database.agenda import adicionar_evento, deletar_evento, listar_eventos_proximos
from core.constantes import TOPICOS_IA, SUGESTOES_AGENDA, SUGESTOES_IA, SUGESTOES_ESTUDO
from database.quiz import registrar_tentativa
from estudos.quiz import gerar_pergunta, avaliar_resposta
from estudos.recomendacao import recomendar_revisao

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(page_title="Jarvis — Assistente Acadêmico", page_icon="J", layout="wide", initial_sidebar_state="expanded")

# ── Constantes ────────────────────────────────────────────────────────────────
COR_PRIORIDADE = {"alta": "red", "normal": "blue", "baixa": "green"}

# ── Session state ─────────────────────────────────────────────────────────────
if "historico" not in st.session_state:
    st.session_state.historico = []
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False
if "show_add_form_evento" not in st.session_state:
    st.session_state.show_add_form_evento = False

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] { align-items: stretch; }
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: center; }
    div[data-testid="stFormSubmitButton"] button,
    .stButton button { white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📅 Próximos compromissos")
    eventos_proximos = listar_eventos_proximos(dias=7)
    if eventos_proximos:
        for evento in eventos_proximos:
            ano, mes, dia = evento["data_evento"].split("-")
            linha = f"- **{evento['titulo']}** — {dia}/{mes}"
            if evento["hora_inicio"]:
                linha += f" às {evento['hora_inicio']}"
            st.markdown(linha)
    else:
        st.caption("Nenhum compromisso nos próximos 7 dias.")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 Jarvis — Assistente Acadêmico")

# ── Abas ─────────────────────────────────────────────────────────────────────
aba_chat, aba_tarefas, aba_agenda, aba_quiz = st.tabs(
    ["💬 Chat com Jarvis", "✅ Lista de Tarefas", "📅 Agenda", "🧠 Quiz"]
)


# ── Funções auxiliares ────────────────────────────────────────────────────────
def exibir_chunks(chunks: list):
    label = f"📄 Ver trechos usados ({len(chunks)} chunk{'s' if len(chunks) > 1 else ''})"
    with st.expander(label):
        for i, c in enumerate(chunks, 1):
            fonte = c["id"].rsplit("-chunk-", 1)[0]
            st.markdown(f"**{i}. {fonte}** — score: `{c['score']:.3f}`")
            st.caption(c["text"][:400] + ("..." if len(c["text"]) > 400 else ""))
            if i < len(chunks):
                st.divider()


def _formatar_saida_passo(passo: dict) -> str:
    texto = passo.get("texto_resultado")
    if texto is None:
        texto = str(passo.get("saida"))
    limite = 2000
    return texto[:limite] + ("..." if len(texto) > limite else "")


def exibir_passos(passos: list):
    label = f"🔧 Ver passos do agente ({len(passos)} passo{'s' if len(passos) > 1 else ''})"
    with st.expander(label):
        for i, p in enumerate(passos, 1):
            st.markdown(f"**{i}. 🔧 {p['ferramenta']}** — entrada: `{p['entrada']}`")
            st.code(_formatar_saida_passo(p), language=None)
            if i < len(passos):
                st.divider()


def renderizar_tarefa(t: dict, concluida: bool) -> None:
    """Renderiza uma tarefa usando componentes nativos do Streamlit (sem HTML manual)."""
    titulo_md = f"~~{t['titulo']}~~" if concluida else f"**{t['titulo']}**"
    st.markdown(f"{titulo_md}  ·  `#{t['id']}`")
    st.badge(t["prioridade"].capitalize(), color=COR_PRIORIDADE.get(t["prioridade"], "gray"))
    if t.get("evento_titulo"):
        st.caption(f"📅 Vinculada a: {t['evento_titulo']} ({t['evento_data']})")
    if t.get("descricao"):
        st.caption(t["descricao"])
    if concluida:
        st.caption(f"✔ Concluída em: {t.get('data_conclusao', '')}")


def renderizar_evento(e: dict) -> None:
    """Renderiza um evento usando componentes nativos do Streamlit (sem HTML manual)."""
    ano, mes, dia = e["data_evento"].split("-")
    horario = e["hora_inicio"] or ""
    if e.get("hora_fim"):
        horario += f" – {e['hora_fim']}"
    st.markdown(f"**{e['titulo']}**  ·  `#{e['id']}`")
    st.caption(f"🗓️ {dia}/{mes}/{ano}" + (f" às {horario}" if horario else ""))
    if e.get("local"):
        st.caption(f"📍 {e['local']}")
    if e.get("descricao"):
        st.caption(e["descricao"])


def enviar_mensagem(pergunta: str):
    historico_anterior = list(st.session_state.historico)
    st.session_state.historico.append({"role": "user", "content": pergunta})

    with st.status("Jarvis está pensando...", expanded=True) as status:
        def _on_passo(passo):
            status.update(label=f"🔧 {passo['ferramenta']}")
            status.write(f"**{passo['ferramenta']}** — entrada: `{passo['entrada']}`")
            status.code(_formatar_saida_passo(passo), language=None)

        try:
            resultado = rodar_agente(pergunta, historico_anterior, on_passo=_on_passo)
        except Exception:
            status.update(label="Erro ao processar", state="error")
            raise
        status.update(label="Resposta pronta", state="complete", expanded=False)

    st.session_state.historico.append({
        "role": "ai",
        "content": resultado["resposta"],
        "chunks": resultado["chunks"],
        "passos": resultado["passos"],
    })
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — CHAT
# ════════════════════════════════════════════════════════════════════════════
with aba_chat:
    st.subheader("Converse com Jarvis")

    with st.expander("📚 Conteúdos disponíveis — pergunte ao Jarvis sobre:"):
        st.markdown("\n".join(f"- {topico}" for topico in TOPICOS_IA))

    # Sugestão clicada vira pergunta imediatamente
    if "pergunta_sugerida" in st.session_state:
        enviar_mensagem(st.session_state.pop("pergunta_sugerida"))

    # Tela de boas-vindas com sugestões (só aparece com chat vazio)
    if not st.session_state.historico:
        st.caption("Para gerenciar tarefas, use a aba **Lista de Tarefas**. Experimente perguntar:")
        selecionada = st.pills("Sugestões", SUGESTOES_AGENDA + SUGESTOES_ESTUDO + SUGESTOES_IA, label_visibility="collapsed")
        if selecionada:
            st.session_state.pergunta_sugerida = selecionada
            st.rerun()

    # Histórico de mensagens
    for msg in st.session_state.historico:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("passos"):
                exibir_passos(msg["passos"])
            if msg.get("chunks"):
                exibir_chunks(msg["chunks"])

    # Campo de entrada
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            pergunta = st.text_input("Mensagem", placeholder="Como posso ajudar?", label_visibility="collapsed")
        with col_btn:
            submitted = st.form_submit_button("Enviar", use_container_width=True)

    if submitted and pergunta.strip():
        enviar_mensagem(pergunta)


# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — TAREFAS
# ════════════════════════════════════════════════════════════════════════════
with aba_tarefas:
    st.subheader("📋 Minhas Tarefas")

    # Formulário para adicionar tarefa (toggle)
    if st.button("➕ Adicionar nova tarefa"):
        st.session_state.show_add_form = not st.session_state.show_add_form

    submitted_tarefa = False
    if st.session_state.show_add_form:
        with st.form("form_add_tarefa", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                novo_titulo    = st.text_input("Título da tarefa")
                nova_descricao = st.text_area("Descrição (opcional)", height=80)
            with col2:
                nova_prioridade = st.selectbox("Prioridade", options=["baixa", "normal", "alta"], index=1)
                eventos_disponiveis = listar_eventos_proximos(dias=180)
                opcoes_evento = {"Nenhum": None}
                for ev in eventos_disponiveis:
                    opcoes_evento[f"{ev['titulo']} ({ev['data_evento']})"] = ev["id"]
                evento_selecionado = st.selectbox("Vincular a um evento (opcional)", options=list(opcoes_evento.keys()))
                submitted_tarefa = st.form_submit_button("✅ Salvar tarefa", use_container_width=True)

        if submitted_tarefa:
            if novo_titulo.strip():
                ok = adicionar_tarefa(
                    titulo=novo_titulo.strip(),
                    descricao=nova_descricao.strip() or None,
                    prioridade=nova_prioridade,
                    evento_id=opcoes_evento[evento_selecionado],
                )
                if ok:
                    st.session_state.show_add_form = False
                    st.rerun()
                else:
                    st.error("Erro ao adicionar a tarefa.")
            else:
                st.warning("O título não pode estar vazio.")

    # Filtro e listagem
    filtro  = st.radio("Exibir:", options=["Pendentes", "Concluídas", "Todas"], horizontal=True, key="filtro_status")
    mapa    = {"Pendentes": "pendente", "Concluídas": "concluida", "Todas": None}
    tarefas = listar_tarefas(status=mapa[filtro])

    if not tarefas:
        st.info("Nenhuma tarefa encontrada.")
    else:
        for t in tarefas:
            concluida = t["status"] == "concluida"
            with st.container(border=True):
                col_info, col_acoes = st.columns([7, 1])

                with col_info:
                    renderizar_tarefa(t, concluida)

                with col_acoes:
                    b1, b2 = st.columns(2)
                    with b1:
                        if not concluida:
                            if st.button("✔", key=f"concluir_{t['id']}", help="Concluir tarefa", use_container_width=True):
                                concluir_tarefa(t["id"])
                                st.rerun()
                        else:
                            if st.button("↩", key=f"desconcluir_{t['id']}", help="Reabrir tarefa", use_container_width=True):
                                desconcluir_tarefa(t["id"])
                                st.rerun()
                    with b2:
                        if st.button("🗑", key=f"deletar_{t['id']}", help="Deletar tarefa", use_container_width=True):
                            deletar_tarefa(t["id"])
                            st.rerun()

    # Rodapé com contagem
    todas     = listar_tarefas()
    pendentes = sum(1 for t in todas if t["status"] == "pendente")
    concluidas = sum(1 for t in todas if t["status"] == "concluida")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Total", len(todas))
    c2.metric("⏳ Pendentes", pendentes)
    c3.metric("✅ Concluídas", concluidas)


# ════════════════════════════════════════════════════════════════════════════
# ABA 3 — AGENDA
# ════════════════════════════════════════════════════════════════════════════
with aba_agenda:
    st.subheader("📅 Minha Agenda")

    if st.button("➕ Adicionar novo evento"):
        st.session_state.show_add_form_evento = not st.session_state.show_add_form_evento

    submitted_evento = False
    if st.session_state.show_add_form_evento:
        with st.form("form_add_evento", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                novo_titulo_evt    = st.text_input("Título do evento")
                nova_descricao_evt = st.text_area("Descrição (opcional)", height=80)
                novo_local         = st.text_input("Local (opcional)")
            with col2:
                nova_data         = st.date_input("Data do evento")
                nova_hora_inicio  = st.time_input("Hora de início", value=None)
                nova_hora_fim     = st.time_input("Hora de fim (opcional)", value=None)
                submitted_evento  = st.form_submit_button("✅ Salvar evento", use_container_width=True)

        if submitted_evento:
            if not novo_titulo_evt.strip():
                st.warning("O título não pode estar vazio.")
            elif nova_hora_inicio is None:
                st.warning("A hora de início é obrigatória.")
            else:
                ok = adicionar_evento(
                    titulo=novo_titulo_evt.strip(),
                    data_evento=nova_data.isoformat(),
                    hora_inicio=nova_hora_inicio.strftime("%H:%M"),
                    descricao=nova_descricao_evt.strip() or None,
                    hora_fim=nova_hora_fim.strftime("%H:%M") if nova_hora_fim else None,
                    local=novo_local.strip() or None,
                )
                if ok:
                    st.session_state.show_add_form_evento = False
                    st.rerun()
                else:
                    st.error("Erro ao adicionar o evento.")

    # Janela de exibição e listagem
    dias_janela = st.number_input(
        "Mostrar eventos dos próximos N dias", min_value=1, max_value=365, value=30, step=1
    )
    eventos = listar_eventos_proximos(dias=dias_janela)

    if not eventos:
        st.info("Nenhum evento encontrado nessa janela de tempo.")
    else:
        for e in eventos:
            with st.container(border=True):
                col_info, col_acoes = st.columns([7, 1])

                with col_info:
                    renderizar_evento(e)

                with col_acoes:
                    if st.button("🗑", key=f"deletar_evento_{e['id']}", help="Deletar evento", use_container_width=True):
                        deletar_evento(e["id"])
                        st.rerun()

    # Rodapé com contagem
    st.divider()
    st.metric("📊 Eventos na janela selecionada", len(eventos))


# ════════════════════════════════════════════════════════════════════════════
# ABA 4 — QUIZ / ACTIVE RECALL
# ════════════════════════════════════════════════════════════════════════════
with aba_quiz:
    st.subheader("🧠 Quiz — Active Recall")
    st.caption("Escolha um tópico, responda à pergunta gerada e receba uma avaliação na hora.")

    # Recomendações com base no histórico de tentativas
    recomendacoes = recomendar_revisao(list(TOPICOS_IA.keys()))
    if recomendacoes:
        st.markdown("**📊 Recomendado para você:**")
        st.markdown("\n".join(f"- {r['topico']} — {r['motivo']}" for r in recomendacoes))
        st.divider()

    coluna_topico, coluna_quantidade = st.columns(2)
    with coluna_topico:
        topico_escolhido = st.selectbox("Tópico", options=list(TOPICOS_IA.keys()), key="quiz_topico_select")
    with coluna_quantidade:
        quantidade_perguntas = st.selectbox(
            "Quantidade de perguntas", options=list(range(1, 11)), key="quiz_quantidade"
        )

    if st.button("🎲 Gerar pergunta(s)"):
        perguntas = []
        with st.spinner("Gerando pergunta(s)..."):
            for _ in range(quantidade_perguntas):
                perguntas_ja_geradas = [p["pergunta"] for p in perguntas]
                dados = gerar_pergunta(topico_escolhido, perguntas_ja_geradas)
                perguntas.append(dados)
        st.session_state.quiz_perguntas = perguntas
        st.session_state.pop("quiz_resultados", None)

    if "quiz_perguntas" in st.session_state:
        st.divider()
        perguntas = st.session_state.quiz_perguntas
        ja_respondido = "quiz_resultados" in st.session_state

        if ja_respondido:
            soma_notas = 0
            for resultado in st.session_state.quiz_resultados:
                soma_notas += resultado["nota"]
            media_notas = soma_notas / len(st.session_state.quiz_resultados)
            st.metric("Nota média do lote", f"{media_notas:.1f}/10")

        for i, dados in enumerate(perguntas):
            st.markdown(f"**Pergunta {i + 1} sobre {dados['topico']}:**")
            st.write(dados["pergunta"])
            st.text_area("Sua resposta", key=f"quiz_resposta_{i}", disabled=ja_respondido)

            if ja_respondido:
                resultado = st.session_state.quiz_resultados[i]
                texto_resultado = f"**Nota: {resultado['nota']}/10**\n\n{resultado['feedback']}"
                if resultado["nota"] >= 7:
                    st.success(texto_resultado)
                elif resultado["nota"] >= 4:
                    st.warning(texto_resultado)
                else:
                    st.error(texto_resultado)

        if st.button("✅ Responder", disabled=ja_respondido):
            resultados = []
            with st.spinner("Avaliando resposta(s)..."):
                for i, dados in enumerate(perguntas):
                    resposta_usuario = st.session_state.get(f"quiz_resposta_{i}", "")
                    resultado = avaliar_resposta(
                        dados["pergunta"], dados["resposta_esperada"], resposta_usuario
                    )
                    registrar_tentativa(dados["topico"], resultado["nota"])
                    resultados.append(resultado)
            st.session_state.quiz_resultados = resultados
            st.rerun()

        if "quiz_resultados" in st.session_state:
            if st.button("➡️ Próximas perguntas"):
                for i in range(len(perguntas)):
                    st.session_state.pop(f"quiz_resposta_{i}", None)
                st.session_state.pop("quiz_perguntas", None)
                st.session_state.pop("quiz_resultados", None)
                st.rerun()
