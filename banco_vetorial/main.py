import chromadb
import uuid

client = chromadb.Client()

collection = client.create_collection(name="documentos")

with open("docs/documentos.txt", "r", encoding="utf-8") as f:
   documentos: list[str] =f.read().splitlines()


collection.add(
   ids=[str(uuid.uuid4()) for _ in documentos],
   documents=documentos,
   metadatas=[{"line": line} for line in range(len(documentos))]
)

print(collection.peek())