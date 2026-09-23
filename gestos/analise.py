"""Análise de um quadro: aplica todos os classificadores e a suavização temporal.

Papel no fluxo
--------------
    ResultadoDeteccao (deteccao) ──► Analisador.analisar ──► AnaliseQuadro
                                         │                       ├─► registro (CSV)
                                         ├─ classificadores.maos   └─► desenho (sobreposição)
                                         ├─ classificadores.rosto
                                         └─ suavizacao.FiltroModa

Cada mão tem filtros próprios, identificados pelo lado ("esquerda"/"direita").
Quando uma mão some, o histórico dela é descartado, para que o Exercício 1
mostre "Mao nao detectada" sem reaproveitar o quadro anterior.

Documentação: docs/Módulos/analise.md
"""

from dataclasses import dataclass, field

from . import config
from .classificadores import maos as cm
from .classificadores import rosto as cr
from .deteccao import ResultadoDeteccao
from .suavizacao import FiltroModa


@dataclass
class AnaliseMao:
    """Classificações de uma mão em um quadro (Exercícios 1, 2 e 3)."""

    lado: str
    landmarks: list
    dedos_bruto: int
    dedos: int            # suavizado
    estado: str           # Ex1
    polegar: str          # Ex3 (suavizado)
    polegar_diferenca: float


@dataclass
class AnaliseRosto:
    """Classificações do rosto em um quadro (Exercícios 4 e 5)."""

    landmarks: list
    boca: str
    proporcao_boca: float
    direcao: str
    desvio_nariz: float
    yaw: float | None = None
    pitch: float | None = None
    roll: float | None = None


@dataclass
class AnaliseQuadro:
    """Resultado completo de um quadro."""

    indice: int
    timestamp_ms: int
    maos: list[AnaliseMao] = field(default_factory=list)
    rosto: AnaliseRosto | None = None


class Analisador:
    """Transforma detecções em rótulos, mantendo filtros temporais por mão (esquerda/direita)."""

    def __init__(self, aspecto: float, janela: int = config.JANELA_SUAVIZACAO):
        """Parâmetros:
            aspecto: largura / altura dos quadros (corrige distâncias em vídeo não quadrado).
            janela: tamanho da janela de suavização, em quadros.
        """
        self.aspecto = aspecto
        self.filtro = FiltroModa(janela)

    def analisar(self, indice: int, timestamp_ms: int, deteccao: ResultadoDeteccao) -> AnaliseQuadro:
        """Classifica mãos e rosto de um quadro.

        Parâmetros:
            indice: índice do quadro.
            timestamp_ms: instante do quadro.
            deteccao: saída de `Detector.processar`.

        Retorna:
            `AnaliseQuadro` com as mãos ordenadas por lado e o rosto (ou None).
        """
        analise = AnaliseQuadro(indice, timestamp_ms)

        lados_vistos = set()
        for mao in deteccao.maos:
            lado = mao.lado
            # Duas mãos com o mesmo rótulo: diferencia a segunda para não misturar filtros.
            if lado in lados_vistos:
                lado = f"{lado}_2"
            lados_vistos.add(lado)

            lm = mao.landmarks
            dedos_bruto = cm.contar_dedos(lm, self.aspecto)
            dedos = self.filtro.atualizar(f"{lado}:dedos", dedos_bruto)
            polegar_bruto, diferenca = cm.classificar_polegar(lm, self.aspecto)
            polegar = self.filtro.atualizar(f"{lado}:polegar", polegar_bruto)
            analise.maos.append(
                AnaliseMao(lado, lm, dedos_bruto, dedos, cm.classificar_mao(dedos), polegar, diferenca)
            )

        # Mãos que sumiram têm o histórico descartado (não reaproveitar quadros anteriores).
        for lado in ("esquerda", "direita", "esquerda_2", "direita_2"):
            if lado not in lados_vistos:
                self.filtro.limpar(f"{lado}:dedos")
                self.filtro.limpar(f"{lado}:polegar")

        if deteccao.rosto is not None:
            lm = deteccao.rosto
            boca, proporcao = cr.classificar_boca(lm, self.aspecto)
            direcao, desvio = cr.classificar_direcao_rosto(lm)
            pose = cr.estimar_pose(deteccao.matriz_rosto)
            analise.rosto = AnaliseRosto(lm, boca, proporcao, direcao, desvio, *(pose or (None, None, None)))

        analise.maos.sort(key=lambda m: m.lado)
        return analise
