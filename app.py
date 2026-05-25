import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "jarvis_academica"))

import streamlit as st
from agente.agente import rodar_agente
from database.operacoes import (
    listar_tarefas,
    adicionar_tarefa,
    concluir_tarefa,
    desconcluir_tarefa,
    deletar_tarefa,
)

st.set_page_config(page_title="Jarvis — Assistente Acadêmico", page_icon="J", layout="wide")

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .prioridade-alta  { color: #e74c3c; font-weight: bold; }
    .prioridade-normal{ color: #f39c12; font-weight: bold; }
    .prioridade-baixa { color: #27ae60; font-weight: bold; }
    .status-concluida { text-decoration: line-through; color: #888; }
    .tarefa-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        background: #fafafa;
    }
    [data-testid="stHorizontalBlock"] {
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📚 Conteúdos disponíveis")
    st.caption("Pergunte ao Jarvis sobre:")
    st.markdown("""
- Embedding
- PLN (Processamento de Linguagem Natural)
- RAG (Retrieval-Augmented Generation)
- Banco Vetorial
- Transformers
- LLM (Large Language Models)
- Quarto Chinês
- Viés da IA
- Deep Learning
- Aprendizado de Máquina
""")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 Jarvis — Assistente Acadêmico")
st.caption("Organize sua agenda, consulte eventos e explore conteúdos sobre Inteligência Artificial")

# ── Abas ─────────────────────────────────────────────────────────────────────
aba_chat, aba_tarefas = st.tabs(["💬 Chat com Jarvis", "✅ Lista de Tarefas"])


# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — CHAT
# ════════════════════════════════════════════════════════════════════════════
if "historico" not in st.session_state:
    st.session_state.historico = []

with aba_chat:
    st.subheader("Converse com Jarvis")

    if not st.session_state.historico:
        st.info(
            "Você pode consultar sua agenda e tirar dúvidas sobre Inteligência Artificial. "
            "Para gerenciar tarefas, use a aba **Lista de Tarefas**. "
            "Exemplos: *'Quais eventos tenho essa semana?'*, "
            "*'O que é um embedding?'*, "
            "*'Me explica como funciona um transformer'*"
        )

    for msg in st.session_state.historico:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            chunks = msg.get("chunks", [])
            if chunks:
                with st.expander(f"📄 Ver trechos usados ({len(chunks)} chunk{'s' if len(chunks) > 1 else ''})"):
                    for i, c in enumerate(chunks, 1):
                        fonte = c["id"].rsplit("-chunk-", 1)[0]
                        st.markdown(f"**{i}. {fonte}** — score: `{c['score']:.3f}`")
                        st.caption(c["text"][:400] + ("..." if len(c["text"]) > 400 else ""))
                        if i < len(chunks):
                            st.divider()

    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([9, 1])
        with col_input:
            pergunta = st.text_input("", placeholder="Como posso ajudar?", label_visibility="collapsed")
        with col_btn:
            submitted = st.form_submit_button("Enviar", use_container_width=True)

    if submitted and pergunta.strip():
        st.session_state.historico.append({"role": "user", "content": pergunta})
        with st.spinner("Jarvis está pensando..."):
            resultado = rodar_agente(pergunta)
        response = resultado["resposta"]
        chunks   = resultado["chunks"]
        st.session_state.historico.append({"role": "ai", "content": response, "chunks": chunks})
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — TAREFAS
# ════════════════════════════════════════════════════════════════════════════
with aba_tarefas:
    st.subheader("📋 Minhas Tarefas")

    # ── Formulário para adicionar tarefa ─────────────────────────────────────
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False

    if st.button("➕ Adicionar nova tarefa"):
        st.session_state.show_add_form = not st.session_state.show_add_form

    submitted = False
    if st.session_state.show_add_form:
        with st.form("form_add_tarefa", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                novo_titulo = st.text_input("Título da tarefa")
                nova_descricao = st.text_area("Descrição (opcional)", height=80)
            with col2:
                nova_prioridade = st.selectbox(
                    "Prioridade",
                    options=["baixa", "normal", "alta"],
                    index=1,
                )
                st.write("")
                st.write("")
                submitted = st.form_submit_button("✅ Salvar tarefa", use_container_width=True)

        if submitted:
            if novo_titulo.strip():
                ok = adicionar_tarefa(
                    titulo=novo_titulo.strip(),
                    descricao=nova_descricao.strip() or None,
                    prioridade=nova_prioridade,
                )
                if ok:
                    st.session_state.show_add_form = False
                    st.rerun()
                else:
                    st.error("Erro ao adicionar a tarefa.")
            else:
                st.warning("O título não pode estar vazio.")

    # ── Filtro de status ──────────────────────────────────────────────────────
    filtro = st.radio(
        "Exibir:",
        options=["Pendentes", "Concluídas", "Todas"],
        horizontal=True,
        key="filtro_status",
    )

    mapa_filtro = {"Pendentes": "pendente", "Concluídas": "concluida", "Todas": None}
    tarefas = listar_tarefas(status=mapa_filtro[filtro])

    if not tarefas:
        st.info("Nenhuma tarefa encontrada.")
    else:
        # Ícones de prioridade
        icone_prioridade = {"alta": "🔴", "normal": "🟡", "baixa": "🟢"}

        for t in tarefas:
            concluida = t["status"] == "concluida"
            icone = icone_prioridade.get(t["prioridade"], "⚪")

            with st.container():
                col_info, col_acoes = st.columns([7, 1])

                with col_info:
                    titulo_html = (
                        f'<span class="status-concluida">{t["titulo"]}</span>'
                        if concluida
                        else f'<strong>{t["titulo"]}</strong>'
                    )
                    st.markdown(
                        f"""
                        <div class="tarefa-card">
                            <div>{icone} {titulo_html} &nbsp;
                                <small style="color:#999;">#{t['id']} · Prioridade: {t['prioridade']}</small>
                            </div>
                            {"<div style='color:#555;font-size:0.85em;margin-top:4px;'>" + t['descricao'] + "</div>" if t.get('descricao') else ""}
                            {"<div style='color:#aaa;font-size:0.78em;margin-top:4px;'>✔ Concluída em: " + str(t.get('data_conclusao','')) + "</div>" if concluida else ""}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

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

    # ── Rodapé de contagem ────────────────────────────────────────────────────
    todas = listar_tarefas()
    pendentes = sum(1 for t in todas if t["status"] == "pendente")
    concluidas = sum(1 for t in todas if t["status"] == "concluida")
    st.divider()
    st.caption(f"📊 Total: {len(todas)} tarefa(s) · ⏳ Pendentes: {pendentes} · ✅ Concluídas: {concluidas}")