# ── ETAPA 1: Converter PDFs para Markdown ─────────────────────────────────────

from pathlib import Path
from docling.document_converter import DocumentConverter

# Pastas de entrada e saída, sempre relativas a este arquivo
pasta_pdfs     = Path(__file__).parent / "pdfs"
pasta_markdown = Path(__file__).parent / "markdown"

# Cria a pasta de saída se ela não existir
pasta_markdown.mkdir(parents=True, exist_ok=True)

# O DocumentConverter do Docling lida com PDFs
converter = DocumentConverter()

# Busca todos os arquivos .pdf dentro da pasta
pdfs = list(pasta_pdfs.glob("*.pdf"))
print(f"Encontrados {len(pdfs)} arquivos PDF.\n")

# ── Converte cada PDF para Markdown
for pdf_file in pdfs:
    print("═" * 60)
    print(f"Convertendo: {pdf_file.name}")

    # O Docling retorna um objeto 'DoclingDocument'.
    # O método export_to_markdown() entrega o texto estruturado.
    resultado = converter.convert(str(pdf_file))
    texto_markdown = resultado.document.export_to_markdown()

    # Salva o Markdown na pasta de destino com o mesmo nome do PDF
    # Usamos Path.with_suffix() para trocar .pdf por .md automaticamente
    caminho_md = pasta_markdown / pdf_file.with_suffix(".md").name
    caminho_md.write_text(texto_markdown, encoding="utf-8")

    print(f"Markdown salvo em: {caminho_md}")
    print(f"Total de caracteres: {len(texto_markdown):,}")
    print()
    print("PRÉVIA DOS PRIMEIROS 1000 CARACTERES:")
    print("═" * 60)
    print(texto_markdown[:1000])
    print()
