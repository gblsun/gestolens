---
tags: [exercicio]
exercicio: 1
---
# Ex1 — Mão aberta e mão fechada

**Objetivo:** classificar cada mão como *aberta*, *fechada* ou *parcialmente aberta*.

![[ex1_mao.gif|260]]

## Regra implementada
Em [[maos]] → `classificar_mao(quantidade_dedos)`, a partir da contagem de [[Ex2 - Contagem de dedos]] já suavizada:

| Dedos | Estado |
|---|---|
| ≥ `DEDOS_MAO_ABERTA` (4) | Mao aberta |
| ≤ `DEDOS_MAO_FECHADA` (1) | Mao fechada |
| 2–3 | Mao parcialmente aberta |
| mão ausente | Mao nao detectada |

O estado é calculado **a partir da contagem suavizada**, então o número e o estado exibidos nunca se contradizem.

## Tarefas da proposta → onde estão
- [x] Testar palma de frente, inclinada e dedos semi-dobrados → vídeos em `Vídeos Exercício mediapipe/`, resultados em [[Resultados]].
- [x] Ajustar limites → `DEDOS_MAO_ABERTA` / `DEDOS_MAO_FECHADA` em [[config]].
- [x] "Mão não detectada" sem reaproveitar o quadro anterior → [[analise]] limpa o histórico do [[suavizacao|filtro]] quando a mão some; [[desenho]] escreve "Mao nao detectada".

## Questão para análise
> Em quais condições a contagem de dedos deixa de representar o estado aberto/fechado?

- Mão de lado (perfil): os dedos se sobrepõem, landmarks ocultos são "adivinhados" pelo modelo.
- Mão deitada ou invertida com a regra **vertical** do código-base: dedos dobrados ficam com a ponta "acima" da articulação e contam como estendidos. Observado em IMG_7459 (polegar para baixo contado como 3 dedos). Motivou a regra por distância ao punho — ver [[geometria]].
- Gestos como "V" ou apontar: 2 dedos → "parcial", embora não seja uma mão semiaberta.
- Oclusão por objeto ou pela outra mão; mão cortada pela borda do quadro.

Relacionados: [[Landmarks da mão]], [[Limiares e calibração]], [[Limitações]].
