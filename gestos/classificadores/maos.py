"""Classificadores de mão: exercícios 1, 2 e 3.

- Ex1 `classificar_mao`: aberta, fechada ou parcialmente aberta.
- Ex2 `contar_dedos`: de 0 a 5 dedos estendidos.
- Ex3 `classificar_polegar`: polegar para cima, para baixo ou outro gesto.

Todas as funções recebem os 21 landmarks de uma mão (ver
docs/Conceitos/Landmarks da mão.md) e o `aspecto` (largura/altura) da imagem.
As regras estão ilustradas em gestos/classificadores/README.md.

Documentação: docs/Módulos/maos.md
"""

from .. import config
from ..geometria import dedos_longos_estendidos, distancia, tamanho_mao

MAO_ABERTA = "Mao aberta"
MAO_FECHADA = "Mao fechada"
MAO_PARCIAL = "Mao parcialmente aberta"
MAO_NAO_DETECTADA = "Mao nao detectada"

POLEGAR_CIMA = "Polegar para cima"
POLEGAR_BAIXO = "Polegar para baixo"
POLEGAR_INDEFINIDO = "Polegar indefinido"
OUTRO_GESTO = "Outro gesto"


def polegar_estendido(lm, aspecto: float = 1.0) -> bool:
    """Indica se o polegar está afastado da palma.

    Regra: a ponta (4) fica mais longe da base do indicador (5) do que a
    articulação IP (3), com folga de `config.FATOR_POLEGAR_ESTENDIDO`. Só usa
    distâncias, então vale para as duas mãos e não muda com o espelhamento.

    Parâmetros:
        lm: 21 landmarks da mão.
        aspecto: largura / altura da imagem.

    Retorna:
        True se o polegar está estendido.
    """
    ponta = distancia(lm[4], lm[5], aspecto)
    articulacao = distancia(lm[3], lm[5], aspecto)
    return ponta > articulacao * config.FATOR_POLEGAR_ESTENDIDO


def contar_dedos(lm, aspecto: float = 1.0) -> int:
    """Exercício 2: conta os dedos estendidos.

    Soma os dedos longos estendidos (pela regra em `config.REGRA_DEDOS`, ver
    `geometria.dedos_longos_estendidos`) com o polegar (ver `polegar_estendido`).

    Parâmetros:
        lm: 21 landmarks da mão.
        aspecto: largura / altura da imagem.

    Retorna:
        Número de 0 a 5.
    """
    return dedos_longos_estendidos(lm, aspecto, config.REGRA_DEDOS) + int(polegar_estendido(lm, aspecto))


def classificar_mao(quantidade_dedos: int | None) -> str:
    """Exercício 1: estado da mão a partir da contagem de dedos.

    Recebe a contagem já suavizada, para que o estado e o número exibidos nunca
    se contradigam.

    Parâmetros:
        quantidade_dedos: 0 a 5, ou None quando a mão não foi detectada.

    Retorna:
        `MAO_ABERTA` (>= DEDOS_MAO_ABERTA), `MAO_FECHADA` (<= DEDOS_MAO_FECHADA),
        `MAO_PARCIAL` (entre os dois) ou `MAO_NAO_DETECTADA`.
    """
    if quantidade_dedos is None:
        return MAO_NAO_DETECTADA
    if quantidade_dedos >= config.DEDOS_MAO_ABERTA:
        return MAO_ABERTA
    if quantidade_dedos <= config.DEDOS_MAO_FECHADA:
        return MAO_FECHADA
    return MAO_PARCIAL


def classificar_polegar(lm, aspecto: float = 1.0) -> tuple[str, float]:
    """Exercício 3: polegar para cima, para baixo ou outro gesto.

    Árvore de decisão:
        1. Mais de 1 dedo longo estendido → `OUTRO_GESTO`.
        2. Polegar recolhido (punho fechado) → `OUTRO_GESTO`.
        3. diferença = (y[4] − y[3]) / tamanho da mão
           < −MARGEM → `POLEGAR_CIMA` · > +MARGEM → `POLEGAR_BAIXO` · senão `POLEGAR_INDEFINIDO`.

    Dividir pelo tamanho da mão torna a margem independente da distância à
    câmera. A faixa indefinida evita decisões instáveis perto do limite.

    Parâmetros:
        lm: 21 landmarks da mão.
        aspecto: largura / altura da imagem.

    Retorna:
        (rótulo, diferença relativa). A diferença é 0.0 quando não chega a ser calculada.
    """
    if dedos_longos_estendidos(lm, aspecto, config.REGRA_DEDOS) > 1:
        return OUTRO_GESTO, 0.0

    escala = tamanho_mao(lm, aspecto)
    if escala < 1e-6:
        return POLEGAR_INDEFINIDO, 0.0

    diferenca = (lm[4].y - lm[3].y) / escala
    # Polegar precisa estar afastado da palma; caso contrário é punho fechado.
    if not polegar_estendido(lm, aspecto):
        return OUTRO_GESTO, diferenca
    if diferenca < -config.MARGEM_POLEGAR_ESCALA:
        return POLEGAR_CIMA, diferenca
    if diferenca > config.MARGEM_POLEGAR_ESCALA:
        return POLEGAR_BAIXO, diferenca
    return POLEGAR_INDEFINIDO, diferenca
