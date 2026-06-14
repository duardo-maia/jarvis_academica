# ── Quiz / Active Recall — geração de perguntas e avaliação de respostas ──────

import sys
from pathlib import Path

from core.logging_config import get_logger

logger = get_logger(__name__)

# Aponta para banco_vetorial/recuperacao, onde está recuperar.py
_caminho_recuperacao = str(Path(__file__).parent.parent.parent / "banco_vetorial" / "recuperacao")
if _caminho_recuperacao not in sys.path:
    sys.path.insert(0, _caminho_recuperacao)

# Carregamento tardio: só importa (e carrega ChromaDB/BM25) na primeira chamada
_recuperar = None


def _modulo_recuperar():
    global _recuperar
    if _recuperar is None:
        import recuperar
        _recuperar = recuperar
    return _recuperar


def gerar_pergunta(topico: str, perguntas_anteriores: list[str] = None) -> dict:
    """Gera uma pergunta de active recall sobre `topico`, com base nos materiais indexados.

    `perguntas_anteriores` é a lista de perguntas já geradas no mesmo lote, usada para
    variar os trechos consultados e pedir ao modelo que não repita as perguntas.
    """
    recuperar = _modulo_recuperar()
    if perguntas_anteriores is None:
        perguntas_anteriores = []

    # Busca mais trechos do que o necessário e usa um pedaço diferente em cada
    # pergunta do lote, para reduzir a chance de perguntas parecidas/repetidas.
    chunks = recuperar.recuperar_hibrido(topico, k=20)
    inicio = (len(perguntas_anteriores) * 5) % len(chunks)
    chunks_selecionados = chunks[inicio:inicio + 5]
    if len(chunks_selecionados) < 5:
        chunks_selecionados += chunks[:5 - len(chunks_selecionados)]
    contexto = "\n\n".join(c["text"] for c in chunks_selecionados)

    aviso_repeticao = ""
    if perguntas_anteriores:
        lista_perguntas = "\n".join(f"- {p}" for p in perguntas_anteriores)
        aviso_repeticao = f"""
IMPORTANTE: o aluno já recebeu as perguntas abaixo. Sua nova pergunta deve ser
sobre um aspecto diferente do tópico, sem repetir ou parafrasear nenhuma delas:
{lista_perguntas}

"""

    prompt = f"""Com base nos trechos abaixo sobre o tópico "{topico}", gere UMA pergunta
dissertativa curta para testar o entendimento do aluno (active recall), e a resposta
esperada (resumida em 1 ou 2 frases).
{aviso_repeticao}
Responda EXATAMENTE neste formato, sem mais nada:
PERGUNTA: <sua pergunta>
RESPOSTA_ESPERADA: <resposta esperada>

Trechos:
{contexto}"""

    resposta = recuperar.llm.chat.completions.create(
        model=recuperar.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
    )
    texto = resposta.choices[0].message.content

    pergunta, resposta_esperada = _separar_pergunta_e_resposta(texto)
    logger.info("Pergunta gerada para o tópico %r", topico)
    return {"topico": topico, "pergunta": pergunta, "resposta_esperada": resposta_esperada}


def _separar_pergunta_e_resposta(texto: str) -> tuple[str, str]:
    """Separa o texto gerado pelo Gemma em pergunta e resposta esperada."""
    if "PERGUNTA:" in texto and "RESPOSTA_ESPERADA:" in texto:
        antes, depois = texto.split("RESPOSTA_ESPERADA:", 1)
        pergunta = antes.split("PERGUNTA:", 1)[1].strip()
        resposta_esperada = depois.strip()
        return pergunta, resposta_esperada

    logger.warning("Formato inesperado ao gerar pergunta: %s", texto)
    return texto.strip(), ""


def avaliar_resposta(pergunta: str, resposta_esperada: str, resposta_usuario: str) -> dict:
    """Avalia a resposta do usuário (0-10) com feedback, comparando com a resposta esperada."""
    recuperar = _modulo_recuperar()

    prompt = f"""Você está avaliando a resposta de um aluno num exercício de active recall.

Pergunta: {pergunta}
Resposta esperada (referência): {resposta_esperada}
Resposta do aluno: {resposta_usuario}

Avalie a resposta do aluno com uma nota de 0 a 10 e dê um feedback breve e construtivo
em português brasileiro, indicando o que está correto e o que falta ou está incorreto.

Seja rigoroso na nota, seguindo estes critérios:
- 0: resposta vazia, sem relação com a pergunta, ou completamente incorreta.
- 1 a 4: resposta com pouca relação ou que aborda só um detalhe secundário, sem
  explicar o conceito principal perguntado.
- 5 a 7: resposta correta na ideia geral, mas incompleta ou imprecisa.
- 8 a 10: resposta correta e completa, cobrindo os pontos principais da resposta esperada.

Responda EXATAMENTE neste formato, sem mais nada:
NOTA: <0 a 10>
FEEDBACK: <seu feedback>"""

    resposta = recuperar.llm.chat.completions.create(
        model=recuperar.llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = resposta.choices[0].message.content

    nota, feedback = _separar_nota_e_feedback(texto)
    logger.info("Resposta avaliada com nota %d", nota)
    return {"nota": nota, "feedback": feedback}


def _separar_nota_e_feedback(texto: str) -> tuple[int, str]:
    """Separa o texto gerado pelo Gemma em nota (0-10) e feedback."""
    if "NOTA:" in texto and "FEEDBACK:" in texto:
        antes, depois = texto.split("FEEDBACK:", 1)
        nota_texto = antes.split("NOTA:", 1)[1].strip()
        try:
            nota = int(nota_texto.split()[0])
        except (ValueError, IndexError):
            nota = 5
        nota = max(0, min(10, nota))
        return nota, depois.strip()

    logger.warning("Formato inesperado ao avaliar resposta: %s", texto)
    return 5, texto.strip()
