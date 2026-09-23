"""Sobreposição visual: landmarks, conexões e painel de classificações.

Desenha diretamente com OpenCV, porque `mp.solutions.drawing_utils` não existe
nas versões recentes do MediaPipe. Os textos ficam sem acento: `cv2.putText`
só renderiza ASCII.

Painel (canto superior esquerdo), de cima para baixo:
    vídeo, quadro e tempo
    [mao <lado>] estado | Dedos: n        (Ex1, Ex2) · cor por lado
       polegar (dif ±x.xx)                (Ex3)
    boca (prop x.xx)                      (Ex4)
    direção (desvio ±x.xx)                (Ex5)
    yaw / pitch / roll                    (extensão Ex5)

Documentação: docs/Módulos/desenho.md
"""

import cv2

from .analise import AnaliseQuadro
from .classificadores.maos import MAO_NAO_DETECTADA
from .classificadores.rosto import ROSTO_NAO_DETECTADO

# Conexões da mão (mesma topologia de HandLandmarksConnections do MediaPipe).
CONEXOES_MAO = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
]
PONTOS_ROSTO_USADOS = [1, 13, 14, 33, 61, 263, 291]

COR_TEXTO = (255, 255, 255)
COR_FUNDO = (0, 0, 0)
CORES_MAO = {"esquerda": (0, 200, 255), "direita": (0, 255, 0)}


def _px(ponto, largura, altura):
    """Converte um landmark normalizado em coordenadas de pixel (x, y)."""
    return int(ponto.x * largura), int(ponto.y * altura)


def desenhar_mao(imagem, landmarks, cor) -> None:
    """Desenha os 21 landmarks da mão e as 21 conexões do esqueleto.

    Parâmetros:
        imagem: quadro BGR, alterado no lugar.
        landmarks: 21 landmarks normalizados.
        cor: cor BGR das conexões (os pontos são sempre vermelhos).
    """
    h, w = imagem.shape[:2]
    for a, b in CONEXOES_MAO:
        cv2.line(imagem, _px(landmarks[a], w, h), _px(landmarks[b], w, h), cor, 2, cv2.LINE_AA)
    for ponto in landmarks:
        cv2.circle(imagem, _px(ponto, w, h), 4, (0, 0, 255), -1, cv2.LINE_AA)


def desenhar_rosto(imagem, landmarks) -> None:
    """Destaca apenas os landmarks do rosto usados nas regras (boca, olhos, nariz)."""
    h, w = imagem.shape[:2]
    for indice in PONTOS_ROSTO_USADOS:
        cv2.circle(imagem, _px(landmarks[indice], w, h), 4, (255, 0, 255), -1, cv2.LINE_AA)
    cv2.line(imagem, _px(landmarks[61], w, h), _px(landmarks[291], w, h), (255, 0, 255), 1)
    cv2.line(imagem, _px(landmarks[13], w, h), _px(landmarks[14], w, h), (255, 0, 255), 1)


def _texto(imagem, texto, y, cor=COR_TEXTO, escala=0.55) -> int:
    """Escreve uma linha de texto com fundo escuro, para ficar legível sobre qualquer cena.

    Retorna:
        A coordenada y da próxima linha.
    """
    (tw, th), base = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, 1)
    cv2.rectangle(imagem, (8, y - th - 6), (16 + tw, y + base), COR_FUNDO, -1)
    cv2.putText(imagem, texto, (12, y), cv2.FONT_HERSHEY_SIMPLEX, escala, cor, 1, cv2.LINE_AA)
    return y + th + 12


def desenhar_analise(imagem, analise: AnaliseQuadro, nome_video: str) -> None:
    """Desenha landmarks e o painel com todas as classificações do quadro.

    Parâmetros:
        imagem: quadro BGR, alterado no lugar.
        analise: resultado de `Analisador.analisar`.
        nome_video: nome exibido no topo do painel.
    """
    y = _texto(imagem, f"{nome_video}  quadro {analise.indice}  t={analise.timestamp_ms / 1000:.2f}s", 24)

    if not analise.maos:
        y = _texto(imagem, MAO_NAO_DETECTADA, y, (0, 0, 255))
    for mao in analise.maos:
        cor = CORES_MAO.get(mao.lado.split("_")[0], (255, 255, 0))
        desenhar_mao(imagem, mao.landmarks, cor)
        y = _texto(imagem, f"[mao {mao.lado}] {mao.estado} | Dedos: {mao.dedos}", y, cor)
        y = _texto(imagem, f"   {mao.polegar} (dif {mao.polegar_diferenca:+.2f})", y, cor)

    if analise.rosto is None:
        _texto(imagem, ROSTO_NAO_DETECTADO, y, (0, 0, 255))
        return
    rosto = analise.rosto
    desenhar_rosto(imagem, rosto.landmarks)
    y = _texto(imagem, f"{rosto.boca} (prop {rosto.proporcao_boca:.2f})", y, (255, 0, 255))
    y = _texto(imagem, f"{rosto.direcao} (desvio {rosto.desvio_nariz:+.2f})", y, (255, 255, 0))
    if rosto.yaw is not None:
        _texto(imagem, f"yaw {rosto.yaw:+.0f}  pitch {rosto.pitch:+.0f}  roll {rosto.roll:+.0f}", y, (200, 200, 200))
