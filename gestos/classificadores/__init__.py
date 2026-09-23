"""Classificadores geométricos (regras heurísticas) para mãos e rosto.

    maos.py   Ex1 estado da mão · Ex2 contagem de dedos · Ex3 polegar
    rosto.py  Ex4 boca · Ex5 direção do rosto · pose (yaw, pitch, roll)

As regras são ilustradas em gestos/classificadores/README.md.
"""

from .maos import classificar_mao, classificar_polegar, contar_dedos
from .rosto import classificar_boca, classificar_direcao_rosto, estimar_pose

__all__ = [
    "contar_dedos",
    "classificar_mao",
    "classificar_polegar",
    "classificar_boca",
    "classificar_direcao_rosto",
    "estimar_pose",
]
