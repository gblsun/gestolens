"""Laço principal: fonte → detecção → análise → registro → desenho → saídas.

Papel no fluxo
--------------
Orquestra um vídeo (ou a webcam) do primeiro ao último quadro:

1. `fonte_video.FonteVideo` entrega o quadro e o seu instante.
2. O quadro é reduzido para `config.LARGURA_MAX_PROCESSAMENTO` e, se pedido, espelhado.
3. `deteccao.Detector` encontra os landmarks de mãos e rosto.
4. `analise.Analisador` aplica as regras dos exercícios 1 a 5, com suavização.
5. `registro.RegistroVideo` grava a linha do CSV.
6. `desenho.desenhar_analise` desenha a sobreposição, que vai para a janela e/ou para o .mp4.

Teclas na janela: Esc pula para o próximo vídeo; q encerra tudo.

Documentação: docs/Módulos/pipeline.md
"""

from dataclasses import dataclass
from pathlib import Path

import cv2

from . import config
from .analise import Analisador
from .deteccao import Detector
from .desenho import desenhar_analise
from .fonte_video import FonteVideo
from .registro import RegistroVideo

TECLA_ESC = 27
ALTURA_MAX_JANELA = 900
TITULO_JANELA = "GestoLens"


@dataclass
class OpcoesPipeline:
    """Opções de execução, montadas a partir da linha de comando ou do menu.

    Atributos:
        mostrar_janela: exibe o resultado em uma janela do OpenCV.
        salvar_video: grava `<pasta_saidas>/<nome>_anotado.mp4`.
        espelhar: espelha horizontalmente cada quadro (modo selfie, usado na webcam).
        pasta_saidas: pasta onde ficam CSVs e vídeos anotados.
    """

    mostrar_janela: bool = True
    salvar_video: bool = True
    espelhar: bool = False
    pasta_saidas: Path = config.PASTA_SAIDAS


class Interrompido(Exception):
    """Levantada quando o usuário aperta q. `args[0]` guarda o `RegistroVideo` parcial."""


def _redimensionar(imagem, largura_max: int):
    """Reduz a imagem para no máximo `largura_max` pixels de largura, mantendo a proporção."""
    h, w = imagem.shape[:2]
    if w <= largura_max:
        return imagem
    escala = largura_max / w
    return cv2.resize(imagem, (largura_max, int(h * escala)), interpolation=cv2.INTER_AREA)


def processar_fonte(origem: Path | int, opcoes: OpcoesPipeline) -> RegistroVideo:
    """Processa um vídeo inteiro (ou a webcam até Esc/q).

    Parâmetros:
        origem: caminho do vídeo ou índice da webcam.
        opcoes: o que mostrar e o que salvar.

    Retorna:
        O `RegistroVideo` com o caminho do CSV e as estatísticas usadas no resumo.

    Levanta:
        Interrompido: quando o usuário aperta q. O registro parcial já está salvo.
        RuntimeError: quando a fonte não abre (arquivo inválido, câmera ausente).
    """
    interromper = False
    with FonteVideo(origem) as fonte, Detector(imagem_espelhada=opcoes.espelhar) as detector:
        registro = RegistroVideo(fonte.nome, opcoes.pasta_saidas)
        gravador = None
        analisador = None
        total = fonte.total_quadros or "ao vivo"
        print(f"Processando {fonte.nome} ({total} quadros a {fonte.fps:.0f} fps)...")
        if fonte.eh_webcam and opcoes.mostrar_janela:
            print("  Esc ou q encerra a webcam.")

        try:
            for quadro in fonte.quadros():
                imagem = _redimensionar(quadro.imagem, config.LARGURA_MAX_PROCESSAMENTO)
                if opcoes.espelhar:
                    imagem = cv2.flip(imagem, 1)
                h, w = imagem.shape[:2]
                if analisador is None:
                    # A proporção largura/altura corrige distâncias em vídeos não quadrados.
                    analisador = Analisador(aspecto=w / h)

                deteccao = detector.processar(imagem, quadro.timestamp_ms)
                analise = analisador.analisar(quadro.indice, quadro.timestamp_ms, deteccao)
                registro.adicionar(analise)
                desenhar_analise(imagem, analise, fonte.nome)

                if opcoes.salvar_video:
                    if gravador is None:
                        opcoes.pasta_saidas.mkdir(parents=True, exist_ok=True)
                        caminho = opcoes.pasta_saidas / f"{fonte.nome}_anotado.mp4"
                        gravador = cv2.VideoWriter(str(caminho), cv2.VideoWriter_fourcc(*"mp4v"), fonte.fps, (w, h))
                    gravador.write(imagem)

                if opcoes.mostrar_janela:
                    exibicao = imagem
                    if h > ALTURA_MAX_JANELA:
                        exibicao = cv2.resize(imagem, (int(w * ALTURA_MAX_JANELA / h), ALTURA_MAX_JANELA))
                    cv2.imshow(TITULO_JANELA, exibicao)
                    tecla = cv2.waitKey(1) & 0xFF
                    if tecla == TECLA_ESC:
                        break
                    if tecla == ord("q"):
                        interromper = True
                        break
        finally:
            registro.fechar()
            if gravador is not None:
                gravador.release()

    print(f"  {registro.total} quadros | mão em {registro.com_mao} | rosto em {registro.com_rosto} → {registro.caminho}")
    if interromper:
        raise Interrompido(registro)
    return registro
