# ── Casos de teste para avaliação do sistema (RAG + agente completo) ──────────

CASOS_RAG = [
    {"pergunta": "O que é um embedding e para que ele é usado em IA?", "tipo": "rag"},
    {"pergunta": "O que é Processamento de Linguagem Natural (PLN)?", "tipo": "rag"},
    {"pergunta": "O que é RAG (Retrieval-Augmented Generation) e como ele funciona?", "tipo": "rag"},
    {"pergunta": "O que é um banco de dados vetorial e para que serve?", "tipo": "rag"},
    {"pergunta": "O que é a arquitetura Transformer e qual o papel do mecanismo de atenção?", "tipo": "rag"},
    {"pergunta": "O que é um LLM (Large Language Model)?", "tipo": "rag"},
    {"pergunta": "Explique o experimento mental do Quarto Chinês.", "tipo": "rag"},
    {"pergunta": "O que é viés algorítmico (viés da IA) e por que ele ocorre?", "tipo": "rag"},
    {"pergunta": "O que é Deep Learning e como se relaciona com redes neurais profundas?", "tipo": "rag"},
    {"pergunta": "O que é Aprendizado de Máquina (Machine Learning)?", "tipo": "rag"},
]

CASOS_AGENTE = [
    {
        "pergunta": "O que tenho hoje?",
        "tipo": "agente",
        "ferramentas_esperadas": ["PRIORIDADES_HOJE"],
    },
    {
        "pergunta": "Tenho prova amanhã?",
        "tipo": "agente",
        "ferramentas_esperadas": ["CONSULTAR_AGENDA"],
    },
    {
        "pergunta": "O que devo priorizar hoje?",
        "tipo": "agente",
        "ferramentas_esperadas": ["PRIORIDADES_HOJE"],
    },
    {
        "pergunta": "Quais são meus próximos compromissos?",
        "tipo": "agente",
        "ferramentas_esperadas": ["CONSULTAR_AGENDA"],
    },
    {
        "pergunta": "Quais tarefas pendentes eu tenho?",
        "tipo": "agente",
        "ferramentas_esperadas": ["LISTAR_TAREFAS"],
    },
    {
        "pergunta": "Adicione uma tarefa de revisão de RAG com prioridade alta",
        "tipo": "agente",
        "ferramentas_esperadas": ["ADICIONAR_TAREFA"],
        "limpar_apos": True,
    },
    {
        "pergunta": "Monte um plano de estudos para a prova",
        "tipo": "agente",
        "ferramentas_esperadas": ["PLANO_ESTUDOS"],
    },
    {
        "pergunta": "Monte um plano de estudos sobre APSO",
        "tipo": "agente",
        "ferramentas_esperadas": [],
        "caso_adversarial": "scope_conflation_fabricacao",
    },
]

CASOS_TESTE = CASOS_RAG + CASOS_AGENTE
