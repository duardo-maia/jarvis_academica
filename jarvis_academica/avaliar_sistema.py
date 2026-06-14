# ── Avaliação do sistema RAG — gera relatório com pergunta, documentos
# recuperados, resposta e espaço para classificação manual ───────────────────

from dotenv import load_dotenv
load_dotenv()

from rag.consulta import consultar_documentos

PERGUNTAS = [
    "O que é um embedding e para que ele é usado em IA?",
    "O que é Processamento de Linguagem Natural (PLN)?",
    "O que é RAG (Retrieval-Augmented Generation) e como ele funciona?",
    "O que é um banco de dados vetorial e para que serve?",
    "O que é a arquitetura Transformer e qual o papel do mecanismo de atenção?",
    "O que é um LLM (Large Language Model)?",
    "Explique o experimento mental do Quarto Chinês.",
    "O que é viés algorítmico (viés da IA) e por que ele ocorre?",
    "O que é Deep Learning e como se relaciona com redes neurais profundas?",
    "O que é Aprendizado de Máquina (Machine Learning)?",
]

arquivo = open("resultados_avaliacao.md", "w", encoding="utf-8")
arquivo.write("# Avaliação do sistema — RAG\n\n")

numero = 1
for pergunta in PERGUNTAS:
    print(f"[{numero}/{len(PERGUNTAS)}] {pergunta}")
    resposta, chunks = consultar_documentos(pergunta)

    arquivo.write(f"## {numero}. {pergunta}\n\n")

    arquivo.write("**Documentos recuperados:**\n\n")
    if len(chunks) == 0:
        arquivo.write("- Nenhum documento recuperado.\n")
    else:
        for chunk in chunks:
            fonte = chunk["id"].rsplit("-chunk-", 1)[0]
            arquivo.write(f"- {fonte} (score: {chunk['score']:.3f})\n")
    arquivo.write("\n")

    arquivo.write("**Resposta:**\n\n")
    arquivo.write(resposta + "\n\n")

    arquivo.write("**Classificação:** _(a preencher: correta / parcialmente correta / incorreta)_\n\n")
    arquivo.write("---\n\n")

    numero = numero + 1

arquivo.close()
print("\nRelatório gerado em: resultados_avaliacao.md")
