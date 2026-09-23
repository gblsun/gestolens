"""Garante que os arquivos de modelo (.task) do MediaPipe Tasks estejam disponíveis.

Na primeira execução, baixa `hand_landmarker.task` (~7,5 MB) e
`face_landmarker.task` (~3,6 MB) para a pasta `modelos/`. Nas execuções
seguintes, reaproveita os arquivos locais.

Documentação: docs/Módulos/modelos.md
"""

import urllib.request
from pathlib import Path

from . import config


def garantir_modelo(nome: str) -> Path:
    """Devolve o caminho local de um modelo, baixando-o se necessário.

    Parâmetros:
        nome: chave de `config.MODELOS` (ex.: "hand_landmarker.task").

    Retorna:
        Caminho do arquivo em `config.PASTA_MODELOS`.

    O download vai primeiro para um arquivo `.part` e só depois é renomeado.
    Assim, um download interrompido nunca deixa um modelo corrompido no lugar.
    """
    destino = config.PASTA_MODELOS / nome
    if destino.exists() and destino.stat().st_size > 0:
        return destino

    config.PASTA_MODELOS.mkdir(parents=True, exist_ok=True)
    url = config.MODELOS[nome]
    print(f"Baixando modelo {nome}...")
    temporario = destino.with_suffix(".part")
    urllib.request.urlretrieve(url, temporario)
    temporario.replace(destino)
    return destino
