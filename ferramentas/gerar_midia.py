"""Gera as imagens, GIFs, gráficos e o mapa do vault usados nos READMEs.

Pré-requisito: rodar o pipeline antes, para existirem `saidas/<video>.csv` e
`saidas/<video>_anotado.mp4`:

    python exercicio_mediapipe.py --sem-janela
    python ferramentas/gerar_midia.py

Tudo é escrito em `assets/`. Os trechos dos GIFs e os quadros das ilustrações
são escolhidos automaticamente a partir dos CSVs (ex.: pico da proporção da
boca), então a mídia acompanha novos vídeos ou novos limiares.

Dependências extras: Pillow e matplotlib.
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from gestos import config  # noqa: E402
from gestos.classificadores import maos as cm  # noqa: E402
from gestos.classificadores import rosto as cr  # noqa: E402
from gestos.deteccao import Detector  # noqa: E402
from gestos.desenho import CONEXOES_MAO  # noqa: E402
from gestos.geometria import DEDOS_LONGOS, dedos_longos_estendidos, distancia, tamanho_mao  # noqa: E402

ASSETS = RAIZ / "assets"
SAIDAS = config.PASTA_SAIDAS

# Paleta de referência (skill dataviz), validada para CVD nas combinações usadas.
AZUL, LARANJA, AQUA, AMARELO, MAGENTA, VERDE, VIOLETA, VERMELHO = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
SUPERFICIE, TINTA, TINTA_2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CORES_DEDO = {"polegar": LARANJA, "indicador": AZUL, "médio": AQUA, "anelar": VIOLETA, "mínimo": MAGENTA}
DEDO_DO_PONTO = {0: None, **{i: "polegar" for i in (1, 2, 3, 4)}, **{i: "indicador" for i in (5, 6, 7, 8)},
                 **{i: "médio" for i in (9, 10, 11, 12)}, **{i: "anelar" for i in (13, 14, 15, 16)},
                 **{i: "mínimo" for i in (17, 18, 19, 20)}}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRADE, "axes.labelcolor": TINTA_2,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.titlecolor": TINTA, "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 1,
})


# ---------------------------------------------------------------- utilidades
def ler_csv(video: str) -> list[dict]:
    """Lê `saidas/<video>.csv`."""
    with open(SAIDAS / f"{video}.csv", newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def numero(valor: str) -> float:
    """Converte uma célula do CSV em float (vazio vira NaN)."""
    return float(valor) if valor not in ("", None) else float("nan")


def ler_quadro(caminho: Path, indice: int, largura: int | None = config.LARGURA_MAX_PROCESSAMENTO):
    """Lê o quadro `indice` de um vídeo (rotação automática) e o reduz como o pipeline faz."""
    captura = cv2.VideoCapture(str(caminho))
    captura.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
    captura.set(cv2.CAP_PROP_POS_FRAMES, indice)
    ok, imagem = captura.read()
    captura.release()
    if not ok:
        raise RuntimeError(f"Não foi possível ler o quadro {indice} de {caminho}")
    if largura and imagem.shape[1] > largura:
        imagem = cv2.resize(imagem, (largura, int(imagem.shape[0] * largura / imagem.shape[1])), cv2.INTER_AREA)
    return imagem


def quadro_original(video: str, indice: int):
    """Quadro do vídeo original (sem anotações)."""
    caminho = next(config.PASTA_VIDEOS.glob(f"{video}.*"))
    return ler_quadro(caminho, indice)


def detectar(imagem):
    """Detecção isolada de um quadro (Detector novo, instante 0)."""
    with Detector(imagem_espelhada=False) as detector:
        return detector.processar(imagem, 0)


def recorte(imagem, pontos, margem=0.35, indices=None):
    """Recorta a região que contém os landmarks.

    Retorna:
        (imagem_rgb_recortada, função landmark → (x, y) em pixels do recorte).
    """
    h, w = imagem.shape[:2]
    sel = [pontos[i] for i in indices] if indices else list(pontos)
    xs = np.array([p.x * w for p in sel])
    ys = np.array([p.y * h for p in sel])
    lado = max(np.ptp(xs), np.ptp(ys)) * (1 + 2 * margem)
    cx, cy = xs.mean(), ys.mean()
    x0, y0 = int(max(0, cx - lado / 2)), int(max(0, cy - lado / 2))
    x1, y1 = int(min(w, cx + lado / 2)), int(min(h, cy + lado / 2))
    rgb = cv2.cvtColor(imagem[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
    return rgb, lambda p: (p.x * w - x0, p.y * h - y0)


def salvar(fig, nome: str) -> None:
    """Salva a figura em assets/ e fecha."""
    fig.savefig(ASSETS / nome, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  {nome}")


def eixo_imagem(ax, rgb, titulo=None):
    """Mostra uma imagem sem eixos."""
    ax.imshow(rgb)
    ax.set_axis_off()
    if titulo:
        ax.set_title(titulo, fontsize=11, color=TINTA, pad=8)


def rotulo_ponto(ax, xy, texto, cor=TINTA, deslocamento=(6, -6), tamanho=8):
    """Número/nome de um landmark com fundo branco para legibilidade."""
    ax.annotate(texto, xy, xytext=deslocamento, textcoords="offset points", fontsize=tamanho, color=cor,
                fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


# ---------------------------------------------------------------- GIFs
def frames_anotados(video: str, inicio_s: float, fim_s: float, largura: int, fps_gif: int = 8):
    """Extrai quadros do vídeo anotado entre dois instantes, como imagens PIL."""
    captura = cv2.VideoCapture(str(SAIDAS / f"{video}_anotado.mp4"))
    fps = captura.get(cv2.CAP_PROP_FPS) or 30
    passo = max(1, round(fps / fps_gif))
    total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
    i0, i1 = max(0, int(inicio_s * fps)), min(total - 1, int(fim_s * fps))
    quadros = []
    captura.set(cv2.CAP_PROP_POS_FRAMES, i0)
    for i in range(i0, i1 + 1):
        ok, imagem = captura.read()
        if not ok:
            break
        if (i - i0) % passo:
            continue
        altura = int(imagem.shape[0] * largura / imagem.shape[1])
        imagem = cv2.resize(imagem, (largura, altura), interpolation=cv2.INTER_AREA)
        quadros.append(Image.fromarray(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)))
    captura.release()
    return quadros


def salvar_gif(quadros, nome: str, fps_gif: int = 8) -> None:
    """Grava um GIF em loop com paleta adaptativa."""
    paleta = [q.convert("P", palette=Image.ADAPTIVE, colors=64) for q in quadros]
    paleta[0].save(ASSETS / nome, save_all=True, append_images=paleta[1:], duration=int(1000 / fps_gif),
                   loop=0, optimize=True, disposal=2)
    print(f"  {nome} ({(ASSETS / nome).stat().st_size / 1e6:.1f} MB, {len(quadros)} quadros)")


def janela_mais_variada(linhas, coluna, duracao=4.0):
    """Início (s) da janela de `duracao` com mais trocas de valor em `coluna`."""
    tempos = [numero(l["t_s"]) for l in linhas]
    valores = [l[coluna] for l in linhas]
    melhor, inicio_melhor = -1, 0.0
    for i, t0 in enumerate(tempos[::15]):
        trecho = [v for t, v in zip(tempos, valores) if t0 <= t < t0 + duracao and v]
        pontuacao = len(set(trecho)) * 100 + sum(a != b for a, b in zip(trecho, trecho[1:]))
        if pontuacao > melhor:
            melhor, inicio_melhor = pontuacao, t0
    return inicio_melhor


def trechos_gif():
    """Escolhe, pelos CSVs, o trecho de cada exercício. Retorna {nome: (video, inicio, fim)}."""
    trechos = {}
    l57, l58 = ler_csv("IMG_7457"), ler_csv("IMG_7458")
    t = janela_mais_variada(l58, "direita_estado")
    trechos["ex1_mao.gif"] = ("IMG_7458", t, t + 4)
    t = janela_mais_variada(l57, "direita_dedos")
    trechos["ex2_dedos.gif"] = ("IMG_7457", t, t + 4)

    l59 = ler_csv("IMG_7459")
    t_cima = next(numero(l["t_s"]) for l in l59 if l["direita_polegar"] == cm.POLEGAR_CIMA)
    trechos["ex3_polegar.gif"] = ("IMG_7459", max(0, t_cima - 0.4), t_cima + 3.6)

    l60 = ler_csv("IMG_7460")
    pico = max(l60, key=lambda l: numero(l["proporcao_boca"]) if l["proporcao_boca"] else -1)
    t = numero(pico["t_s"])
    trechos["ex4_boca.gif"] = ("IMG_7460", max(0, t - 1.5), t + 2.5)

    l61 = ler_csv("IMG_7461")
    esq = min(l61, key=lambda l: numero(l["desvio_nariz"]) if l["desvio_nariz"] else 9)
    t = numero(esq["t_s"])
    trechos["ex5_direcao.gif"] = ("IMG_7461", max(0, t - 1.5), t + 2.5)
    return trechos


def gerar_gifs():
    """GIF por exercício e a montagem demo.gif."""
    trechos = trechos_gif()
    for nome, (video, t0, t1) in trechos.items():
        salvar_gif(frames_anotados(video, t0, t1, largura=240), nome)

    # demo: 4 exercícios lado a lado, sincronizados em 3,5 s.
    colunas = [frames_anotados(*trechos[n][:2], trechos[n][1] + 3.5, largura=170)
               for n in ("ex2_dedos.gif", "ex3_polegar.gif", "ex4_boca.gif", "ex5_direcao.gif")]
    n = min(len(c) for c in colunas)
    altura = colunas[0][0].height
    faixa = 26
    fonte = ImageFont.truetype(font_manager.findfont("DejaVu Sans:bold"), 13)
    titulos = ("Ex2 · dedos", "Ex3 · polegar", "Ex4 · boca", "Ex5 · direção")
    montagem = []
    for i in range(n):
        tela = Image.new("RGB", (170 * 4 + 6 * 3, altura + faixa), SUPERFICIE)
        desenho = ImageDraw.Draw(tela)
        for j, coluna in enumerate(colunas):
            tela.paste(coluna[i].resize((170, altura)), (j * 176, faixa))
            desenho.text((j * 176 + 85, faixa // 2), titulos[j], fill=TINTA, font=fonte, anchor="mm")
        montagem.append(tela)
    salvar_gif(montagem, "demo.gif")


# ---------------------------------------------------------------- ilustrações
def quadro_com(video, filtro):
    """Quadro no meio da sequência contínua mais longa que satisfaz `filtro`.

    Retorna:
        (índice do quadro, linha do CSV).
    """
    linhas = ler_csv(video)
    melhor, atual = (0, -1), None
    for i, linha in enumerate(linhas):
        if filtro(linha):
            atual = i if atual is None else atual
            if i - atual > melhor[1] - melhor[0]:
                melhor = (atual, i)
        else:
            atual = None
    if melhor[1] < 0:
        raise ValueError(f"Nenhum quadro de {video} satisfaz o filtro")
    meio = (melhor[0] + melhor[1]) // 2
    return int(linhas[meio]["quadro"]), linhas[meio]


def rosto_detectado(video, indice):
    """(imagem, ResultadoDeteccao com rosto) de um quadro original; tenta vizinhos se preciso."""
    for delta in (0, 3, -3, 6, -6, 10, -10, 15, -15):
        imagem = quadro_original(video, max(0, indice + delta))
        det = detectar(imagem)
        if det.rosto is not None:
            return imagem, det
    raise RuntimeError(f"Nenhum rosto perto de {video}#{indice}")


def mao_detectada(video, indice):
    """(imagem, landmarks da primeira mão, aspecto) de um quadro original.

    Se a detecção isolada falhar, tenta quadros vizinhos.
    """
    for delta in (0, 3, -3, 6, -6, 10, -10, 15, -15):
        imagem = quadro_original(video, max(0, indice + delta))
        det = detectar(imagem)
        if det.maos:
            return imagem, det.maos[0].landmarks, imagem.shape[1] / imagem.shape[0]
    raise RuntimeError(f"Nenhuma mão perto de {video}#{indice}")


def desenhar_esqueleto(ax, lm, px, numeros=True, alfa=1.0):
    """Esqueleto da mão colorido por dedo."""
    for a, b in CONEXOES_MAO:
        dedo = DEDO_DO_PONTO[b] or DEDO_DO_PONTO[a]
        (xa, ya), (xb, yb) = px(lm[a]), px(lm[b])
        ax.plot([xa, xb], [ya, yb], color=CORES_DEDO.get(dedo, TINTA_2), lw=2.5, alpha=alfa, solid_capstyle="round")
    for i, p in enumerate(lm):
        x, y = px(p)
        ax.scatter([x], [y], s=46, color=CORES_DEDO.get(DEDO_DO_PONTO[i], TINTA), edgecolor="white", lw=1.5,
                   zorder=3, alpha=alfa)
        if numeros:
            rotulo_ponto(ax, (x, y), str(i))


def mapa_mao():
    """Os 21 landmarks numerados sobre uma mão aberta real."""
    indice, _ = quadro_com("IMG_7457", lambda l: l["direita_dedos_bruto"] == "5")
    imagem, lm, _ = mao_detectada("IMG_7457", indice)
    rgb, px = recorte(imagem, lm, margem=0.25)
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    eixo_imagem(ax, (rgb * 0.55 + 255 * 0.45).astype(np.uint8))
    desenhar_esqueleto(ax, lm, px)
    for dedo, cor in CORES_DEDO.items():
        ax.plot([], [], color=cor, lw=3, label=dedo)
    ax.plot([], [], "o", color=TINTA, label="0 = punho")
    ax.legend(loc="lower left", frameon=True, fontsize=9, facecolor="white", edgecolor=GRADE)
    ax.set_title("21 landmarks da mão (Hand Landmarker)\nponta = 4, 8, 12, 16, 20 · PIP = 6, 10, 14, 18", fontsize=11)
    salvar(fig, "mapa_mao.png")


def mapa_rosto():
    """Pontos do rosto usados nas regras, com as medidas desenhadas."""
    indice, _ = quadro_com("IMG_7460", lambda l: l["direcao"] == cr.ROSTO_FRENTE and l["boca"] == cr.BOCA_FECHADA)
    imagem, det = rosto_detectado("IMG_7460", indice)
    lm = det.rosto
    rgb, px = recorte(imagem, lm, margem=0.08)
    fig, ax = plt.subplots(figsize=(6.4, 7))
    eixo_imagem(ax, (rgb * 0.6 + 255 * 0.4).astype(np.uint8))
    todos = np.array([px(p) for p in lm])
    ax.scatter(todos[:, 0], todos[:, 1], s=2, color=TINTA_2, alpha=0.35)
    P = {i: px(lm[i]) for i in (1, 13, 14, 33, 61, 263, 291)}
    ax.plot(*zip(P[61], P[291]), color=AZUL, lw=2.5)
    ax.plot(*zip(P[13], P[14]), color=LARANJA, lw=2.5)
    ax.plot(*zip(P[33], P[263]), color=AQUA, lw=2, ls="-")
    centro = ((P[33][0] + P[263][0]) / 2, (P[33][1] + P[263][1]) / 2)
    ax.plot([centro[0], centro[0]], [centro[1], P[1][1]], color=AQUA, lw=1)
    ax.annotate("", P[1], (centro[0], P[1][1]), arrowprops=dict(arrowstyle="->", color=VIOLETA, lw=2))
    for i, nome, cor, desl in [(1, "1 nariz", VIOLETA, (8, 4)), (13, "13", LARANJA, (6, 6)),
                               (14, "14", LARANJA, (6, -14)), (33, "33 olho", AQUA, (-50, -14)),
                               (263, "263 olho", AQUA, (6, -14)), (61, "61", AZUL, (-26, 4)), (291, "291", AZUL, (6, 4))]:
        ax.scatter(*P[i], s=60, color=cor, edgecolor="white", lw=1.5, zorder=3)
        rotulo_ponto(ax, P[i], nome, cor, desl, 9)
    ax.plot([], [], color=AZUL, lw=3, label="largura da boca 61–291")
    ax.plot([], [], color=LARANJA, lw=3, label="abertura 13–14")
    ax.plot([], [], color=AQUA, lw=3, label="distância entre olhos 33–263")
    ax.plot([], [], color=VIOLETA, lw=3, label="desvio horizontal do nariz")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=9, frameon=False)
    ax.set_title("Landmarks do rosto usados nas regras (de 478)", fontsize=11)
    salvar(fig, "mapa_rosto.png")


def regra_dedos():
    """Mesmo quadro de polegar para baixo: regra vertical × regra por distância."""
    indice, _ = quadro_com("IMG_7459", lambda l: l["direita_polegar"] == cm.POLEGAR_BAIXO)
    imagem, lm, aspecto = mao_detectada("IMG_7459", indice)
    rgb, px = recorte(imagem, lm, margem=0.3)
    fundo = (rgb * 0.55 + 255 * 0.45).astype(np.uint8)
    fig, eixos = plt.subplots(1, 2, figsize=(11, 5.8))
    for ax, regra in zip(eixos, ("vertical", "distancia")):
        eixo_imagem(ax, fundo)
        desenhar_esqueleto(ax, lm, px, numeros=False, alfa=0.35)
        pulso = px(lm[0])
        for ponta, pip in DEDOS_LONGOS:
            (xt, yt), (xp, yp) = px(lm[ponta]), px(lm[pip])
            if regra == "vertical":
                estendido = lm[ponta].y < lm[pip].y
                ax.plot([xp - 14, xp + 14], [yp, yp], color=TINTA_2, lw=1.5)
                ax.annotate("", (xt, yt), (xt, yp), arrowprops=dict(arrowstyle="->", color=TINTA_2, lw=1.2))
            else:
                estendido = distancia(lm[ponta], lm[0], aspecto) > distancia(lm[pip], lm[0], aspecto)
                ax.plot(*zip(pulso, (xt, yt)), color=TINTA_2, lw=1, ls="-")
                ax.plot(*zip(pulso, (xp, yp)), color=GRADE, lw=3, alpha=0.9)
            cor = VERDE if estendido else VERMELHO
            ax.scatter([xt], [yt], s=90, color=cor, edgecolor="white", lw=1.5, zorder=4)
            rotulo_ponto(ax, (xt, yt), "estendido" if estendido else "dobrado", cor, (8, -4), 8)
        if regra == "distancia":
            ax.scatter(*pulso, s=90, color=TINTA, edgecolor="white", lw=1.5, zorder=4)
            rotulo_ponto(ax, pulso, "punho (0)", TINTA, (8, 4), 8)
        n = dedos_longos_estendidos(lm, aspecto, regra)
        titulo = ("Regra vertical (código-base)\nponta acima da PIP? → " if regra == "vertical"
                  else "Regra por distância (padrão)\nponta mais longe do punho que a PIP? → ")
        ax.set_title(titulo + f"{n} dedos longos estendidos", fontsize=11,
                     color=VERMELHO if regra == "vertical" else VERDE)
    fig.suptitle("Polegar para baixo com a mão invertida: os dedos estão dobrados", fontsize=12, y=1.02)
    salvar(fig, "regra_dedos.png")


def melhor_quadro_polegar(alvo):
    """Quadro de IMG_7459 em que a detecção isolada confirma `alvo` com a maior |diferença|."""
    candidatos = [int(l["quadro"]) for l in ler_csv("IMG_7459") if l["direita_polegar"] == alvo]
    melhor = None
    for indice in candidatos[:: max(1, len(candidatos) // 12)]:
        imagem = quadro_original("IMG_7459", indice)
        det = detectar(imagem)
        if not det.maos:
            continue
        lm, aspecto = det.maos[0].landmarks, imagem.shape[1] / imagem.shape[0]
        rotulo, dif = cm.classificar_polegar(lm, aspecto)
        if rotulo == alvo and (melhor is None or abs(dif) > melhor[0]):
            melhor = (abs(dif), imagem, lm, aspecto)
    if melhor is None:
        raise RuntimeError(f"Nenhum quadro confirma {alvo}")
    return melhor[1:]


def regra_polegar():
    """Polegar para cima e para baixo: diferença vertical 3→4 relativa ao tamanho da mão."""
    fig, eixos = plt.subplots(1, 2, figsize=(10, 5.6))
    for ax, alvo in zip(eixos, (cm.POLEGAR_CIMA, cm.POLEGAR_BAIXO)):
        imagem, lm, aspecto = melhor_quadro_polegar(alvo)
        rgb, px = recorte(imagem, lm, margem=0.3)
        eixo_imagem(ax, (rgb * 0.55 + 255 * 0.45).astype(np.uint8))
        desenhar_esqueleto(ax, lm, px, numeros=False, alfa=0.35)
        p0, p9, p3, p4 = px(lm[0]), px(lm[9]), px(lm[3]), px(lm[4])
        ax.plot(*zip(p0, p9), color=AZUL, lw=3)
        rotulo_ponto(ax, ((p0[0] + p9[0]) / 2, (p0[1] + p9[1]) / 2), "tamanho da mão (0–9)", AZUL, (8, 0), 8)
        ax.plot([p3[0], p3[0] + 60], [p3[1], p3[1]], color=TINTA_2, lw=1)
        ax.annotate("", (p3[0] + 45, p4[1]), (p3[0] + 45, p3[1]),
                    arrowprops=dict(arrowstyle="->", color=LARANJA, lw=2.5))
        for i, p in ((3, p3), (4, p4)):
            ax.scatter(*p, s=80, color=LARANJA, edgecolor="white", lw=1.5, zorder=4)
            rotulo_ponto(ax, p, str(i), LARANJA, (-18, -4), 9)
        rotulo, dif = cm.classificar_polegar(lm, aspecto)
        ax.set_title(f"{rotulo}\ndiferença = (y4 − y3) / tamanho = {dif:+.2f}", fontsize=11)
    fig.suptitle(f"Margem ±{config.MARGEM_POLEGAR_ESCALA}: abaixo de −{config.MARGEM_POLEGAR_ESCALA} = cima, "
                 f"acima de +{config.MARGEM_POLEGAR_ESCALA} = baixo, entre os dois = indefinido", fontsize=10, y=0.99)
    salvar(fig, "regra_polegar.png")


def regra_boca():
    """Boca fechada × aberta com as duas medidas e a proporção."""
    linhas = ler_csv("IMG_7460")
    fechada = next(l for l in linhas if l["boca"] == cr.BOCA_FECHADA)
    aberta = max(linhas, key=lambda l: numero(l["proporcao_boca"]) if l["proporcao_boca"] else -1)
    fig, eixos = plt.subplots(1, 2, figsize=(10, 4.6))
    for ax, linha in zip(eixos, (fechada, aberta)):
        imagem, det = rosto_detectado("IMG_7460", int(linha["quadro"]))
        lm = det.rosto
        aspecto = imagem.shape[1] / imagem.shape[0]
        rgb, px = recorte(imagem, lm, margem=0.6, indices=[61, 291, 13, 14, 0, 17])
        eixo_imagem(ax, rgb)
        P = {i: px(lm[i]) for i in (13, 14, 61, 291)}
        ax.plot(*zip(P[61], P[291]), color=AZUL, lw=3)
        ax.plot(*zip(P[13], P[14]), color=LARANJA, lw=3)
        for i in P:
            ax.scatter(*P[i], s=60, color=AZUL if i in (61, 291) else LARANJA, edgecolor="white", lw=1.5, zorder=3)
        rotulo, prop = cr.classificar_boca(lm, aspecto)
        ax.set_title(f"{rotulo}: proporção = {prop:.2f}", fontsize=11)
    fig.suptitle(f"proporção = abertura (13–14, laranja) / largura (61–291, azul) · limiar {config.LIMIAR_BOCA_ABERTA}",
                 fontsize=10.5, y=1.0)
    salvar(fig, "regra_boca.png")


def regra_direcao():
    """Três poses de IMG_7461: esquerda da imagem, frente, direita da imagem."""
    escolhas = [quadro_com("IMG_7461", lambda l, d=d: l["direcao"] == d)[1]
                for d in (cr.ROSTO_ESQUERDA, cr.ROSTO_FRENTE, cr.ROSTO_DIREITA)]
    fig, eixos = plt.subplots(1, 3, figsize=(12, 5))
    for ax, linha in zip(eixos, escolhas):
        imagem, det = rosto_detectado("IMG_7461", int(linha["quadro"]))
        lm = det.rosto
        rgb, px = recorte(imagem, lm, margem=0.12)
        eixo_imagem(ax, rgb)
        o1, o2, nariz = px(lm[33]), px(lm[263]), px(lm[1])
        centro = ((o1[0] + o2[0]) / 2, (o1[1] + o2[1]) / 2)
        ax.plot(*zip(o1, o2), color=AQUA, lw=2)
        ax.axvline(centro[0], color=AQUA, lw=1)
        ax.annotate("", (nariz[0], centro[1]), centro, arrowprops=dict(arrowstyle="->", color=VIOLETA, lw=2.5))
        ax.scatter(*nariz, s=70, color=VIOLETA, edgecolor="white", lw=1.5, zorder=3)
        rotulo, desvio = cr.classificar_direcao_rosto(lm)
        yaw = round(cr.estimar_pose(det.matriz_rosto)[0]) + 0  # evita "-0"
        ax.set_title(f"{rotulo.replace('Rosto virado', 'Virado')}\ndesvio {desvio:+.2f} · yaw {yaw:+.0f}°", fontsize=10.5)
    fig.suptitle(f"desvio = (x do nariz − centro dos olhos) / distância entre olhos · "
                 f"|desvio| > {config.LIMIAR_DIRECAO} = virado", fontsize=10.5, y=1.01)
    salvar(fig, "regra_direcao.png")


def figura_aspecto():
    """Por que x e y normalizados não têm a mesma escala num vídeo em retrato."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 6.4), gridspec_kw={"width_ratios": [1, 0.5625 * 1.25]})
    paineis = ((1, 1, "coordenadas normalizadas\n(o que o MediaPipe devolve)"),
               (1080, 1920, "pixels reais\n(vídeo retrato 1080 × 1920)"))
    for ax, (largura, altura, titulo) in zip((a1, a2), paineis):
        ax.set_xlim(-0.02 * largura, 1.02 * largura)
        ax.set_ylim(1.02 * altura, -0.02 * altura)
        ax.set_aspect("equal")
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        for i in range(11):
            ax.plot([i * largura / 10] * 2, [0, altura], color=GRADE, lw=1)
            ax.plot([0, largura], [i * altura / 10] * 2, color=GRADE, lw=1)
        ax.add_patch(plt.Rectangle((0, 0), largura, altura, fill=False, ec=TINTA_2, lw=1.5))
        # Uma célula 0,1 × 0,1 destacada.
        ax.add_patch(plt.Rectangle((0.4 * largura, 0.4 * altura), 0.1 * largura, 0.1 * altura, fc=AZUL, alpha=0.35, ec=AZUL, lw=2))
        rotulo = "0,1 × 0,1\nquadrado" if largura == 1 else "108 × 192 px\nretângulo alto"
        ax.text(0.55 * largura, 0.45 * altura, rotulo, va="center", ha="left", fontsize=10, color=AZUL, fontweight="bold")
        ax.set_title(titulo, fontsize=11)
    fig.suptitle("A mesma célula de 0,1 × 0,1 tem 108 px de largura e 192 px de altura", fontsize=12)
    fig.text(0.5, 0.02, "correção: distancia(a, b, aspecto) = hypot(Δx · largura/altura, Δy)", ha="center",
             fontsize=10.5, family="monospace", color=TINTA)
    salvar(fig, "aspecto.png")


