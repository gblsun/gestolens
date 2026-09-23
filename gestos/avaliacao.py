"""Protocolo de testes: compara as saídas por quadro com o gabarito em rotulos.csv.

Formato de rotulos.csv (uma linha por trecho de vídeo):
    video,inicio_s,fim_s,exercicio,lado,rotulo_esperado
    IMG_7457,0.0,3.5,ex2,direita,3

- exercicio: ex1 (estado da mão), ex2 (dedos), ex3 (polegar), ex4 (boca), ex5 (direção)
- lado: esquerda | direita | vazio (qualquer mão serve) — ignorado em ex4/ex5
- rotulo_esperado: rótulo completo ou apelido curto (ver APELIDOS)

Critério por quadro dentro de um trecho rotulado:
- acerto: alguma previsão (da mão indicada, ou de qualquer mão) é igual ao esperado;
- indefinido: todas as previsões são indefinidas ou "não detectado";
- erro: caso contrário. O par (esperado, previsto) entra na tabela de confusões.

A acurácia é calculada só sobre os quadros decididos (acertos + erros). A taxa
de indefinidos mostra a cobertura.

Documentação: docs/Módulos/avaliacao.md · docs/Avaliação/Protocolo de testes.md
"""

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .classificadores import maos as cm
from .classificadores import rosto as cr

COLUNA_POR_EXERCICIO = {"ex1": "estado", "ex2": "dedos", "ex3": "polegar", "ex4": "boca", "ex5": "direcao"}
NOTA_POR_EXERCICIO = {
    "ex1": "Ex1 - Mão aberta e fechada",
    "ex2": "Ex2 - Contagem de dedos",
    "ex3": "Ex3 - Polegar para cima e para baixo",
    "ex4": "Ex4 - Boca aberta e fechada",
    "ex5": "Ex5 - Direção do rosto",
}
APELIDOS = {
    "ex1": {"aberta": cm.MAO_ABERTA, "fechada": cm.MAO_FECHADA, "parcial": cm.MAO_PARCIAL},
    "ex3": {"cima": cm.POLEGAR_CIMA, "baixo": cm.POLEGAR_BAIXO, "outro": cm.OUTRO_GESTO},
    "ex4": {"aberta": cr.BOCA_ABERTA, "fechada": cr.BOCA_FECHADA},
    "ex5": {"frente": cr.ROSTO_FRENTE, "esquerda": cr.ROSTO_ESQUERDA, "direita": cr.ROSTO_DIREITA},
}
INDEFINIDOS = {
    "", cm.MAO_NAO_DETECTADA, cm.POLEGAR_INDEFINIDO,
    cr.BOCA_INDEFINIDA, cr.DIRECAO_INDEFINIDA, cr.ROSTO_NAO_DETECTADO,
}


@dataclass
class Placar:
    """Contagem de acertos, erros e indefinidos de um exercício."""

    acertos: int = 0
    erros: int = 0
    indefinidos: int = 0
    confusoes: Counter = field(default_factory=Counter)  # (esperado, previsto) -> quadros

    @property
    def total(self) -> int:
        """Quadros avaliados (acertos + erros + indefinidos)."""
        return self.acertos + self.erros + self.indefinidos

    @property
    def acuracia(self) -> float | None:
        """Acertos entre os quadros em que o sistema tomou uma decisão."""
        decididos = self.acertos + self.erros
        return self.acertos / decididos if decididos else None


def ler_rotulos(caminho: Path) -> list[dict]:
    """Lê o gabarito ignorando linhas vazias e comentários (#)."""
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        linhas = [l for l in csv.DictReader(arquivo) if l.get("video") and not l["video"].startswith("#")]
    return linhas


def _esperado(exercicio: str, rotulo: str) -> str:
    """Troca um apelido (ex.: "cima") pelo rótulo completo do classificador."""
    rotulo = rotulo.strip()
    return APELIDOS.get(exercicio, {}).get(rotulo.lower(), rotulo)


def _previstos(linha: dict, exercicio: str, lado: str) -> list[str]:
    """Lê do CSV as previsões relevantes para o exercício (uma por mão, ou a do rosto)."""
    coluna = COLUNA_POR_EXERCICIO[exercicio]
    if exercicio in ("ex4", "ex5"):
        return [linha[coluna]]
    lados = [lado] if lado else ["esquerda", "direita"]
    return [linha[f"{l}_{coluna}"] for l in lados]


