import streamlit as st
from agente.agente import rodar_agente
from database.operacoes import (
    listar_tarefas,
    adicionar_tarefa,
    concluir_tarefa,
    desconcluir_tarefa,
    deletar_tarefa,
)

st.set_page_config(page_title="Jarvis Acadêmica", page_icon="J", layout="wide")

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
    st.header("📎 Faça Upload de Arquivos")
    st.file_uploader(
        "Upload de PDF para ajuda",
        type=["pdf"],
        accept_multiple_files=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 Jarvis — Assistente Acadêmica")
st.caption("Agenda inteligente + Lista de Tarefas")

# ── Abas ─────────────────────────────────────────────────────────────────────
aba_chat, aba_tarefas = st.tabs(["💬 Chat com Jarvis", "✅ Lista de Tarefas"])


# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — CHAT
# ════════════════════════════════════════════════════════════════════════════
with aba_chat:
    st.subheader("Converse com a Jarvis")
    st.info(
        "Você pode perguntar sobre eventos, contatos, lembretes e tarefas. "
        "Exemplos: *'Quais são minhas tarefas pendentes?'*, "
        "*'Adiciona a tarefa Estudar Álgebra com prioridade alta'*, "
        "*'Quais eventos tenho essa semana?'*"
    )

    question = st.chat_input("Como posso ajudar?")

    if question:
        st.chat_message("user").write(question)
        with st.spinner("Jarvis está pensando..."):
            response = rodar_agente(question)
        st.chat_message("ai").write(response)


# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — TAREFAS
# ════════════════════════════════════════════════════════════════════════════
with aba_tarefas:
    st.subheader("📋 Minhas Tarefas")

    # ── Formulário para adicionar tarefa ─────────────────────────────────────
    with st.expander("➕ Adicionar nova tarefa", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            novo_titulo = st.text_input("Título da tarefa", key="novo_titulo")
            nova_descricao = st.text_area("Descrição (opcional)", key="nova_descricao", height=80)
        with col2:
            nova_prioridade = st.selectbox(
                "Prioridade",
                options=["baixa", "normal", "alta"],
                index=1,
                key="nova_prioridade",
            )
            st.write("")
            st.write("")
            if st.button("✅ Salvar tarefa", use_container_width=True):
                if novo_titulo.strip():
                    ok = adicionar_tarefa(
                        titulo=novo_titulo.strip(),
                        descricao=nova_descricao.strip() or None,
                        prioridade=nova_prioridade,
                    )
                    if ok:
                        st.success("Tarefa adicionada com sucesso!")
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
                col_info, col_acoes = st.columns([5, 1])

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
                    if not concluida:
                        if st.button("✔ Concluir", key=f"concluir_{t['id']}", use_container_width=True):
                            concluir_tarefa(t["id"])
                            st.rerun()
                    else:
                        if st.button("↩ Reabrir", key=f"desconcluir_{t['id']}", use_container_width=True):
                            desconcluir_tarefa(t["id"])
                            st.rerun()
                    if st.button("🗑 Deletar", key=f"deletar_{t['id']}", use_container_width=True):
                        deletar_tarefa(t["id"])
                        st.rerun()

    # ── Rodapé de contagem ────────────────────────────────────────────────────
    todas = listar_tarefas()
    pendentes = sum(1 for t in todas if t["status"] == "pendente")
    concluidas = sum(1 for t in todas if t["status"] == "concluida")
    st.divider()
    st.caption(f"📊 Total: {len(todas)} tarefa(s) · ⏳ Pendentes: {pendentes} · ✅ Concluídas: {concluidas}")