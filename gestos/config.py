"""Configurações centrais: caminhos, modelos e limiares das regras heurísticas.

É o único arquivo a editar durante a calibração. Todos os limiares vêm do
código-base da proposta (ou foram adaptados dele) e são pontos de partida, não
valores universais. Veja docs/Conceitos/Limiares e calibração.md.

Documentação: docs/Módulos/config.md
"""

from pathlib import Path

# --- Caminhos -------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
PASTA_VIDEOS = RAIZ / "Vídeos Exercício mediapipe"   # vídeos gravados (entrada padrão)
PASTA_MODELOS = RAIZ / "modelos"                      # .task baixados automaticamente
PASTA_SAIDAS = RAIZ / "saidas"                        # CSVs e vídeos anotados
PASTA_RESULTADOS_VAULT = RAIZ / "docs" / "Resultados" # notas geradas para o Obsidian
ARQUIVO_ROTULOS = RAIZ / "rotulos.csv"                # gabarito da avaliação

EXTENSOES_VIDEO = {".mov", ".mp4", ".avi", ".mkv", ".m4v"}

# --- Modelos MediaPipe Tasks ---------------------------------------------
MODELOS = {
    "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
}

# --- Detecção -------------------------------------------------------------
MAX_MAOS = 2
MAX_ROSTOS = 1
CONFIANCA_DETECCAO = 0.6       # confiança mínima para aceitar uma mão/rosto novo
CONFIANCA_RASTREAMENTO = 0.5   # abaixo disso o rastreamento é refeito por detecção
LARGURA_MAX_PROCESSAMENTO = 720  # reduz quadros grandes (1080p/4K) antes da detecção

# --- Exercício 1: estado da mão -------------------------------------------
DEDOS_MAO_ABERTA = 4   # >= 4 dedos -> aberta
DEDOS_MAO_FECHADA = 1  # <= 1 dedo  -> fechada

# --- Exercício 2: contagem de dedos -------------------------------------
# "distancia" (invariante à rotação, padrão) ou "vertical" (regra original do código-base).
REGRA_DEDOS = "distancia"
FATOR_POLEGAR_ESTENDIDO = 1.15  # dist(4,5) > dist(3,5) * fator
JANELA_SUAVIZACAO = 7           # quadros usados pela moda temporal

# --- Exercício 3: polegar -----------------------------------------------
# O código-base usa 0.04 em coordenadas normalizadas (depende da distância à câmera).
# Aqui a diferença vertical ponta(4)-articulação(3) é dividida pelo tamanho da mão
# (punho→base do dedo médio), então a margem é relativa: 0.25 = 1/4 do tamanho da mão.
MARGEM_POLEGAR_ESCALA = 0.25

# --- Exercício 4: boca ---------------------------------------------------
LIMIAR_BOCA_ABERTA = 0.15  # proporção altura/largura da boca

# --- Exercício 5: direção do rosto --------------------------------------
LIMIAR_DIRECAO = 0.12            # |desvio do nariz| acima disso -> rosto virado
FAIXA_INDEFINIDA_DIRECAO = 0.03  # |desvio| em [limiar - faixa, limiar + faixa] -> indefinido
