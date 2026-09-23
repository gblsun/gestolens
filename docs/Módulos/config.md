---
tags: [modulo]
arquivo: gestos/config.py
---
# config

`gestos/config.py` · voltar ao [[Início]]

Parâmetros centrais: caminhos, URLs dos modelos e **todos os limiares** das regras. É o único lugar a editar durante a [[Limiares e calibração|calibração]].

| Constante | Valor | Usado em |
|---|---|---|
| `LARGURA_MAX_PROCESSAMENTO` | 720 | [[pipeline]] |
| `CONFIANCA_DETECCAO` / `_RASTREAMENTO` | 0.6 / 0.5 | [[deteccao]] |
| `DEDOS_MAO_ABERTA` / `_FECHADA` | 4 / 1 | [[Ex1 - Mão aberta e fechada]] |
| `REGRA_DEDOS` | "distancia" | [[Ex2 - Contagem de dedos]] |
| `FATOR_POLEGAR_ESTENDIDO` | 1.15 | [[Ex2 - Contagem de dedos]] |
| `JANELA_SUAVIZACAO` | 7 | [[suavizacao]] |
| `MARGEM_POLEGAR_ESCALA` | 0.25 | [[Ex3 - Polegar para cima e para baixo]] |
| `LIMIAR_BOCA_ABERTA` | 0.15 | [[Ex4 - Boca aberta e fechada]] |
| `LIMIAR_DIRECAO` / `FAIXA_INDEFINIDA_DIRECAO` | 0.12 / 0.03 | [[Ex5 - Direção do rosto]] |
