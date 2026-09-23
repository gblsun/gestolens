"""Classificadores de rosto: exercícios 4 e 5 e a extensão de pose.

- Ex4 `classificar_boca`: boca aberta ou fechada, com a proporção altura/largura.
- Ex5 `classificar_direcao_rosto`: de frente ou virado para a esquerda/direita da imagem.
- Extensão do Ex5 `estimar_pose`: yaw, pitch e roll a partir da matriz facial.

Índices usados (ver docs/Conceitos/Landmarks do rosto.md): 13/14 lábios internos,
61/291 cantos da boca, 33/263 cantos externos dos olhos, 1 ponta do nariz.

Documentação: docs/Módulos/rosto.md
"""

import math

import numpy as np

from .. import config
from ..geometria import distancia

BOCA_ABERTA = "Boca aberta"
BOCA_FECHADA = "Boca fechada"
BOCA_INDEFINIDA = "Boca indefinida"

ROSTO_FRENTE = "Rosto de frente"
ROSTO_ESQUERDA = "Rosto virado p/ esquerda da imagem"
ROSTO_DIREITA = "Rosto virado p/ direita da imagem"
DIRECAO_INDEFINIDA = "Direcao indefinida"
ROSTO_NAO_DETECTADO = "Rosto nao detectado"

# Índices do Face Landmarker (mesma topologia do Face Mesh).
LABIO_SUPERIOR, LABIO_INFERIOR = 13, 14
CANTO_BOCA_ESQ, CANTO_BOCA_DIR = 61, 291
OLHO_CANTO_EXT_1, OLHO_CANTO_EXT_2 = 33, 263
PONTA_NARIZ = 1


def classificar_boca(lm, aspecto: float = 1.0) -> tuple[str, float]:
    """Exercício 4: boca aberta ou fechada.

    proporção = dist(13, 14) / dist(61, 291). Dividir pela largura da boca
    reduz (sem eliminar) o efeito da distância à câmera.

    Parâmetros:
        lm: 478 landmarks do rosto.
        aspecto: largura / altura da imagem. Sem essa correção, em vídeo retrato
            a largura sairia subestimada e a proporção, inflada.

    Retorna:
        (rótulo, proporção). A proporção é exibida no vídeo para calibrar `LIMIAR_BOCA_ABERTA`.
    """
    altura = distancia(lm[LABIO_SUPERIOR], lm[LABIO_INFERIOR], aspecto)
    largura = distancia(lm[CANTO_BOCA_ESQ], lm[CANTO_BOCA_DIR], aspecto)
    if largura < 1e-6:
        return BOCA_INDEFINIDA, 0.0
    proporcao = altura / largura
    rotulo = BOCA_ABERTA if proporcao > config.LIMIAR_BOCA_ABERTA else BOCA_FECHADA
    return rotulo, proporcao


def classificar_direcao_rosto(lm) -> tuple[str, float]:
    """Exercício 5: direção do rosto pela posição do nariz entre os olhos.

    desvio = (x[1] − centro dos olhos) / distância entre os olhos.

    Os rótulos descrevem a direção **na imagem exibida**, então continuam
    corretos com ou sem espelhamento. Quando |desvio| fica a até
    `FAIXA_INDEFINIDA_DIRECAO` do `LIMIAR_DIRECAO`, o resultado é "Direcao indefinida".

    Parâmetros:
        lm: 478 landmarks do rosto. Não precisa do aspecto: o desvio é uma razão
            entre duas medidas no eixo x.

    Retorna:
        (rótulo, desvio). Desvio negativo = nariz à esquerda do centro na imagem.
    """
    olho_a, olho_b, nariz = lm[OLHO_CANTO_EXT_1], lm[OLHO_CANTO_EXT_2], lm[PONTA_NARIZ]
    centro_x = (olho_a.x + olho_b.x) / 2
    distancia_olhos = abs(olho_b.x - olho_a.x)
    if distancia_olhos < 1e-6:
        return DIRECAO_INDEFINIDA, 0.0

    desvio = (nariz.x - centro_x) / distancia_olhos
    limiar, faixa = config.LIMIAR_DIRECAO, config.FAIXA_INDEFINIDA_DIRECAO
    if abs(abs(desvio) - limiar) <= faixa:
        return DIRECAO_INDEFINIDA, desvio
    if desvio < -limiar:
        return ROSTO_ESQUERDA, desvio
    if desvio > limiar:
        return ROSTO_DIREITA, desvio
    return ROSTO_FRENTE, desvio


def estimar_pose(matriz: np.ndarray | None) -> tuple[float, float, float] | None:
    """Extensão do Exercício 5: yaw, pitch e roll da cabeça, em graus.

    A matriz 4x4 do Face Landmarker leva o modelo canônico de rosto para o
    espaço da câmera; o bloco 3x3 é a rotação R. Decomposição de Euler:

        yaw   = atan2(R02, R22)   girar para os lados
        pitch = asin(−R12)        olhar para cima/baixo
        roll  = atan2(R10, R11)   inclinar para o ombro

    Os sinais dependem da convenção do MediaPipe: calibre olhando para cada
    lado e anote o sinal observado (em IMG_7461, virar para a esquerda da imagem ≈ yaw negativo).

    Parâmetros:
        matriz: matriz 4x4 ou None.

    Retorna:
        (yaw, pitch, roll), ou None se não houver matriz.
    """
    if matriz is None:
        return None
    r = np.asarray(matriz)[:3, :3]
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, -r[1, 2]))))
    yaw = math.degrees(math.atan2(r[0, 2], r[2, 2]))
    roll = math.degrees(math.atan2(r[1, 0], r[1, 1]))
    return yaw, pitch, roll
