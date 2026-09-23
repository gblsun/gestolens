"""GestoLens: reconhecimento de gestos e expressões com MediaPipe Tasks e OpenCV.

Pacote com as etapas do pipeline (ver gestos/README.md para o mapa ilustrado):

    fonte_video → deteccao → analise (classificadores + suavizacao) → registro / desenho → avaliacao

Módulos:
    config          limiares, caminhos e URLs dos modelos
    modelos         download dos arquivos .task
    fonte_video     leitura de arquivos de vídeo e da webcam
    deteccao        HandLandmarker e FaceLandmarker em modo VIDEO
    geometria       distâncias e regras de dedo estendido
    classificadores regras dos exercícios 1 a 5 (maos.py, rosto.py)
    suavizacao      filtro de moda temporal
    analise         aplica classificadores e suavização a um quadro
    desenho         sobreposição visual
    registro        CSV por quadro, resumo e notas do Obsidian
    avaliacao       compara com o gabarito rotulos.csv
    pipeline        laço principal

Documentação detalhada: docs/Módulos (vault do Obsidian).
"""

__version__ = "1.0.0"
