"""Funções geométricas sobre landmarks normalizados.

x é normalizado pela largura e y pela altura da imagem. Em vídeos que não são
quadrados (ex.: retrato 1080x1920), uma unidade em x não vale o mesmo que uma
unidade em y. Por isso as distâncias aceitam `aspecto = largura / altura`: Δx é
multiplicado por ele e tudo passa a ser medido em "alturas de imagem".

Documentação: docs/Módulos/geometria.md · docs/Conceitos/Proporção da imagem.md
"""

import math

# Pares (ponta, articulação PIP) de indicador, médio, anelar e mínimo.
DEDOS_LONGOS = [(8, 6), (12, 10), (16, 14), (20, 18)]


def distancia(a, b, aspecto: float = 1.0) -> float:
    """Distância euclidiana entre dois landmarks.

    Parâmetros:
        a, b: objetos com atributos `x` e `y` normalizados.
        aspecto: largura / altura da imagem (1.0 dispensa a correção).

    Retorna:
        Distância em unidades da altura da imagem.
    """
    return math.hypot((a.x - b.x) * aspecto, a.y - b.y)


def dedos_longos_estendidos(lm, aspecto: float = 1.0, regra: str = "distancia") -> int:
    """Conta quantos dos quatro dedos longos estão estendidos.

    Parâmetros:
        lm: 21 landmarks da mão.
        aspecto: largura / altura da imagem.
        regra:
            - "vertical" (código-base): ponta acima da articulação PIP (y menor).
              Só funciona com a mão em pé; com a mão deitada ou invertida (polegar
              para baixo), dedos dobrados passam a contar como estendidos.
            - "distancia": ponta mais distante do punho (0) do que a articulação
              PIP. Não depende da rotação da mão no plano da imagem.

    Retorna:
        Número de 0 a 4.
    """
    if regra == "vertical":
        return sum(lm[ponta].y < lm[articulacao].y for ponta, articulacao in DEDOS_LONGOS)
    punho = lm[0]
    return sum(
        distancia(lm[ponta], punho, aspecto) > distancia(lm[articulacao], punho, aspecto)
        for ponta, articulacao in DEDOS_LONGOS
    )


def tamanho_mao(lm, aspecto: float = 1.0) -> float:
    """Escala de referência da mão: distância do punho (0) à base do dedo médio (9).

    Serve para exprimir margens como fração do tamanho da mão, o que as torna
    independentes da distância à câmera.
    """
    return distancia(lm[0], lm[9], aspecto)
