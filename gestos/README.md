# 📦 `gestos/`: o pipeline do GestoLens

Este pacote transforma quadros de vídeo em rótulos ("Mao aberta", "Polegar para cima", "Boca aberta"…). Cada arquivo cuida de **uma** etapa, e todas as decisões ajustáveis ficam em [`config.py`](config.py).

![Demonstração do pipeline](../assets/demo.gif)

← voltar ao [README principal](../README.md)

---

## Mapa de dependências

Quem importa quem. As setas vão de quem **usa** para quem **é usado**:

```mermaid
graph TD
    CLI["exercicio_mediapipe.py<br/><i>menu + CLI</i>"] --> P[pipeline]
    CLI --> RG[registro]
    CLI --> AV[avaliacao]
    CLI --> FV[fonte_video]

    P --> FV
    P --> DT[deteccao]
    P --> AN[analise]
    P --> DE[desenho]
    P --> RG

    DT --> MO[modelos]
    AN --> CM["classificadores/maos"]
    AN --> CR["classificadores/rosto"]
    AN --> SU[suavizacao]
    CM --> GE[geometria]
    CR --> GE
    DE --> AN
    RG --> AN
    AV --> CM
    AV --> CR

    CF[(config)]:::cfg
    FV -.-> CF
    DT -.-> CF
    CM -.-> CF
    CR -.-> CF
    AN -.-> CF
    MO -.-> CF

    classDef cfg fill:#fff4d6,stroke:#eda100
```

**Como ler:** `config` (em amarelo) é consultado por quase todos e não depende de ninguém: é o único lugar a editar para calibrar. `classificadores` só conhecem `geometria` e `config`, então são funções puras (landmarks entram, rótulos saem) e podem ser testadas sem vídeo nenhum.

---

## O caminho de um quadro

```mermaid
sequenceDiagram
    autonumber
    participant F as fonte_video
    participant P as pipeline
    participant D as deteccao
    participant A as analise
    participant C as classificadores
    participant S as suavizacao
    participant R as registro
    participant G as desenho

    F->>P: Quadro(indice, timestamp_ms, imagem BGR)
    P->>P: reduz para 720 px · espelha (webcam)
    P->>D: processar(imagem, timestamp_ms)
    D-->>P: ResultadoDeteccao(maos[lado, 21 pts], rosto[478 pts], matriz 4x4)
    P->>A: analisar(indice, ts, deteccao)
    loop cada mão
        A->>C: contar_dedos · classificar_polegar
        A->>S: atualizar("direita:dedos", n)
        S-->>A: moda dos últimos 7
        A->>C: classificar_mao(n suavizado)
    end
    A->>C: classificar_boca · classificar_direcao_rosto · estimar_pose
    A-->>P: AnaliseQuadro
    P->>R: adicionar(analise) → linha no CSV
    P->>G: desenhar_analise(imagem, analise)
    P->>P: imshow / VideoWriter
```

**Pontos-chave, pela numeração:**
- **(1)** O `timestamp_ms` é **estritamente crescente**. No arquivo vem de `índice / fps`; na webcam vem do relógio.
- **(4)** O `lado` da mão já vem corrigido. O MediaPipe presume imagem espelhada, e o `Detector` inverte o rótulo quando a imagem não é espelhada. Detalhes em [Espelhamento](../docs/Conceitos/Espelhamento.md).
- **(7–8)** A suavização tem uma chave por mão. Quando a mão some, a chave é apagada: o Ex1 mostra "Mao nao detectada" e nunca reaproveita o quadro anterior.
- **(9)** O estado da mão é calculado **a partir da contagem já suavizada**, então o número e o estado exibidos nunca se contradizem.

---

## Os dados que circulam

```mermaid
classDiagram
    direction LR
    class Quadro {
      indice: int
      timestamp_ms: int
      imagem: BGR
    }
    class ResultadoDeteccao {
      maos: list~MaoDetectada~
      rosto: 478 landmarks ou None
      matriz_rosto: 4x4 ou None
    }
    class MaoDetectada {
      landmarks: 21
      lado: esquerda ou direita
      confianca_lado: float
    }
    class AnaliseQuadro {
      indice, timestamp_ms
      maos: list~AnaliseMao~
      rosto: AnaliseRosto ou None
    }
    class AnaliseMao {
      lado
      dedos_bruto, dedos
      estado, polegar, polegar_diferenca
    }
    class AnaliseRosto {
      boca, proporcao_boca
      direcao, desvio_nariz
      yaw, pitch, roll
    }
    Quadro --> ResultadoDeteccao : deteccao
    ResultadoDeteccao *-- MaoDetectada
    ResultadoDeteccao --> AnaliseQuadro : analise
    AnaliseQuadro *-- AnaliseMao
    AnaliseQuadro *-- AnaliseRosto
```