# ---------------------------------------------------------------- gráficos
def grafico_boca():
    """Proporção da boca ao longo de IMG_7460, com o limiar."""
    linhas = ler_csv("IMG_7460")
    t = [numero(l["t_s"]) for l in linhas]
    p = [numero(l["proporcao_boca"]) for l in linhas]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.fill_between(t, p, config.LIMIAR_BOCA_ABERTA, where=[v > config.LIMIAR_BOCA_ABERTA for v in p],
                    color=AZUL, alpha=0.12, lw=0)
    ax.plot(t, p, color=AZUL, lw=2)
    ax.axhline(config.LIMIAR_BOCA_ABERTA, color=TINTA_2, lw=1)
    ax.text(t[-1], config.LIMIAR_BOCA_ABERTA + 0.015, f"limiar {config.LIMIAR_BOCA_ABERTA} → acima = boca aberta",
            ha="right", va="bottom", color=TINTA_2, fontsize=9)
    ax.set_xlabel("tempo (s)")
    ax.set_ylabel("proporção altura / largura")
    ax.set_title("IMG_7460 · proporção da boca por quadro", loc="left", fontsize=11)
    ax.set_ylim(bottom=0)
    salvar(fig, "grafico_boca.png")


def grafico_direcao():
    """Desvio do nariz e yaw em IMG_7461, em dois painéis com o mesmo eixo de tempo (sem eixo duplo)."""
    linhas = [l for l in ler_csv("IMG_7461") if l["desvio_nariz"]]
    t = [numero(l["t_s"]) for l in linhas]
    d = [numero(l["desvio_nariz"]) for l in linhas]
    y = [numero(l["yaw"]) for l in linhas]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.4), sharex=True)
    lim, faixa = config.LIMIAR_DIRECAO, config.FAIXA_INDEFINIDA_DIRECAO
    for s in (1, -1):
        a1.axhspan(s * (lim - faixa), s * (lim + faixa), color=GRADE, alpha=0.9, lw=0)
    a1.plot(t, d, color=VIOLETA, lw=2)
    a1.text(t[0], lim + faixa + 0.05, "faixa indefinida ±0,12 ± 0,03", fontsize=8.5, color=TINTA_2)
    a1.text(t[-1], 0.55, "↑ direita da imagem", ha="right", fontsize=8.5, color=TINTA_2)
    a1.text(t[-1], -0.75, "↓ esquerda da imagem", ha="right", fontsize=8.5, color=TINTA_2)
    a1.set_ylabel("desvio do nariz")
    a1.set_title("IMG_7461 · direção do rosto (regra do Ex5) e pose facial (extensão)", loc="left", fontsize=11)
    a2.plot(t, y, color=AZUL, lw=2)
    a2.axhline(0, color=TINTA_2, lw=1)
    a2.set_ylabel("yaw (graus)")
    a2.set_xlabel("tempo (s)")
    salvar(fig, "grafico_direcao.png")


