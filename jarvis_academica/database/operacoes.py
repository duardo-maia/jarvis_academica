# ── Banco de dados — conexão e utilitários genéricos compartilhados ───────────
# tarefas.py e agenda.py importam _conectar() daqui; este módulo não conhece
# as tabelas específicas de cada um.

import sqlite3
from pathlib import Path

from core.logging_config import get_logger

logger = get_logger(__name__)

DB_PATH     = Path(__file__).parent / "agenda_jarvis.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# Cria o banco automaticamente se ainda não existir
if not DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()
    logger.info("Banco criado com sucesso em %s", DB_PATH)


def _conectar() -> sqlite3.Connection:
    """Abre uma conexão com o banco, já com acesso a colunas por nome (Row)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def executar_sql(sql: str) -> str:
    """Executa qualquer SQL e retorna o resultado como texto."""
    conn = _conectar()
    cursor = conn.cursor()
    try:
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        resultado = ""
        for stmt in statements:
            cursor.execute(stmt)
            tipo = stmt.strip().upper().split()[0]
            if tipo == "SELECT":
                rows = cursor.fetchall()
                if not rows:
                    resultado += "Nenhum registro encontrado.\n"
                else:
                    cols = rows[0].keys()
                    resultado += " | ".join(cols) + "\n"
                    resultado += "-" * 60 + "\n"
                    for row in rows:
                        resultado += " | ".join(str(v) if v is not None else "" for v in row) + "\n"
            else:
                conn.commit()
                resultado += f"Operação executada com sucesso. Linhas afetadas: {cursor.rowcount}\n"
        return resultado.strip()
    except Exception as e:
        logger.error("Erro ao executar SQL %r: %s", sql, e)
        return f"ERRO: {e}"
    finally:
        conn.close()


def get_schema() -> str:
    """Retorna o esquema do banco para o modelo entender a estrutura."""
    conn = _conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    schema = ""
    for name, ddl in tables:
        schema += f"\n-- Tabela: {name}\n{ddl}\n"
    return schema
