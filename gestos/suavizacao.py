"""Suavização temporal (extensão do Exercício 2).

Classificações quadro a quadro oscilam por causa do ruído dos landmarks e de
poses perto do limiar. `FiltroModa` devolve o rótulo mais frequente numa janela
deslizante de N quadros por chave (ex.: "direita:dedos").

Documentação: docs/Módulos/suavizacao.md · docs/Conceitos/Suavização temporal.md
"""

from collections import Counter, deque


class FiltroModa:
    """Mantém os últimos N valores de cada chave e devolve o mais frequente (moda).

    Em empate vence o valor mais recente. Quando a mão/rosto some, a chave deve
    ser zerada com `limpar` para não reaproveitar classificações antigas
    (exigência do Exercício 1).
    """

    def __init__(self, janela: int):
        """Parâmetros:
            janela: número de quadros considerados (mínimo 1; 1 desliga a suavização).
        """
        self.janela = max(1, janela)
        self.historico: dict[str, deque] = {}

    def atualizar(self, chave: str, valor):
        """Registra um novo valor e devolve o valor suavizado.

        Parâmetros:
            chave: identifica a série (ex.: "esquerda:polegar").
            valor: rótulo ou número do quadro atual (precisa ser hashable).

        Retorna:
            A moda dos últimos `janela` valores da chave; em empate, o mais recente.
        """
        fila = self.historico.setdefault(chave, deque(maxlen=self.janela))
        fila.append(valor)
        contagem = Counter(fila)
        maximo = max(contagem.values())
        for candidato in reversed(fila):
            if contagem[candidato] == maximo:
                return candidato
        return valor

    def limpar(self, chave: str) -> None:
        """Descarta o histórico de `chave` (usado quando a mão sai do quadro)."""
        self.historico.pop(chave, None)