def grafico_suavizacao():
    """Contagem de dedos bruta × suavizada (moda de 7 quadros) em IMG_7457."""
    linhas = ler_csv("IMG_7457")
    t0 = janela_mais_variada(linhas, "direita_dedos_bruto", duracao=5)
    trecho = [l for l in linhas if t0 <= numero(l["t_s"]) < t0 + 5]
    t = [numero(l["t_s"]) for l in trecho]
    bruto = [numero(l["direita_dedos_bruto"]) for l in trecho]
    suave = [numero(l["direita_dedos"]) for l in trecho]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.step(t, bruto, where="post", color=LARANJA, lw=1.5, alpha=0.9, label="bruto (por quadro)")
    ax.step(t, suave, where="post", color=AZUL, lw=2.5, label=f"suavizado (moda de {config.JANELA_SUAVIZACAO} quadros)")
    ax.set_yticks(range(6))
    ax.set_ylim(-0.3, 5.5)
    ax.set_xlabel("tempo (s)")
    ax.set_ylabel("dedos (mão direita)")
    ax.set_title("IMG_7457 · a suavização remove oscilações de poucos quadros", loc="left", fontsize=11)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.22), ncol=2, frameon=False, fontsize=9)
    trocas_b = sum(a != b for a, b in zip(bruto, bruto[1:]))
    trocas_s = sum(a != b for a, b in zip(suave, suave[1:]))
    ax.text(t[-1], 5.25, f"trocas: bruto {trocas_b} · suavizado {trocas_s}", ha="right", fontsize=9, color=TINTA_2)
    salvar(fig, "grafico_suavizacao.png")


