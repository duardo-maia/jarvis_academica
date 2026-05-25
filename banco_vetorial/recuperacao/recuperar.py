# ── ETAPA 4: Recuperação e Geração (RAG) 
# Busca híbrida: BM25 (léxica) + ChromaDB (semântica) → resposta com Gemma

import pickle
import numpy as np
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from openai import OpenAI

# Caminhos
data_path = Path(__file__).parent.parent / "data"
bm25_path = Path(__file__).parent.parent / "indexacao" / "bm25_index.pkl"

# Configuração do LLM Gemma
gemma_base_url = "https://llm.liaufms.org/v1/gemma-3-12b-it"
gemma_api_key  = "Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A"
gemma_model    = "google/gemma-3-12b-it"

# ── Carrega o índice BM25 
with open(bm25_path, "rb") as f:
    dados_bm25 = pickle.load(f)

indice_bm25 = dados_bm25["bm25"]
ids_chunks  = dados_bm25["ids"]
textos      = dados_bm25["texts"]

# ── Conecta ao ChromaDB e extrai os embeddings 
ef = DefaultEmbeddingFunction()

client_chroma = chromadb.PersistentClient(path=str(data_path))
collection    = client_chroma.get_collection(name="documentos", embedding_function=ef)

# Extrai todos os embeddings para calcular o scores
dados      = collection.get(include=["embeddings"])
matriz_emb = np.array(dados["embeddings"], dtype="float32")

# Normaliza as linhas 
normas     = np.linalg.norm(matriz_emb, axis=1, keepdims=True)
matriz_emb = matriz_emb / np.where(normas == 0, 1, normas)

# ── Client do Gemma 
gemma = OpenAI(base_url=gemma_base_url, api_key=gemma_api_key)

print("Índices carregados! Pronto para buscar.\n")


# ── Funções auxiliares 

def tokenizar(texto):
    return texto.lower().split()


def normalizar(v):
    """Normaliza um vetor para o intervalo [0, 1]."""
    v     = np.array(v, dtype="float32")
    delta = float(v.max() - v.min())
    if delta < 1e-9:
        return np.zeros_like(v)
    return (v - v.min()) / delta


# ── Funções de Retrieval 

def recuperar_bm25(pergunta, k=3):
    """Busca léxica: pontua chunks pela frequência dos termos da pergunta."""
    scores = indice_bm25.get_scores(tokenizar(pergunta))
    idx    = np.argsort(scores)[::-1][:k]
    return [{"id": ids_chunks[i], "text": textos[i], "score": float(scores[i])} for i in idx]


def recuperar_dense(pergunta, k=3):
    """Busca semântica: encontra chunks com significado similar à pergunta."""
    resultados = collection.query(query_texts=[pergunta], n_results=k)
    return [
        {
            "id":    resultados["ids"][0][i],
            "text":  resultados["documents"][0][i],
            "score": 1 - resultados["distances"][0][i],  # distância → similaridade
        }
        for i in range(len(resultados["ids"][0]))
    ]


def recuperar_hibrido(pergunta, k=5, alpha=0.6):
    """
    Combina BM25 e busca semântica.
    alpha = peso do semântico (0 = só BM25, 1 = só semântico, 0.6 = padrão)
    """
    # Score léxico (BM25) para todos os chunks
    sb = normalizar(indice_bm25.get_scores(tokenizar(pergunta)))

    # Score semântico para todos os chunks via produto vetorial
    vetor_pergunta = np.array(ef([pergunta])[0], dtype="float32")
    norma          = np.linalg.norm(vetor_pergunta)
    vetor_pergunta = vetor_pergunta / (norma if norma > 0 else 1)
    sd = normalizar(np.dot(matriz_emb, vetor_pergunta))

    # Combina os scores
    score_final = alpha * sd + (1.0 - alpha) * sb
    idx         = np.argsort(score_final)[::-1][:k]

    return [{"id": ids_chunks[i], "text": textos[i], "score": float(score_final[i])} for i in idx]


# ── Geração com Gemma

def diversificar(chunks, max_por_fonte=2):
    """Garante no máximo 2 chunks por documento, forçando variedade de fontes."""
    contagem = {}
    resultado = []
    for c in chunks:
        fonte = c["id"].rsplit("-chunk-", 1)[0]
        if contagem.get(fonte, 0) < max_por_fonte:
            contagem[fonte] = contagem.get(fonte, 0) + 1
            resultado.append(c)
    return resultado


def gerar_resposta(pergunta, k=10, alpha=0.6):
    """Recupera os chunks mais relevantes e gera uma resposta com o Gemma."""
    candidatos        = recuperar_hibrido(pergunta, k=k, alpha=alpha)
    chunks_relevantes = diversificar(candidatos)

    # Exibe os chunks recuperados no log para verificação
    print(f"\n[Chunks recuperados — {len(chunks_relevantes)} trechos]")
    for i, c in enumerate(chunks_relevantes, 1):
        fonte = c["id"].rsplit("-chunk-", 1)[0]
        print(f"\n  {i}. {fonte}  (score: {c['score']:.3f})")
        print(f"     {c['text'][:300].replace(chr(10), ' ')}...")
    print()

    # Agrupa os trechos por documento de origem
    trechos = []
    for c in chunks_relevantes:
        fonte = c["id"].rsplit("-chunk-", 1)[0]
        trechos.append(f"Documento: {fonte}\n{c['text']}")

    contexto = "\n\n---\n\n".join(trechos)

    prompt = f"""Você é um assistente especializado em inteligência artificial.
Responda de forma detalhada em texto corrido, sem listas, sem tópicos e sem citar os documentos de origem.
Quando as informações vierem de fontes diferentes, integre tudo numa resposta fluida e coesa.
Se a informação não estiver nos trechos, diga que não encontrou.

Trechos:

{contexto}

Pergunta: {pergunta}
Resposta:"""

    resposta = gemma.chat.completions.create(
        model=gemma_model,
        messages=[{"role": "user", "content": prompt}],
    )

    return resposta.choices[0].message.content, chunks_relevantes


# ── Teste 

if __name__ == "__main__":
    pergunta = input("Digite sua pergunta: ")

    resposta, _ = gerar_resposta(pergunta)
    print()
    print("── Resposta ──")
    print(resposta)
