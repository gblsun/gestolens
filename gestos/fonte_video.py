"""Fontes de quadros: arquivos de vídeo gravados, pastas de vídeos ou webcam.

Papel no fluxo
--------------
Primeira etapa do pipeline: entrega quadros BGR, cada um com um instante em
milissegundos. O modo VIDEO do MediaPipe Tasks exige esse instante e ele precisa
ser estritamente crescente.

- Arquivo: o instante vem do índice do quadro e do fps do arquivo. É
  determinístico e não depende da velocidade do processamento.
- Webcam: o instante vem do relógio (`time.monotonic`), porque o fps real da
  câmera varia com luz e carga da CPU.

Documentação: docs/Módulos/fonte_video.md
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2

from . import config


@dataclass
class Quadro:
    """Um quadro lido da fonte.

    Atributos:
        indice: posição do quadro (0, 1, 2, ...).
        timestamp_ms: instante do quadro em milissegundos, estritamente crescente.
        imagem: matriz BGR (altura x largura x 3) do OpenCV.
    """

    indice: int
    timestamp_ms: int
    imagem: "cv2.typing.MatLike"


def listar_videos(entrada: Path) -> list[Path]:
    """Lista os vídeos a processar.

    Parâmetros:
        entrada: um arquivo de vídeo ou uma pasta.

    Retorna:
        Lista ordenada de caminhos. Com um arquivo, a lista tem só ele. Com uma
        pasta, entram os arquivos cujas extensões estão em `config.EXTENSOES_VIDEO`.

    Levanta:
        FileNotFoundError: se `entrada` não existir.
    """
    if entrada.is_file():
        return [entrada]
    if entrada.is_dir():
        return sorted(p for p in entrada.iterdir() if p.suffix.lower() in config.EXTENSOES_VIDEO)
    raise FileNotFoundError(f"Entrada não encontrada: {entrada}")


class FonteVideo:
    """Lê quadros de um arquivo de vídeo ou da webcam.

    Parâmetros:
        origem: caminho do arquivo (`Path`) ou índice da webcam (`int`, normalmente 0).

    Atributos:
        nome: nome curto usado nos arquivos de saída (nome do arquivo sem extensão, ou "webcam").
        eh_webcam: True quando a origem é uma câmera ao vivo.
        fps: quadros por segundo informados pela fonte (30 quando a fonte não informa).
        total_quadros: total de quadros do arquivo (0 na webcam).

    Para arquivos .MOV de celular, o OpenCV aplica automaticamente a rotação
    guardada nos metadados (`CAP_PROP_ORIENTATION_AUTO`). Por isso vídeos em
    retrato não saem deitados.

    Pode ser usado como gerenciador de contexto (`with FonteVideo(...) as fonte:`).
    """

    def __init__(self, origem: Path | int):
        self.origem = origem
        self.eh_webcam = isinstance(origem, int)
        self.nome = "webcam" if self.eh_webcam else Path(origem).stem
        self.captura = cv2.VideoCapture(origem if self.eh_webcam else str(origem))
        if not self.captura.isOpened():
            dica = " Verifique se a câmera está conectada e livre." if self.eh_webcam else ""
            raise RuntimeError(f"Não foi possível abrir a fonte de vídeo: {origem}.{dica}")
        self.captura.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
        fps = self.captura.get(cv2.CAP_PROP_FPS)
        self.fps = fps if fps and fps > 1 else 30.0
        self.total_quadros = 0 if self.eh_webcam else int(self.captura.get(cv2.CAP_PROP_FRAME_COUNT))

    def quadros(self) -> Iterator[Quadro]:
        """Itera os quadros até o fim do arquivo (ou até a webcam parar de responder).

        Retorna:
            Gerador de `Quadro` com `timestamp_ms` estritamente crescente.
        """
        indice = 0
        ultimo_ts = -1
        inicio = time.monotonic()
        while True:
            sucesso, imagem = self.captura.read()
            if not sucesso:
                break
            if self.eh_webcam:
                ts = int((time.monotonic() - inicio) * 1000)
            else:
                ts = int(round(indice * 1000.0 / self.fps))
            # Nunca repetir um instante: o MediaPipe rejeita timestamps iguais.
            ts = max(ts, ultimo_ts + 1)
            ultimo_ts = ts
            yield Quadro(indice, ts, imagem)
            indice += 1

    def fechar(self) -> None:
        """Libera o arquivo ou a câmera."""
        self.captura.release()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.fechar()