def miniaturas():
    """Um quadro anotado de cada vídeo, com o que ele exercita."""
    conteudo = {"IMG_7457": "Ex1 · Ex2\nmão aberta/fechada, dedos", "IMG_7458": "Ex1 · Ex2\ncontagem de dedos",
                "IMG_7459": "Ex3\npolegar cima/baixo", "IMG_7460": "Ex4\nboca aberta/fechada",
                "IMG_7461": "Ex5 · pose\ndireção do rosto"}
    alvos = {"IMG_7457": lambda l: l["direita_dedos"] == "5", "IMG_7458": lambda l: l["direita_dedos"] == "3",
             "IMG_7459": lambda l: l["direita_polegar"] == cm.POLEGAR_CIMA,
             "IMG_7460": lambda l: numero(l["proporcao_boca"] or "0") > 0.4,
             "IMG_7461": lambda l: l["direcao"] == cr.ROSTO_ESQUERDA}
    fig, eixos = plt.subplots(1, 5, figsize=(14, 5.6))
    for ax, (video, texto) in zip(eixos, conteudo.items()):
        indice, _ = quadro_com(video, alvos[video])
        imagem = ler_quadro(SAIDAS / f"{video}_anotado.mp4", indice, largura=None)
        eixo_imagem(ax, cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB), f"{video}\n{texto}")
    salvar(fig, "miniaturas.png")


