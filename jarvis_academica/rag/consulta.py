import sys
from pathlib import Path

# Aponta para banco_vetorial/recuperacao onde está o módulo recuperar.py
_caminho_recuperacao = str(Path(__file__).parent.parent.parent / "banco_vetorial" / "recuperacao")
if _caminho_recuperacao not in sys.path:
    sys.path.insert(0, _caminho_recuperacao)

# Carregamento tardio: só importa (e carrega ChromaDB/BM25) na primeira chamada
_gerar_resposta = None


def consultar_documentos(pergunta: str) -> str:
    """Busca nos documentos acadêmicos indexados e retorna uma resposta gerada pelo modelo."""
    global _gerar_resposta
    if _gerar_resposta is None:
        from recuperar import gerar_resposta  # executa o carregamento dos índices aqui
        _gerar_resposta = gerar_resposta
    return _gerar_resposta(pergunta)
