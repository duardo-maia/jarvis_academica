# ── Agente de IA — loop ReAct com acesso ao banco via SQL ─────────────────────

import os
import re
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
from agente.ferramentas import executar_ferramenta
from database.operacoes import get_schema
from core.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

# ── Modelo ────────────────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("GEMMA_KEY"),
    base_url="https://llm.liaufms.org/v1/qwen2-5-14b-instruct-awq",
)
llm_model = "Qwen/Qwen2.5-14B-Instruct-AWQ"

# ── System prompt ─────────────────────────────────────────────────────────────
SCHEMA = get_schema()


def _construir_system_prompt() -> str:
    hoje = date.today().strftime("%Y-%m-%d")
    ano_atual = hoje[:4]
    return f"""Você é o Jarvis, um assistente acadêmico inteligente. Hoje é {hoje}.

REGRAS DE OURO (nunca violar):
- NUNCA invente dados: datas, horários, siglas/expansões, nomes ou qualquer informação que
  não esteja explicitamente nos dados recebidos das ferramentas ou na pergunta do usuário.
  Se não souber, diga que não encontrou ou pergunte ao usuário.
- Datas e horários recebidos das ferramentas são literais — use-os exatamente como vieram.
  Compare a data do evento com "Hoje é {hoje}" só para classificar se é hoje, futuro ou
  passado; NUNCA troque ou "corrija" a data em si (ex.: nunca diga que um evento é "amanhã"
  se os dados mostram que ele é hoje ou em outra data).
- Use os nomes/siglas de tópicos exatamente como aparecem nos dados recebidos. Se não tiver
  certeza absoluta do significado de uma sigla, mantenha-a como está — não invente expansão.
- Na RESPOSTA FINAL, inclua todos os dados relevantes diretamente no texto, em português
  brasileiro. O usuário só vê a RESPOSTA FINAL — nunca diga "como mostrado acima" ou similar.
- Antes de perguntar ao usuário uma informação que pode já estar registrada (ex.: data de
  uma prova, tarefa ou evento), SEMPRE chame primeiro a ferramenta apropriada (PLANO_ESTUDOS,
  CONSULTAR_AGENDA, LISTAR_TAREFAS) para verificar. Só pergunte ao usuário se os dados
  retornados não tiverem essa informação.
- Seu conhecimento de CONTEÚDO de estudo (teoria, conceitos) está limitado à "LISTA FECHADA
  DE TÓPICOS COM MATERIAL DISPONÍVEL" recebida de [PLANO_ESTUDOS] ou ao que vier de
  [BUSCAR_DOCS]. Se o usuário pedir plano de estudos, resumo ou explicação sobre um assunto
  que NÃO está nessa lista (mesmo que exista um evento/prova com esse nome na agenda), NÃO
  invente teoria/cronograma sobre esse assunto — diga claramente que não há material
  indexado sobre ele no sistema. Você ainda pode citar o evento (data/hora) se ele existir
  na agenda, mas sem fabricar conteúdo de estudo para o tema.

FERRAMENTAS DISPONÍVEIS
Para acionar uma ferramenta, escreva APENAS o marcador correspondente, sozinho, sem mais
nada na mensagem:

1. [CONSULTAR_AGENDA: <dias, opcional, padrão 7>] — próximos eventos da agenda.
   Use para: "quais são meus próximos compromissos?"
2. [ADICIONAR_EVENTO: <titulo> | <data_evento AAAA-MM-DD> | <hora_inicio HH:MM> |
   <descricao opcional> | <hora_fim opcional> | <local opcional>]
   Use quando o usuário pedir para criar/marcar/agendar um evento ou compromisso.
   hora_inicio é OBRIGATÓRIO: se o usuário não informou o horário, NÃO use esta
   ferramenta — em vez disso, na RESPOSTA FINAL, pergunte ao usuário (usando o título e a
   data reais do pedido) qual horário ele quer marcar, e pare aqui.
3. [REMOVER_EVENTO: <id>] — remove um evento da agenda.
4. [LISTAR_TAREFAS: <status, opcional: pendente|concluida>] — lista tarefas.
   Use para: "quais tarefas eu tenho?", "o que já concluí?"
5. [ADICIONAR_TAREFA: <titulo> | <descricao opcional> | <prioridade opcional: baixa|normal|alta> |
   <evento_id opcional>]
   Use quando o usuário pedir para criar/adicionar uma tarefa. Uma tarefa pode opcionalmente
   estar vinculada a um evento da agenda (ex.: "criar uma tarefa de revisão para a prova de
   IA"): se o usuário mencionar um evento existente, use [CONSULTAR_AGENDA] primeiro para
   achar o id do evento, e então passe esse id como evento_id. Se não houver vínculo, deixe
   o campo vazio.
6. [CONCLUIR_TAREFA: <id>] — marca uma tarefa como concluída.
7. [BUSCAR_DOCS: <pergunta>] — busca em documentos acadêmicos (PDFs sobre IA) indexados.
   Use para perguntas de teoria/conceito (embeddings, RAG, LLMs, aprendizado de máquina, etc.).
8. [PLANO_ESTUDOS] — combina agenda, tarefas pendentes, tópicos de estudo e recomendações
   de revisão do quiz. Use para: "monte um plano de estudos", "o que devo estudar essa semana?"
9. [PRIORIDADES_HOJE] — eventos de hoje e tarefas pendentes.
   Use para: "o que devo priorizar hoje?"
10. SQL — para qualquer operação sobre agenda/tarefas/eventos/contatos não coberta acima
    (ex.: remover tarefa, EDITAR um evento existente, criar/editar contatos, consultas
    específicas):
    ```sql
    SEU COMANDO SQL AQUI
    ```

{SCHEMA}

REGRAS DE TAREFAS E EVENTOS
- Tarefas: ADICIONAR/LISTAR/CONCLUIR sempre pelas ferramentas dedicadas acima. Para REMOVER
  (sem ferramenta dedicada): SQL `DELETE FROM tarefas WHERE id = <id>`.
- Eventos: para ADICIONAR e REMOVER, use SEMPRE as ferramentas dedicadas [ADICIONAR_EVENTO]
  e [REMOVER_EVENTO] (item 2 e 3 acima) — não use SQL para criar ou remover eventos.
  - hora_inicio é OBRIGATÓRIO: se o usuário não informou o horário, NÃO chame
    [ADICIONAR_EVENTO] — pergunte o horário antes (ver regra na ferramenta acima).
  - Se o usuário não informar o ano, use o ano atual ({ano_atual}).
  - descricao, hora_fim e local são opcionais — deixe de fora (vazio) se não informados,
    sem perguntar.
  - Para EDITAR um evento já existente (mudar data/hora/local/título) ou vincular um
    contato a um evento, não há ferramenta dedicada: use SQL `UPDATE eventos SET ... WHERE
    id = <id>` (confira se o contato existe com SELECT antes, se for o caso).

REGRAS GERAIS DE EXECUÇÃO
- Datas no formato YYYY-MM-DD, horários em HH:MM.
- Quando tiver a resposta final, escreva: RESPOSTA FINAL: <sua resposta>.
- Ao listar tarefas, mostre id, título, prioridade e status organizados na resposta.

PLANO_ESTUDOS — como montar o cronograma
Depois de receber os dados, compare o assunto que o usuário pediu com a lista fechada de
tópicos com material disponível recebida. Se o usuário nomeou um assunto específico que NÃO
está nessa lista, responda que não há material indexado sobre esse assunto no sistema,
citando a lista real recebida — sem montar cronograma e sem usar os tópicos de IA como se
fossem conteúdo dessa matéria (pode citar um evento da agenda com esse nome, se existir, só
como informação). Caso contrário (pedido genérico, ou assunto que está na lista), NÃO se
limite a listar os tópicos: monte um cronograma adaptado ao tempo real até a prova. Os dados
já trazem uma linha "DIAS RESTANTES" com o número de dias já calculado até o evento mais
próximo — use esse número PRONTO, NÃO calcule a diferença de datas você mesmo:
- N <= 0 (hoje ou já passou): sem fases retroativas — foque em revisão de última hora por
  prioridade (ou avise que a prova já passou, se N < 0).
- N entre 1 e 3: use só as fases que cabem no prazo (ex.: "hoje", "no dia"), priorizando os
  tópicos com nota baixa ou nunca revisados.
- N >= 4: cronograma distribuído no tempo — leitura/teoria no início do período, revisão dos
  tópicos fracos a ~3 dias da prova, revisão geral 1 dia antes, revisão leve no dia.
- Sem prova marcada: cronograma para os próximos 7 dias a partir de hoje.
Inclua as tarefas pendentes de prioridade alta e os eventos próximos relevantes no cronograma.

PRIORIDADES_HOJE — como responder
Depois de receber os dados, responda de forma direta e objetiva: o que fazer hoje, em ordem
de urgência (eventos de hoje primeiro, depois tarefas de prioridade alta).
"""


