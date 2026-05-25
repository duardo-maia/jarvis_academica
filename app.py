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

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(page_title="Jarvis — Assistente Acadêmico", page_icon="J", layout="wide", initial_sidebar_state="expanded")

# ── Constantes ────────────────────────────────────────────────────────────────
SUGESTOES_AGENDA = [
    "Quais eventos tenho essa semana?",
    "Quais são meus próximos eventos?",
    "Quem são meus contatos?",
]

SUGESTOES_IA = [
    "O que é um embedding?",
    "Como funciona o RAG?",
    "O que é um transformer?",
    "O que é deep learning?",
    "O que é um LLM?",
    "O que é viés na IA?",
]

ICONE_PRIORIDADE = {"alta": "🔴", "normal": "🟡", "baixa": "🟢"}

# ── Session state ─────────────────────────────────────────────────────────────
if "historico" not in st.session_state:
    st.session_state.historico = []
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .status-concluida { text-decoration: line-through; color: #888; }
    .tarefa-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        background: #fafafa;
    }
    [data-testid="stHorizontalBlock"] { align-items: center; }
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

# ── Abas ─────────────────────────────────────────────────────────────────────
aba_chat, aba_tarefas = st.tabs(["💬 Chat com Jarvis", "✅ Lista de Tarefas"])


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


def html_card_tarefa(t: dict, concluida: bool) -> str:
    icone      = ICONE_PRIORIDADE.get(t["prioridade"], "⚪")
    titulo_html = (
        f'<span class="status-concluida">{t["titulo"]}</span>'
        if concluida
        else f'<strong>{t["titulo"]}</strong>'
    )
    descricao_html = (
        f"<div style='color:#555;font-size:0.85em;margin-top:4px;'>{t['descricao']}</div>"
        if t.get("descricao") else ""
    )
    conclusao_html = (
        f"<div style='color:#aaa;font-size:0.78em;margin-top:4px;'>✔ Concluída em: {t.get('data_conclusao','')}</div>"
        if concluida else ""
    )
    return f"""
    <div class="tarefa-card">
        <div>{icone} {titulo_html} &nbsp;
            <small style="color:#999;">#{t['id']} · Prioridade: {t['prioridade']}</small>
        </div>
        {descricao_html}
        {conclusao_html}
    </div>
    """


def enviar_mensagem(pergunta: str):
    st.session_state.historico.append({"role": "user", "content": pergunta})
    with st.spinner("Jarvis está pensando..."):
        resultado = rodar_agente(pergunta)
    st.session_state.historico.append({
        "role": "ai",
        "content": resultado["resposta"],
        "chunks": resultado["chunks"],
    })
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — CHAT
# ════════════════════════════════════════════════════════════════════════════
with aba_chat:
    st.subheader("Converse com Jarvis")

    # Sugestão clicada vira pergunta imediatamente
    if "pergunta_sugerida" in st.session_state:
        enviar_mensagem(st.session_state.pop("pergunta_sugerida"))

    # Tela de boas-vindas com sugestões (só aparece com chat vazio)
    if not st.session_state.historico:
        st.caption("Para gerenciar tarefas, use a aba **Lista de Tarefas**. Experimente perguntar:")
        selecionada = st.pills("Sugestões", SUGESTOES_AGENDA + SUGESTOES_IA, label_visibility="collapsed")
        if selecionada:
            st.session_state.pergunta_sugerida = selecionada
            st.rerun()

    # Histórico de mensagens
    for msg in st.session_state.historico:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("chunks"):
                exibir_chunks(msg["chunks"])

    # Campo de entrada
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([9, 1])
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
                nova_prioridade    = st.selectbox("Prioridade", options=["baixa", "normal", "alta"], index=1)
                st.write("")
                st.write("")
                submitted_tarefa = st.form_submit_button("✅ Salvar tarefa", use_container_width=True)

        if submitted_tarefa:
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

    # Filtro e listagem
    filtro  = st.radio("Exibir:", options=["Pendentes", "Concluídas", "Todas"], horizontal=True, key="filtro_status")
    mapa    = {"Pendentes": "pendente", "Concluídas": "concluida", "Todas": None}
    tarefas = listar_tarefas(status=mapa[filtro])

    if not tarefas:
        st.info("Nenhuma tarefa encontrada.")
    else:
        for t in tarefas:
            concluida = t["status"] == "concluida"
            col_info, col_acoes = st.columns([7, 1])

            with col_info:
                st.markdown(html_card_tarefa(t, concluida), unsafe_allow_html=True)

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
    st.caption(f"📊 Total: {len(todas)} tarefa(s) · ⏳ Pendentes: {pendentes} · ✅ Concluídas: {concluidas}")