---

## Módulo a módulo

| Arquivo | Responsabilidade | Principais nomes | Nota no vault |
|---|---|---|---|
| [`config.py`](config.py) | caminhos, URLs dos modelos, **todos os limiares** | `LIMIAR_BOCA_ABERTA`, `REGRA_DEDOS`… | [config](../docs/Módulos/config.md) |
| [`modelos.py`](modelos.py) | baixa os `.task` na primeira execução | `garantir_modelo` | [modelos](../docs/Módulos/modelos.md) |
| [`fonte_video.py`](fonte_video.py) | lê arquivo ou webcam, aplica a rotação do `.MOV` e gera os instantes | `FonteVideo`, `Quadro`, `listar_videos` | [fonte_video](../docs/Módulos/fonte_video.md) |
| [`deteccao.py`](deteccao.py) | HandLandmarker + FaceLandmarker em modo VIDEO; corrige a lateralidade | `Detector`, `ResultadoDeteccao` | [deteccao](../docs/Módulos/deteccao.md) |
| [`geometria.py`](geometria.py) | distâncias com correção de aspecto; regras de dedo estendido | `distancia`, `dedos_longos_estendidos` | [geometria](../docs/Módulos/geometria.md) |
| [`classificadores/`](classificadores/README.md) | regras dos exercícios 1–5 | `contar_dedos`, `classificar_boca`… | [maos](../docs/Módulos/maos.md) · [rosto](../docs/Módulos/rosto.md) |
| [`suavizacao.py`](suavizacao.py) | moda temporal por chave | `FiltroModa` | [suavizacao](../docs/Módulos/suavizacao.md) |
| [`analise.py`](analise.py) | aplica classificadores e suavização a um quadro | `Analisador`, `AnaliseQuadro` | [analise](../docs/Módulos/analise.md) |
| [`desenho.py`](desenho.py) | esqueleto da mão, pontos do rosto, painel de texto | `desenhar_analise` | [desenho](../docs/Módulos/desenho.md) |
| [`registro.py`](registro.py) | CSV por quadro, `resumo.csv`, notas de resultado | `RegistroVideo`, `salvar_resumo` | [registro](../docs/Módulos/registro.md) |
| [`avaliacao.py`](avaliacao.py) | compara com `rotulos.csv` | `avaliar`, `Placar` | [avaliacao](../docs/Módulos/avaliacao.md) |
| [`pipeline.py`](pipeline.py) | laço principal, janela e gravação | `processar_fonte`, `OpcoesPipeline` | [pipeline](../docs/Módulos/pipeline.md) |

Todas as funções e classes têm docstring em português, com **Parâmetros / Retorna / Levanta**. Use `help(gestos.analise.Analisador)` no Python para ler.

---

## Uma armadilha escondida: a proporção da imagem

![Uma célula 0,1 × 0,1 normalizada vira um retângulo alto em pixels](../assets/aspecto.png)

O MediaPipe devolve `x` dividido pela **largura** e `y` dividido pela **altura**. Num vídeo em retrato (1080×1920), 0,1 em x são 108 px, mas 0,1 em y são 192 px. Qualquer distância "diagonal" calculada direto nas coordenadas normalizadas sai distorcida. A proporção da boca, por exemplo, sairia ~1,8× maior. Por isso `geometria.distancia` recebe `aspecto = largura / altura` e corrige Δx. Mais em [Proporção da imagem](../docs/Conceitos/Proporção%20da%20imagem.md).

---

## Usar o pacote no seu código

```python
from gestos.fonte_video import FonteVideo
from gestos.deteccao import Detector
from gestos.analise import Analisador

with FonteVideo(0) as fonte, Detector(imagem_espelhada=True) as detector:   # 0 = webcam
    analisador = None
    for quadro in fonte.quadros():
        imagem = quadro.imagem[:, ::-1].copy()                              # espelha
        h, w = imagem.shape[:2]
        analisador = analisador or Analisador(aspecto=w / h)
        analise = analisador.analisar(quadro.indice, quadro.timestamp_ms,
                                      detector.processar(imagem, quadro.timestamp_ms))
        for mao in analise.maos:
            print(mao.lado, mao.dedos, mao.estado, mao.polegar)
```