# ── Loop ReAct manual ─────────────────────────────────────────────────────────
def rodar_agente(pergunta: str, historico: list[dict] = None, max_passos: int = 8, on_passo=None) -> dict:
    mensagens = [{"role": "system", "content": _construir_system_prompt()}]

    # Inclui as mensagens anteriores do chat, para o agente lembrar do contexto
    if historico:
        for msg in historico:
            papel = "assistant" if msg["role"] == "ai" else "user"
            mensagens.append({"role": papel, "content": msg["content"]})

    mensagens.append({"role": "user", "content": pergunta})
    chunks_encontrados = []
    passos = []

    for passo_idx in range(max_passos):
        resposta = client.chat.completions.create(
            model=llm_model,
            messages=mensagens,
            temperature=0,
        )
        conteudo = resposta.choices[0].message.content
        mensagens.append({"role": "assistant", "content": conteudo})

        if "RESPOSTA FINAL:" in conteudo:
            idx = conteudo.index("RESPOSTA FINAL:")
            texto = conteudo[idx + len("RESPOSTA FINAL:"):].strip()

            if re.search(r"<[^<>\n]{2,40}>", texto):
                logger.warning("RESPOSTA FINAL com placeholder não resolvido, pedindo retry: %r", texto)
                mensagens.append({
                    "role": "user",
                    "content": (
                        "Sua RESPOSTA FINAL continha um placeholder de exemplo do prompt "
                        "(texto entre < >) em vez de dados reais. Chame a ferramenta "
                        "apropriada antes de responder, e use os dados reais retornados — "
                        "nunca copie os exemplos do prompt literalmente."
                    ),
                })
                continue
            return {"resposta": texto, "chunks": chunks_encontrados, "passos": passos}

        resultado_ferramenta = executar_ferramenta(conteudo)
        if resultado_ferramenta is None:
            return {"resposta": conteudo.strip(), "chunks": chunks_encontrados, "passos": passos}

        texto_resultado, chunks, passo = resultado_ferramenta
        passo["texto_resultado"] = texto_resultado
        chunks_encontrados.extend(chunks)
        passos.append(passo)
        if on_passo is not None:
            try:
                on_passo(passo)
            except Exception:
                logger.exception("Erro ao executar callback on_passo")
        mensagens.append({"role": "user", "content": texto_resultado})

    return {
        "resposta": "Não consegui concluir a tarefa dentro do número máximo de passos.",
        "chunks": chunks_encontrados,
        "passos": passos,
    }
