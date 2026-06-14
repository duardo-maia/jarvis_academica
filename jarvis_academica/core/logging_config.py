# ── Configuração centralizada de logging ──────────────────────────────────────

import logging
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(nome: str) -> logging.Logger:
    """Retorna um logger configurado com saída em arquivo (logs/jarvis.log) e console."""
    logger = logging.getLogger(nome)
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        arquivo = logging.FileHandler(LOG_DIR / "jarvis.log", encoding="utf-8")
        arquivo.setFormatter(formatter)
        logger.addHandler(arquivo)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

        logger.setLevel(logging.INFO)
    return logger
