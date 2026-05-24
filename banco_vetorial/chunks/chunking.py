# ── ETAPA 2: Chunking dos textos em Markdown ──────────────────────────────────
# Estratégia escolhida: janela deslizante com sobreposição

from pathlib import Path
import json

pasta_markdown = Path(__file__).parent.parent / "docs" / "markdown"
arquivo_saida  = Path(__file__).parent / "chunks.json"


def chunking_janela(texto, tamanho=500, sobreposicao=100):
    if sobreposicao >= tamanho:
        raise ValueError(
            f"sobreposicao ({sobreposicao}) deve ser menor que tamanho ({tamanho})"
        )
    chunks = []
    passo = tamanho - sobreposicao
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio += passo
    return chunks


# ── Lê cada Markdown e aplica o chunking 
markdowns = list(pasta_markdown.glob("*.md"))
print(f"Encontrados {len(markdowns)} arquivos Markdown.\n")

# Aqui vão parar todos os chunks de todos os documentos
chunks = []

for md_file in markdowns:
    print("═" * 60)
    print(f"Arquivo: {md_file.name}")

    # Lê o texto completo do Markdown
    texto = md_file.read_text(encoding="utf-8")

    # Aplica a função de chunking
    chunks_do_arquivo = chunking_janela(texto)

    print(f"Total de chunks gerados: {len(chunks_do_arquivo)}")
    print()
    print("PRÉVIA DO PRIMEIRO CHUNK:")
    print(chunks_do_arquivo[0][:300])
    print()

    # Monta os dicionários com id, texto e origem do documento
    # O 'source' guarda o nome do arquivo sem extensão para saber de onde veio
    for i, chunk in enumerate(chunks_do_arquivo):
        chunks.append({
            "id":     f"{md_file.stem}-chunk-{i}",
            "text":   chunk,
            "source": md_file.stem,
        })

# ── Salva todos os chunks num arquivo JSON ─────────────────────────────────────

arquivo_saida.write_text(
    json.dumps(chunks, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("═" * 60)
print(f"Total geral de chunks: {len(chunks)}")
print(f"Chunks salvos em: {arquivo_saida}")