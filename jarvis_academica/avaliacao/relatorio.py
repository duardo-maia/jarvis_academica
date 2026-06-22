# ── Geração do relatório de avaliação — preserva classificações já feitas ─────
# manualmente em execuções anteriores, antes de sobrescrever o arquivo.

import re

PLACEHOLDER = "_(a preencher: correta / parcialmente correta / incorreta)_"

_PADRAO_BLOCO = re.compile(
    r"^## \d+\. (.+?)\n.*?\*\*Classifica[cç][aã]o:\*\*[ \t]*(.*?)[ \t]*\n"
    r"(?:\n\*\*Justificativa:\*\*[ \t]*(.*?)[ \t]*\n)?",
    re.DOTALL | re.MULTILINE,
)


def carregar_classificacoes_antigas(caminho: str) -> dict:
    """Lê um resultados_avaliacao.md já existente e retorna
    {pergunta: {"classificacao": str, "justificativa": str | None}} para toda
    pergunta cuja classificação já foi preenchida manualmente (não é o
    placeholder) — preserva também a Justificativa, se houver. Tolerante a
    espaços extras/finais já presentes no arquivo real."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except FileNotFoundError:
        return {}

    classificacoes = {}
    for match in _PADRAO_BLOCO.finditer(conteudo):
        pergunta = match.group(1).strip()
        classificacao = match.group(2).strip()
        justificativa = match.group(3).strip() if match.group(3) else None
        if classificacao and classificacao != PLACEHOLDER and "a preencher" not in classificacao:
            classificacoes[pergunta] = {"classificacao": classificacao, "justificativa": justificativa}
    return classificacoes


def _formatar_saida_passo(passo: dict, limite: int = 1000) -> str:
    """Mesma ideia do _formatar_saida_passo de app.py, mas com limite menor —
    aqui é um relatório estático pra ler, não uma UI interativa."""
    texto = passo.get("texto_resultado")
    if texto is None:
        texto = str(passo.get("saida"))
    return texto[:limite] + ("..." if len(texto) > limite else "")


def _linhas_classificacao(classificacao: str, justificativa: str = None) -> list:
    linhas = [f"**Classificação:** {classificacao}"]
    if justificativa:
        linhas += ["", f"**Justificativa:** {justificativa}"]
    return linhas


def renderizar_caso_rag(numero: int, caso: dict, resultado: dict, classificacao: str, justificativa: str = None) -> str:
    linhas = [f"## {numero}. {caso['pergunta']}\n", "**Documentos recuperados:**\n"]
    chunks = resultado["chunks"]
    if not chunks:
        linhas.append("- Nenhum documento recuperado.")
    else:
        for chunk in chunks:
            fonte = chunk["id"].rsplit("-chunk-", 1)[0]
            linhas.append(f"- {fonte} (score: {chunk['score']:.3f})")
    linhas += ["", "**Resposta:**\n", resultado["resposta"], ""]
    linhas += _linhas_classificacao(classificacao, justificativa)
    linhas += ["", "---", ""]
    return "\n".join(linhas)


def renderizar_caso_agente(
    numero: int, caso: dict, resultado: dict, avisos: list, classificacao: str, justificativa: str = None
) -> str:
    linhas = [f"## {numero}. {caso['pergunta']}\n"]
    if caso.get("caso_adversarial"):
        linhas.append(
            "> **Caso adversarial** — reproduz falha real documentada na Análise de "
            "Erros (não-determinismo conhecido; qualquer comportamento deve ser "
            "avaliado manualmente).\n"
        )
    linhas.append("**Ferramentas chamadas:**\n")
    passos = resultado["passos"]
    if not passos:
        linhas.append("- Nenhuma ferramenta chamada (resposta direta do modelo).")
    else:
        for p in passos:
            linhas.append(f"- `{p['ferramenta']}` — entrada: `{p['entrada']}`")
            linhas.append(f"  - saída: `{_formatar_saida_passo(p)}`")
    linhas += ["", "**Resposta:**\n", resultado["resposta"], ""]
    if avisos:
        linhas.append("**Verificação automática:** " + " / ".join(avisos))
    else:
        linhas.append("**Verificação automática:** nenhuma inconsistência detectada.")
    linhas += [""] + _linhas_classificacao(classificacao, justificativa) + ["", "---", ""]
    return "\n".join(linhas)
