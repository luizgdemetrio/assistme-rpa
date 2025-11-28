# src/utils/paths.py
import os
from pathlib import Path


def pasta_protocolo(protocolo: str) -> Path:
    base = Path(
        r"C:\Users\Luiz Gustavo\NEXCORP SER. TELECOMUNICAÇÕES S.A\Rodolfo Pollmann - Acionamentos PR\ASSISTME"
    )
    destino = base / protocolo
    destino.mkdir(parents=True, exist_ok=True)
    return destino