# ---------------------------------------------------------------- mapa do vault
CORES_PASTA = {"Módulos": AZUL, "Exercícios": LARANJA, "Conceitos": AQUA, "Avaliação": AMARELO,
               "Resultados": MAGENTA}


def grafo_vault():
    """Desenha o grafo de notas do Obsidian (wikilinks) com layout de forças."""
    notas = {p.stem: p for p in RAIZ.rglob("*.md")
             if not any(x in p.parts for x in ("saidas", "gestos", ".obsidian", "assets", "ferramentas",
                                               "proposta", "Vídeos Exercício mediapipe"))}
    arestas = set()
    for nome, caminho in notas.items():
        texto = caminho.read_text(encoding="utf-8")
        wikilinks = re.findall(r"\[\[([^\]|#]+)", texto)
        links_md = [Path(unquote(l)).stem for l in re.findall(r"\]\(([^)#]+?\.md)", texto)]
        for alvo in wikilinks + links_md:
            alvo = alvo.strip()
            if alvo in notas and alvo != nome:
                arestas.add(tuple(sorted((nome, alvo))))
    nomes = sorted(notas)
    idx = {n: i for i, n in enumerate(nomes)}
    grau = Counter(n for a in arestas for n in a)

    # Fruchterman–Reingold simples em numpy (semente fixa → imagem reprodutível).
    rng = np.random.default_rng(7)
    pos = rng.normal(size=(len(nomes), 2))
    k = 1.8 / np.sqrt(len(nomes))
    temperatura = 0.2
    pares = np.array([(idx[a], idx[b]) for a, b in arestas])
    for _ in range(600):
        delta = pos[:, None, :] - pos[None, :, :]
        dist = np.linalg.norm(delta, axis=-1) + 1e-9
        desloc = (delta / dist[..., None] * (k * k / dist)[..., None]).sum(axis=1)
        d = pos[pares[:, 0]] - pos[pares[:, 1]]
        dd = np.linalg.norm(d, axis=1)[:, None] + 1e-9
        forca = d / dd * (dd * dd / k)
        np.add.at(desloc, pares[:, 0], -forca)
        np.add.at(desloc, pares[:, 1], forca)
        desloc -= pos * 0.02  # gravidade leve para o centro
        norma = np.linalg.norm(desloc, axis=1)[:, None] + 1e-9
        pos += desloc / norma * np.minimum(norma, temperatura)
        temperatura *= 0.99

    def cor(nome):
        if nome in ("Início", "README"):
            return VERDE
        pasta = notas[nome].parent.name
        return CORES_PASTA.get(pasta, TINTA_2)

    fig, ax = plt.subplots(figsize=(13, 10))
    ax.set_axis_off()
    ax.grid(False)
    for a, b in arestas:
        ax.plot(*zip(pos[idx[a]], pos[idx[b]]), color=GRADE, lw=0.8, zorder=1)
    for nome in nomes:
        x, y = pos[idx[nome]]
        tamanho = 40 + 18 * grau[nome]
        ax.scatter([x], [y], s=tamanho, color=cor(nome), edgecolor="white", lw=1.5, zorder=2)
        ax.text(x, y - 0.012 - np.sqrt(tamanho) / 900, nome, ha="center", va="top", fontsize=7.5, color=TINTA,
                zorder=3, bbox=dict(boxstyle="round,pad=0.1", fc=SUPERFICIE, ec="none", alpha=0.7))
    for rotulo, c in [("Início / README", VERDE), *[(p, c) for p, c in CORES_PASTA.items()]]:
        ax.scatter([], [], s=80, color=c, label=rotulo)
    ax.legend(loc="upper left", frameon=False, fontsize=10, title="pasta da nota", title_fontsize=10)
    ax.set_title(f"Grafo do vault · {len(nomes)} notas, {len(arestas)} ligações (tamanho = nº de ligações)",
                 fontsize=12, loc="left")
    salvar(fig, "grafo_vault.png")


def main():
    """Gera toda a mídia em assets/."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ASSETS.mkdir(exist_ok=True)
    faltando = [v for v in ("IMG_7457", "IMG_7458", "IMG_7459", "IMG_7460", "IMG_7461")
                if not (SAIDAS / f"{v}_anotado.mp4").exists()]
    if faltando:
        sys.exit(f"Rode antes: python exercicio_mediapipe.py --sem-janela  (faltam saídas de {faltando})")
    print("Ilustrações:")
    for gerar in (mapa_mao, mapa_rosto, regra_dedos, regra_polegar, regra_boca, regra_direcao, figura_aspecto,
                  grafico_boca, grafico_direcao, grafico_suavizacao, miniaturas, grafo_vault):
        gerar()
    print("GIFs:")
    gerar_gifs()


if __name__ == "__main__":
    main()
