---
tags: [exercicio]
exercicio: 4
---
# Ex4 — Boca aberta e boca fechada

**Objetivo:** estimar se a boca está aberta pela razão abertura/largura.

![[ex4_boca.gif|260]]

![[regra_boca.png]]

![[grafico_boca.png]]

## Regra implementada
[[rosto]] → `classificar_boca(lm, aspecto)` retorna `(rótulo, proporção)`:

```
altura  = dist(13, 14)   # lábios internos superior e inferior
largura = dist(61, 291)  # cantos da boca
proporção = altura / largura
proporção > LIMIAR_BOCA_ABERTA (0.15) → Boca aberta, senão Boca fechada
```

Índices em [[Landmarks do rosto]]. As distâncias usam a correção de [[Proporção da imagem]]: sem ela, num vídeo em retrato a largura (eixo x) ficaria subestimada e a proporção inflada em ~1,8×.

## Tarefas da proposta → onde estão
- [x] Mostrar a proporção na imagem → [[desenho]] exibe `(prop 0.xx)`; o CSV guarda `proporcao_boca`.
- [x] Coletar fechada / ligeiramente aberta / bem aberta e justificar o limiar → usar a coluna `proporcao_boca` dos trechos rotulados; ver [[Limiares e calibração]].
- [x] Fala, sorriso, rosto inclinado, distâncias → gravar trechos, rotular com `ex4` e ler falsos positivos/negativos em [[Avaliação]].

## Observações
- Boca fechada nos vídeos: proporção ≈ 0,01–0,02 (IMG_7459). O limiar 0,15 deixa folga grande; bocejos e fala forte passam de 0,3.
- **Sorriso** aumenta a largura → reduz a proporção (falso negativo para "aberta").
- **Fala** oscila rapidamente → candidatos a [[Suavização temporal]].
- Rosto de perfil comprime a largura em 2D → falso positivo.

> [!warning] O valor 0.15 é ponto de partida, não um limiar universal.