def avaliar(pasta_saidas: Path, caminho_rotulos: Path) -> dict[str, Placar]:
    """Cruza cada trecho rotulado com os quadros do CSV correspondente.

    Parâmetros:
        pasta_saidas: pasta com os `<video>.csv` gerados pelo pipeline.
        caminho_rotulos: gabarito no formato descrito no topo do módulo.

    Retorna:
        Dicionário exercício ("ex1".."ex5") → `Placar`.
    """
    placares: dict[str, Placar] = defaultdict(Placar)
    cache: dict[str, list[dict]] = {}

    for rotulo in ler_rotulos(caminho_rotulos):
        video = Path(rotulo["video"].strip()).stem
        if video not in cache:
            caminho_csv = pasta_saidas / f"{video}.csv"
            if not caminho_csv.exists():
                print(f"Aviso: {caminho_csv} não existe — processe o vídeo antes de avaliar.")
                cache[video] = []
            else:
                with open(caminho_csv, newline="", encoding="utf-8") as arquivo:
                    cache[video] = list(csv.DictReader(arquivo))

        exercicio = rotulo["exercicio"].strip().lower()
        esperado = _esperado(exercicio, rotulo["rotulo_esperado"])
        lado = (rotulo.get("lado") or "").strip().lower()
        inicio, fim = float(rotulo["inicio_s"]), float(rotulo["fim_s"])
        placar = placares[exercicio]

        for linha in cache[video]:
            if not inicio <= float(linha["t_s"]) <= fim:
                continue
            previstos = _previstos(linha, exercicio, lado)
            if esperado in previstos:
                placar.acertos += 1
            elif all(p in INDEFINIDOS for p in previstos):
                placar.indefinidos += 1
            else:
                placar.erros += 1
                decidido = next(p for p in previstos if p not in INDEFINIDOS)
                placar.confusoes[(esperado, decidido)] += 1
    return dict(placares)


def gerar_relatorio(placares: dict[str, Placar], pasta_saidas: Path,
                    pasta_vault: Path = config.PASTA_RESULTADOS_VAULT) -> Path:
    """Grava saidas/avaliacao.csv e a nota docs/Resultados/Avaliação.md.

    Parâmetros:
        placares: saída de `avaliar`.
        pasta_saidas: onde gravar o CSV.
        pasta_vault: onde gravar a nota Markdown.

    Retorna:
        Caminho da nota gerada.
    """
    with open(pasta_saidas / "avaliacao.csv", "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["exercicio", "quadros", "acertos", "erros", "indefinidos", "acuracia"])
        for ex, p in sorted(placares.items()):
            escritor.writerow([ex, p.total, p.acertos, p.erros, p.indefinidos,
                               "" if p.acuracia is None else f"{p.acuracia:.3f}"])

    partes = [
        "---", "tags: [resultado, avaliacao]", "---",
        "# Avaliação",
        "",
        "Gerado por [[avaliacao]] a partir de `rotulos.csv`. Metodologia em [[Protocolo de testes]] "
        "e [[Como preencher rotulos.csv]].",
        "",
        "| Exercício | Quadros | Acertos | Erros | Indefinidos | Acurácia (decididos) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for ex, p in sorted(placares.items()):
        acc = "—" if p.acuracia is None else f"{100 * p.acuracia:.1f}%"
        partes.append(f"| [[{NOTA_POR_EXERCICIO.get(ex, ex)}]] | {p.total} | {p.acertos} | {p.erros} | {p.indefinidos} | {acc} |")
    partes.append("")

    for ex, p in sorted(placares.items()):
        if not p.confusoes:
            continue
        partes += [f"## Erros — {ex}", "", "| Esperado | Previsto | Quadros |", "|---|---|---:|"]
        for (esperado, previsto), n in p.confusoes.most_common():
            partes.append(f"| {esperado} | {previsto} | {n} |")
        partes.append("")

    pasta_vault.mkdir(parents=True, exist_ok=True)
    caminho = pasta_vault / "Avaliação.md"
    caminho.write_text("\n".join(partes), encoding="utf-8")
    return caminho
