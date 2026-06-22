# ── Análise de Erros — falhas reais encontradas e reproduzidas em sessão de
# desenvolvimento, documentadas com tipo, causa e possível solução ────────────

FALHAS = [
    {
        "tipo": "geração — instrução não seguida (placeholder literal)",
        "causa": (
            "O modelo às vezes copiava texto de exemplo entre `< >` do próprio "
            "system prompt (ex.: `<titulo>`) para dentro da RESPOSTA FINAL, em vez "
            "de substituir pelos dados reais retornados pela ferramenta."
        ),
        "solucao": (
            "Corrigido: guarda de regex em `rodar_agente` (agente/agente.py) detecta "
            r"`<[^<>\n]{2,40}>` em qualquer RESPOSTA FINAL e força um retry pedindo "
            "explicitamente que o modelo use dados reais."
        ),
        "status": "corrigida",
        "evidencia": "Reproduzido e corrigido em sessão de desenvolvimento (ver agente/agente.py, guarda de placeholder).",
    },
    {
        "tipo": "tool calling — loop infinito",
        "causa": (
            "Uma regra de prompt mais estrita, exigindo SEMPRE chamar PLANO_ESTUDOS "
            "antes de responder, levou o modelo a chamar repetidamente a mesma "
            "ferramenta até esgotar max_passos (7 chamadas), em vez de finalizar."
        ),
        "solucao": (
            "Revertida a regra mais estrita — o ganho de robustez não compensou o "
            "novo modo de falha (pior que o original). Tratado como limite atual "
            "aceito do design do loop ReAct deste agente."
        ),
        "status": "corrigida (revertendo a causa)",
        "evidencia": "Reproduzido e revertido em sessão de desenvolvimento (ver histórico de agente/agente.py).",
    },
    {
        "tipo": "ambiguidade / geração — conflito de escopo e fabricação não-determinística",
        "causa": (
            "Para a pergunta 'Monte um plano de estudos sobre APSO' (assunto real da "
            "agenda do usuário, mas sem nenhuma relação com TOPICOS_IA), o agente "
            "produziu três comportamentos diferentes em execuções distintas a "
            "temperature=0: (1) recusa correta sem chamar ferramenta; (2) fabricação "
            "completa de uma data de prova errada e uma tarefa inexistente, sem "
            "chamar nenhuma ferramenta; (3) chamada correta de PLANO_ESTUDOS, mas "
            "mistura de tópicos de IA (reais, mas irrelevantes) como se fossem "
            "conteúdo da prova de APSO."
        ),
        "solucao": (
            "NÃO corrigida — tentativas de reforçar a regra no prompt geraram um "
            "modo de falha pior (ver falha do loop infinito acima). Tratada como "
            "limitação conhecida do modelo de base; mitigada parcialmente por "
            "verificação automática determinística (avaliacao/verificacao.py) que "
            "sinaliza ids/datas/tópicos suspeitos no relatório, mas a classificação "
            "final permanece manual."
        ),
        "status": "conhecida, não corrigida",
        "evidencia": (
            "Reproduzida em sessão de desenvolvimento com o caso de teste adversarial "
            "'Monte um plano de estudos sobre APSO' (ver Avaliação do Sistema, caso de agente correspondente)."
        ),
    },
    {
        "tipo": "geração — instrução não seguida (placeholder literal, variante com colchetes)",
        "causa": (
            "Variante da Falha 1: em vez de copiar um placeholder entre `< >`, o "
            "modelo escreveu trechos como '[Detalhes dos próximos eventos conforme "
            "retornado pela PLANO_ESTUDOS]' — um placeholder com colchetes em vez de "
            "ângulos, que não é capturado pela guarda de regex existente (que só "
            "procura `<...>`)."
        ),
        "solucao": (
            "NÃO corrigida — descoberta ao rodar a suíte de avaliação estendida "
            "(caso adversarial da APSO). Para cobrir, a guarda de regex em "
            "`rodar_agente` precisaria reconhecer também o padrão `[...]` quando "
            "contém frases como 'conforme retornado' ou nomes de ferramentas em "
            "maiúsculas — não implementado por estar fora do escopo desta sessão "
            "(não tocar mais no prompt/guardrails do agente)."
        ),
        "status": "conhecida, não corrigida",
        "evidencia": (
            "Observada na execução do `avaliar_sistema.py` estendido, caso de teste "
            "adversarial 'Monte um plano de estudos sobre APSO' (ver Avaliação do "
            "Sistema, caso 18: resposta contém '[Detalhes dos próximos eventos "
            "conforme retornado pela PLANO_ESTUDOS]')."
        ),
    },
    {
        "tipo": "tool calling — preenchimento incorreto de parâmetros da ferramenta",
        "causa": (
            "Ao pedir para adicionar uma tarefa com prioridade alta via linguagem "
            "natural ('Adicione uma tarefa de revisão de RAG com prioridade alta'), "
            "o modelo montou o marcador [ADICIONAR_TAREFA: ...] colocando o texto "
            "'prioridade: alta' no campo de descrição em vez do campo de prioridade "
            "— a tarefa foi criada com prioridade 'normal' (valor padrão) e "
            "descrição 'prioridade: alta', e o próprio modelo percebeu o erro na "
            "resposta final, mas só depois de já ter chamado a ferramenta errada."
        ),
        "solucao": (
            "NÃO corrigida — descoberta ao rodar a suíte de avaliação estendida. "
            "Uma possível solução seria reforçar no prompt um exemplo explícito de "
            "como mapear atributos mencionados em linguagem natural (prioridade, "
            "descrição) para a posição correta dos argumentos separados por '|' no "
            "marcador [ADICIONAR_TAREFA: ...], mas não implementada por estar fora "
            "do escopo desta sessão."
        ),
        "status": "conhecida, não corrigida",
        "evidencia": (
            "Observada na execução do `avaliar_sistema.py` estendido, caso de teste "
            "'Adicione uma tarefa de revisão de RAG com prioridade alta' (ver "
            "Avaliação do Sistema, caso 16: ferramenta chamada com entrada "
            "{'descricao': 'prioridade: alta', 'prioridade': 'normal', ...})."
        ),
    },
]


def renderizar_analise_erros(falhas: list[dict]) -> str:
    linhas = ["# Análise de Erros\n"]
    for i, f in enumerate(falhas, 1):
        linhas += [
            f"## Falha {i}: {f['tipo']}\n",
            f"**Causa:** {f['causa']}\n",
            f"**Possível solução:** {f['solucao']}\n",
            f"**Status:** {f['status']}\n",
            f"**Evidência:** {f['evidencia']}\n",
            "---\n",
        ]
    return "\n".join(linhas)
