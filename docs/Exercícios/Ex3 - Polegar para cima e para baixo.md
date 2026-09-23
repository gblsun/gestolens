---
tags: [exercicio]
exercicio: 3
---
# Ex3 — Polegar para cima e para baixo

**Objetivo:** identificar 👍 e 👎 e rejeitar outras configurações.

![[ex3_polegar.gif|260]]

![[regra_polegar.png]]

## Regra implementada
[[maos]] → `classificar_polegar(lm, aspecto)` retorna `(rótulo, diferença)`:

1. Se mais de 1 dedo longo está estendido → **Outro gesto**.
2. Se o polegar não está estendido (punho fechado) → **Outro gesto**.
3. `diferença = (y[4] − y[3]) / tamanho_mão`, onde `tamanho_mão = dist(0, 9)` ([[geometria]]).
4. `diferença < −0.25` → **Polegar para cima**; `> +0.25` → **Polegar para baixo**; entre os dois → **Polegar indefinido**.

A margem `MARGEM_POLEGAR_ESCALA` ([[config]]) é **relativa ao tamanho da mão**, ao contrário do `0.04` absoluto do código-base, que muda de significado conforme a distância à câmera. O rótulo é suavizado por [[suavizacao]]; a diferença exibida é a do quadro atual.

## Tarefas da proposta → onde estão
- [x] Testar com as duas mãos e polegar inclinado → lado de cada mão identificado em [[deteccao]] (colunas `esquerda_*` / `direita_*` no CSV).
- [x] Calibrar a margem → `MARGEM_POLEGAR_ESCALA`; a diferença aparece no vídeo e no CSV (`*_polegar_dif`). Ver [[Limiares e calibração]].
- [x] "Outro gesto" quando demais dedos estendidos ou orientação insegura → passos 1, 2 e faixa indefinida.

## Questão para análise
> Por que "esquerda" e "direita" podem mudar quando a imagem é espelhada?

Espelhar inverte o eixo x: a mão direita da pessoa aparece do lado direito da imagem espelhada (como num espelho), mas do lado esquerdo na imagem original. Além disso, o classificador de lateralidade do MediaPipe **assume imagem espelhada**; em vídeo gravado sem espelhar ele devolve o lado trocado, por isso [[deteccao]] inverte o rótulo quando `--espelhar` não é usado. A regra vertical do polegar não é afetada (só usa y). Ver [[Espelhamento]].

Relacionados: [[Landmarks da mão]], [[Ex2 - Contagem de dedos]].
