# ── Constantes compartilhadas entre app.py, agente, plano de estudos e quiz ───

# Tópicos de IA indexados no banco vetorial, com palavras-chave usadas para
# detectar relação com tarefas/eventos da agenda (plano de estudos) e para
# selecionar tópicos no quiz.
TOPICOS_IA = {
    "Embedding": ["embedding", "embeddings", "vetor de palavras"],
    "PLN": ["pln", "processamento de linguagem natural", "nlp"],
    "RAG": ["rag", "retrieval-augmented generation", "recuperação aumentada", "busca híbrida"],
    "Banco Vetorial": ["banco vetorial", "vector database", "chromadb", "busca vetorial"],
    "Transformers": ["transformer", "transformers", "atenção", "attention"],
    "LLM": ["llm", "large language model", "modelo de linguagem"],
    "Quarto Chinês": ["quarto chinês", "chinese room"],
    "Viés da IA": ["viés", "bias", "viés algorítmico", "viés da ia"],
    "Deep Learning": ["deep learning", "rede neural profunda", "redes neurais"],
    "Aprendizado de Máquina": ["aprendizado de máquina", "machine learning"],
}

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

SUGESTOES_ESTUDO = [
    "Monte um plano de estudos para a prova",
    "O que devo priorizar hoje?",
    "O que devo revisar?",
]
