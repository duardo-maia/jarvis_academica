import sqlite3
from pathlib import Path

pasta = Path(__file__).parent

conn = sqlite3.connect(pasta / "agenda_jarvis.db")
cursor = conn.cursor()

with open(pasta / "schema.sql", "r", encoding="utf-8") as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()

print("Banco criado com sucesso!")