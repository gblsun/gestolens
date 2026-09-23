"""Detecção de landmarks de mão e rosto com a API MediaPipe Tasks (modo VIDEO).

Papel no fluxo
--------------
Recebe um quadro BGR e o seu instante e devolve um `ResultadoDeteccao` com:
- até 2 mãos (21 landmarks cada) e o lado real de cada mão da pessoa;
- 1 rosto (478 landmarks) e a matriz 4x4 de transformação facial, usada na pose.

O modo VIDEO rastreia os landmarks entre quadros, o que é mais estável e mais
rápido que detectar do zero a cada quadro, mas exige instantes crescentes.
Por isso cada vídeo ganha um `Detector` novo.

Documentação: docs/Módulos/deteccao.md · docs/Conceitos/MediaPipe Tasks.md
"""

from dataclasses import dataclass, field

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

from . import config
from .modelos import garantir_modelo

LADO_OPOSTO = {"Left": "Right", "Right": "Left"}
LADO_PT = {"Left": "esquerda", "Right": "direita"}


@dataclass
class MaoDetectada:
    """Uma mão encontrada no quadro.

    Atributos:
        landmarks: 21 `NormalizedLandmark` (x, y em [0, 1]; z relativo ao punho).
        lado: "esquerda" ou "direita" (a mão da pessoa, já corrigida pelo espelhamento).
        confianca_lado: confiança do classificador de lateralidade (0 a 1).
    """

    landmarks: list
    lado: str
    confianca_lado: float


@dataclass
class ResultadoDeteccao:
    """Tudo o que foi detectado em um quadro.

    Atributos:
        maos: mãos detectadas (lista vazia se nenhuma).
        rosto: 478 landmarks do rosto, ou None.
        matriz_rosto: matriz 4x4 de transformação facial, ou None.
    """

    maos: list[MaoDetectada] = field(default_factory=list)
    rosto: list | None = None
    matriz_rosto: np.ndarray | None = None


class Detector:
    """Encapsula HandLandmarker e FaceLandmarker em modo VIDEO.

    Parâmetros:
        imagem_espelhada: True se os quadros chegam espelhados (webcam em modo selfie).
            Isso é usado para corrigir o rótulo de lateralidade.

    Use como gerenciador de contexto para liberar os recursos nativos:

        with Detector(imagem_espelhada=False) as detector:
            resultado = detector.processar(imagem, timestamp_ms)
    """

    def __init__(self, imagem_espelhada: bool):
        # O MediaPipe rotula a lateralidade supondo imagem espelhada (selfie).
        # Em vídeo não espelhado o rótulo sai invertido e precisa ser trocado.
        self.imagem_espelhada = imagem_espelhada

        # Os modelos são passados como bytes porque o MediaPipe não abre caminhos
        # com acentos no Windows (ex.: "expressões").
        opcoes_mao = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_buffer=garantir_modelo("hand_landmarker.task").read_bytes()),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=config.MAX_MAOS,
            min_hand_detection_confidence=config.CONFIANCA_DETECCAO,
            min_hand_presence_confidence=config.CONFIANCA_DETECCAO,
            min_tracking_confidence=config.CONFIANCA_RASTREAMENTO,
        )
        opcoes_rosto = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_buffer=garantir_modelo("face_landmarker.task").read_bytes()),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=config.MAX_ROSTOS,
            min_face_detection_confidence=config.CONFIANCA_DETECCAO,
            min_face_presence_confidence=config.CONFIANCA_DETECCAO,
            min_tracking_confidence=config.CONFIANCA_RASTREAMENTO,
            output_facial_transformation_matrixes=True,
        )
        self.detector_maos = vision.HandLandmarker.create_from_options(opcoes_mao)
        self.detector_rosto = vision.FaceLandmarker.create_from_options(opcoes_rosto)

    def processar(self, imagem_bgr, timestamp_ms: int) -> ResultadoDeteccao:
        """Detecta mãos e rosto em um quadro.

        Parâmetros:
            imagem_bgr: quadro no formato do OpenCV (BGR).
            timestamp_ms: instante do quadro; precisa ser maior que o da chamada anterior.

        Retorna:
            `ResultadoDeteccao` com mãos, rosto e matriz facial.
        """
        rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)
        imagem_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))

        res_maos = self.detector_maos.detect_for_video(imagem_mp, timestamp_ms)
        res_rosto = self.detector_rosto.detect_for_video(imagem_mp, timestamp_ms)

        resultado = ResultadoDeteccao()
        for landmarks, lateralidade in zip(res_maos.hand_landmarks, res_maos.handedness):
            categoria = lateralidade[0]
            rotulo = categoria.category_name
            if not self.imagem_espelhada:
                rotulo = LADO_OPOSTO.get(rotulo, rotulo)
            resultado.maos.append(MaoDetectada(landmarks, LADO_PT.get(rotulo, rotulo), categoria.score))

        if res_rosto.face_landmarks:
            resultado.rosto = res_rosto.face_landmarks[0]
            if res_rosto.facial_transformation_matrixes:
                resultado.matriz_rosto = np.asarray(res_rosto.facial_transformation_matrixes[0])
        return resultado

    def fechar(self) -> None:
        """Libera os recursos nativos dos dois detectores."""
        self.detector_maos.close()
        self.detector_rosto.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.fechar()
