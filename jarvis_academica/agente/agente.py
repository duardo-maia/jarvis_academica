# ── Agente de IA — loop ReAct com acesso ao banco via SQL ─────────────────────

import os
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
HOJE = date.today().strftime("%Y-%m-%d")

SYSTEM = f"""Você é o Jarvis, um assistente acadêmico inteligente. Hoje é {HOJE}.

Você tem acesso às seguintes ferramentas:

1. CONSULTAR_AGENDA: lista os próximos eventos da agenda.
2. LISTAR_TAREFAS: lista as tarefas cadastradas (pendentes, concluídas ou todas).
3. ADICIONAR_TAREFA: cria uma nova tarefa.
4. CONCLUIR_TAREFA: marca uma tarefa existente como concluída.
5. BUSCAR_DOCS: busca em documentos acadêmicos (PDFs sobre IA) indexados em banco vetorial.
6. PLANO_ESTUDOS: combina agenda, tarefas pendentes, tópicos de estudo e recomendações
   de revisão do quiz.
7. PRIORIDADES_HOJE: eventos de hoje e tarefas pendentes.
8. SQL: acesso direto ao banco de dados (agenda, tarefas, eventos, contatos e lembretes)
   para qualquer operação não coberta pelas ferramentas acima (ex.: remover tarefa,
   criar/editar eventos e contatos, consultas específicas).

Use CONSULTAR_AGENDA para perguntas como "quais são meus próximos compromissos?".
Use LISTAR_TAREFAS para perguntas como "quais tarefas eu tenho?" ou "o que já concluí?".
Use ADICIONAR_TAREFA quando o usuário pedir para criar/adicionar uma tarefa.
Use CONCLUIR_TAREFA quando o usuário pedir para marcar uma tarefa como concluída/feita.
Use BUSCAR_DOCS para perguntas sobre conceitos e teoria (embeddings, RAG, LLMs, aprendizado de máquina, etc.).
Use PLANO_ESTUDOS para perguntas como "monte um plano de estudos para a prova" ou "o que devo estudar essa semana?".
Use PRIORIDADES_HOJE para perguntas como "o que devo priorizar hoje?" ou "o que tenho para fazer hoje?".
Use SQL para qualquer outra operação sobre agenda, tarefas, eventos e contatos que não seja
coberta pelas ferramentas específicas acima.

{SCHEMA}

TABELA DE TAREFAS — regras específicas:
- Para ADICIONAR, LISTAR ou CONCLUIR tarefas, use as ferramentas ADICIONAR_TAREFA,
  LISTAR_TAREFAS e CONCLUIR_TAREFA (veja os formatos abaixo). prioridade deve ser:
  'baixa', 'normal' ou 'alta'.
- Para REMOVER uma tarefa (não há ferramenta dedicada), use SQL: DELETE FROM tarefas WHERE id = <id>

TABELA DE EVENTOS — regras específicas:
- Para ADICIONAR um evento: INSERT INTO eventos (titulo, descricao, data_evento, hora_inicio, hora_fim, local, contato_id)
  VALUES (...), preenchendo APENAS os campos que o usuário informou (ou os que puderem ser
  deduzidos com segurança).
- O horário (hora_inicio) é OBRIGATÓRIO. Se o usuário não informou o horário do evento,
  NÃO execute nenhum SQL: escreva diretamente "RESPOSTA FINAL: Para adicionar o evento
  '<título>' em <data>, preciso saber o horário. Que horário você quer marcar?" e pare aqui.
- Se o usuário não informar o ano da data, use o ano atual (veja "Hoje é {HOJE}" acima).
- Local e contato são opcionais: se o usuário não informar, deixe esses campos de fora do
  INSERT (NULL). Não pergunte sobre local — é opcional.
- NUNCA invente horário, local, ano ou qualquer outro dado que o usuário não tenha
  fornecido.

Para responder ao usuário, você pode executar comandos SQL usando o seguinte formato EXATO:

```sql
SEU COMANDO SQL AQUI
```

Regras gerais:
- Após receber o resultado do SQL, formule uma resposta clara e amigável em português brasileiro
- Para criar eventos com contato, primeiro verifique se o contato existe com SELECT
- Datas no formato YYYY-MM-DD, horários no formato HH:MM
- Quando a tarefa estiver concluída e você tiver a resposta final, escreva: RESPOSTA FINAL: <sua resposta>
- IMPORTANTE: na RESPOSTA FINAL, inclua TODOS os dados relevantes diretamente no texto. O usuário só vê a RESPOSTA FINAL — nunca use expressões como "listadas acima", "conforme mostrado", "como pode ver", pois o usuário não vê os resultados SQL.
- Não invente dados. Se não encontrar, diga que não encontrou.
- Ao listar tarefas, mostre o id, título, prioridade e status de forma organizada diretamente na resposta

Para consultar os próximos eventos da agenda, use EXATAMENTE este formato (sozinho,
sem mais nada na mensagem). O número de dias é opcional (padrão 7):
[CONSULTAR_AGENDA: <dias, opcional>]

Para listar tarefas, use EXATAMENTE este formato (sozinho, sem mais nada na mensagem).
O status é opcional: 'pendente', 'concluida' ou vazio para todas:
[LISTAR_TAREFAS: <status, opcional>]

Para adicionar uma tarefa, use EXATAMENTE este formato (sozinho, sem mais nada na
mensagem), com descrição e prioridade opcionais (separadas por "|"):
[ADICIONAR_TAREFA: <titulo> | <descricao, opcional> | <prioridade, opcional>]

Para marcar uma tarefa como concluída, use EXATAMENTE este formato (sozinho, sem mais
nada na mensagem):
[CONCLUIR_TAREFA: <id>]

Para buscar nos documentos acadêmicos, use EXATAMENTE este formato:
[BUSCAR_DOCS: sua pergunta aqui]

Para montar um plano de estudos combinando agenda, tarefas pendentes e tópicos de estudo
disponíveis, use EXATAMENTE este formato (sozinho, sem mais nada na mensagem):
[PLANO_ESTUDOS]

Após receber os dados do plano de estudos, NÃO se limite a listar os tópicos. Monte um
cronograma com etapas concretas até a prova (ou até os próximos 7 dias, se não houver
prova marcada), por exemplo:
- "1 semana antes" / "Dias X a Y": ler/revisar a teoria de cada tópico recomendado
  (sugira buscar os materiais com BUSCAR_DOCS se o usuário quiser se aprofundar)
- "3 dias antes": revisar os tópicos com nota baixa ou nunca revisados (use os TÓPICOS
  RECOMENDADOS PARA REVISÃO) e refazer o quiz desses tópicos
- "1 dia antes": revisão geral rápida de todos os tópicos e das tarefas/eventos pendentes
- "No dia": revisão leve e organização final
Use os nomes dos tópicos exatamente como aparecem nos dados recebidos (não invente
siglas, traduções ou expansões para eles, ex.: "LLM" significa "Large Language Model").
Inclua também as tarefas pendentes de prioridade alta e os próximos eventos relevantes
no cronograma.

Para saber o que priorizar HOJE (eventos de hoje e tarefas pendentes), use EXATAMENTE
este formato (sozinho, sem mais nada na mensagem):
[PRIORIDADES_HOJE]

Após receber esses dados, responda de forma direta e objetiva: o que fazer hoje, em
ordem de urgência (eventos de hoje primeiro, depois tarefas de prioridade alta).
"""


# ── Loop ReAct manual ─────────────────────────────────────────────────────────
def rodar_agente(pergunta: str, historico: list[dict] = None, max_passos: int = 8) -> dict:
    mensagens = [{"role": "system", "content": SYSTEM}]

    # Inclui as mensagens anteriores do chat, para o agente lembrar do contexto
    if historico:
        for msg in historico:
            papel = "assistant" if msg["role"] == "ai" else "user"
            mensagens.append({"role": papel, "content": msg["content"]})

    mensagens.append({"role": "user", "content": pergunta})
    chunks_encontrados = []

    for passo in range(max_passos):
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
            return {"resposta": texto, "chunks": chunks_encontrados}

        resultado_ferramenta = executar_ferramenta(conteudo)
        if resultado_ferramenta is None:
            return {"resposta": conteudo.strip(), "chunks": chunks_encontrados}

        texto_resultado, chunks = resultado_ferramenta
        chunks_encontrados.extend(chunks)
        mensagens.append({"role": "user", "content": texto_resultado})

    return {"resposta": "Não consegui concluir a tarefa dentro do número máximo de passos.", "chunks": []}
