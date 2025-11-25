#!/usr/bin/env python3
"""
Gera um CSV arrumado e um grafico de linhas a partir de qualquer aba do arquivo
de vagas da Eurostat que siga o layout padrao (primeira coluna geo, colunas por trimestre).

Uso rapido:
    python scripts/gerar_grafico_vagas.py --aba "Sheet 19"

Modo interativo (recomendado para testar):
    python scripts/gerar_grafico_vagas.py --interativo
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import pandas as pd


PAISES_PADRAO = [
    "European Union - 27 countries (from 2020)",
    "Euro area - 20 countries (from 2023)",
    "Germany",
    "France",
    "Spain",
]


def slugificar(nome_aba: str) -> str:
    """Cria um sufixo seguro para nomes de arquivo a partir do nome da aba."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", nome_aba).strip("_").lower()
    return slug or "aba"


def montar_nomes_colunas(linha_cabecalho: Sequence[object]) -> List[str]:
    """
    Propaga os rotulos de trimestre da Eurostat.
    Quando a celula do cabecalho esta vazia, assume que e o flag da coluna anterior.
    """
    colunas: List[str] = []
    for idx, valor in enumerate(linha_cabecalho):
        if idx == 0:
            colunas.append("geo")
            continue
        if pd.isna(valor):
            colunas.append(f"{colunas[-1]}_flag")
        else:
            colunas.append(str(valor))
    return colunas


def carregar_tabela_vagas(
    caminho_excel: Path,
    nome_aba: str,
    linha_cabecalho: int,
    linha_inicio_dados: int,
) -> Tuple[pd.DataFrame, List[str], str | None]:
    """
    Converte a aba da Eurostat em um DataFrame arrumado (geo, trimestre, taxa de vagas).
    Linhas sao indexadas em zero: por padrao, cabecalho na linha 10 e dados a partir da linha 12.
    """
    bruto = pd.read_excel(caminho_excel, sheet_name=nome_aba, header=None)

    area_trabalho: str | None = None
    try:
        celula_area = bruto.iloc[6, 2]
        if pd.notna(celula_area):
            area_trabalho = str(celula_area)
    except Exception:
        area_trabalho = None

    cabecalho = bruto.iloc[linha_cabecalho]
    colunas = montar_nomes_colunas(cabecalho)

    dados = bruto.iloc[linha_inicio_dados:].reset_index(drop=True)
    dados.columns = colunas
    dados = dados[dados["geo"].notna()]

    colunas_valor = [col for col in colunas if col != "geo" and not col.endswith("_flag")]
    arrumado = (
        dados[["geo"] + colunas_valor]
        .replace({":": pd.NA})
        .melt(id_vars="geo", var_name="trimestre", value_name="taxa_vaga")
    )
    arrumado["taxa_vaga"] = pd.to_numeric(arrumado["taxa_vaga"], errors="coerce")
    arrumado = arrumado.dropna(subset=["taxa_vaga"])
    arrumado["trimestre"] = pd.Categorical(arrumado["trimestre"], categories=colunas_valor, ordered=True)
    return arrumado, colunas_valor, area_trabalho


def plotar_taxa_vagas(
    dados_arrumados: pd.DataFrame,
    ordem_trimestres: Sequence[str],
    paises: Iterable[str],
    nome_aba: str,
    caminho_saida: Path,
) -> None:
    """Desenha o grafico de linhas para os paises escolhidos."""
    paises = list(paises)
    recorte = dados_arrumados[dados_arrumados["geo"].isin(paises)].copy()
    if recorte.empty:
        raise ValueError("Nenhuma linha encontrada para os paises informados.")

    recorte = recorte.sort_values(["geo", "trimestre"])
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    for geo, grupo in recorte.groupby("geo"):
        ax.plot(grupo["trimestre"].astype(str), grupo["taxa_vaga"], marker="o", label=geo)

    ax.set_title(f"Taxa de vagas de trabalho - {nome_aba}")
    ax.set_ylabel("Taxa de vagas (%)")
    ax.set_xlabel("Trimestre")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=300)
    plt.close(fig)


def solicitar_int(msg: str, padrao: int) -> int:
    """Pergunta um inteiro no terminal, aceitando Enter como default."""
    entrada = input(f"{msg} [{padrao}]: ").strip()
    if entrada == "":
        return padrao
    try:
        return int(entrada)
    except ValueError:
        print("Valor invalido, usando padrao.")
        return padrao


def solicitar_lista_paises(padrao: List[str]) -> List[str]:
    """Pergunta lista de geos separada por virgula ou ponto-e-virgula."""
    entrada = input(
        "Quais geos deseja plotar? Separe por virgula ou ponto-e-virgula "
        f"(Enter para padrao: {', '.join(padrao)}): "
    ).strip()
    if entrada == "":
        return padrao
    separador = ";" if ";" in entrada else ","
    return [parte.strip() for parte in entrada.split(separador) if parte.strip()]


def listar_abas_excel(caminho_excel: Path) -> List[str]:
    """Retorna as abas disponiveis no XLSX."""
    with pd.ExcelFile(caminho_excel) as xls:
        return list(xls.sheet_names)


def mostrar_resumo(
    dados_arrumados: pd.DataFrame,
    ordem_trimestres: Sequence[str],
    nome_aba: str,
    area_trabalho: str | None,
) -> None:
    """Mostra um pequeno resumo da aba escolhida."""
    geos = list(dados_arrumados["geo"].unique())
    exemplo_geo = geos[:5]
    trimestres = list(ordem_trimestres)
    print("\nResumo da aba selecionada")
    print("-------------------------")
    print(f"Aba: {nome_aba}")
    if area_trabalho:
        print(f"Area (celula C7): {area_trabalho}")
    print(f"Total de geos: {len(geos)} (ex.: {', '.join(exemplo_geo)})")
    print(f"Total de trimestres: {len(trimestres)} (primeiros: {', '.join(trimestres[:4])})")
    print(
        f"Intervalo de taxa_vaga: min={dados_arrumados['taxa_vaga'].min():.2f} "
        f"| max={dados_arrumados['taxa_vaga'].max():.2f}"
    )
    print()


def fluxo_interativo(caminho_excel: Path) -> None:
    """Pergunta aba/parametros no terminal e gera CSV + PNG."""
    if not caminho_excel.exists():
        raise SystemExit(f"Arquivo nao encontrado: {caminho_excel}")

    abas = listar_abas_excel(caminho_excel)
    if not abas:
        raise SystemExit("Nenhuma aba encontrada no XLSX.")

    print("Abas encontradas no arquivo:")
    for idx, aba in enumerate(abas, start=1):
        print(f"  [{idx}] {aba}")

    escolha = input("Digite o numero da aba que deseja usar: ").strip()
    try:
        idx_escolhido = int(escolha) - 1
        nome_aba = abas[idx_escolhido]
    except (ValueError, IndexError):
        raise SystemExit("Escolha invalida. Execute novamente e selecione um numero da lista.")

    slug_aba = slugificar(nome_aba)
    caminho_csv = Path("PowerBI") / f"tabela_vagas_{slug_aba}.csv"
    caminho_grafico = Path("plots") / f"grafico_vagas_{slug_aba}.png"

    dados_arrumados, ordem_trimestres, area_trabalho = carregar_tabela_vagas(
        caminho_excel=caminho_excel,
        nome_aba=nome_aba,
        linha_cabecalho=10,
        linha_inicio_dados=12,
    )

    faltantes = [geo for geo in PAISES_PADRAO if geo not in dados_arrumados["geo"].unique()]
    if faltantes:
        print(f"Aviso: estes geos nao foram encontrados e serao ignorados: {', '.join(faltantes)}")
    paises_validos = [geo for geo in PAISES_PADRAO if geo in dados_arrumados["geo"].unique()]
    if not paises_validos:
        raise SystemExit("Nenhum geo valido restou para plotar. Ajuste os nomes e tente de novo.")

    mostrar_resumo(dados_arrumados, ordem_trimestres, nome_aba, area_trabalho)

    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    dados_arrumados.to_csv(caminho_csv, index=False)
    print(f"Tabela arrumada salva em {caminho_csv}")

    plotar_taxa_vagas(dados_arrumados, ordem_trimestres, paises_validos, nome_aba, caminho_grafico)
    print(f"Grafico salvo em {caminho_grafico}")


def receber_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera CSV arrumado e grafico de vagas a partir de qualquer aba no layout Eurostat."
    )
    parser.add_argument(
        "--caminho-excel",
        type=Path,
        default=Path("data") / "job_vacancies.xlsx",
        help="Caminho do arquivo XLSX baixado da Eurostat.",
    )
    parser.add_argument(
        "--aba",
        default="Sheet 19",
        help="Nome da aba que segue o layout original (primeira coluna geo, demais trimestres).",
    )
    parser.add_argument(
        "--paises",
        nargs="+",
        default=PAISES_PADRAO,
        help="Rotulos de geo a exibir no grafico.",
    )
    parser.add_argument(
        "--linha-cabecalho",
        type=int,
        default=10,
        help="Indice (zero-based) da linha do cabecalho onde estao os trimestres.",
    )
    parser.add_argument(
        "--linha-dados",
        type=int,
        default=12,
        help="Indice (zero-based) da primeira linha com dados de pais.",
    )
    parser.add_argument(
        "--saida-csv",
        type=Path,
        help="Caminho opcional do CSV arrumado. Se omitido, sera salvo em PowerBI/tabela_vagas_<aba>.csv.",
    )
    parser.add_argument(
        "--saida-grafico",
        type=Path,
        help="Caminho opcional do grafico. Se omitido, sera salvo em plots/grafico_vagas_<aba>.png.",
    )
    parser.add_argument(
        "--sem-csv",
        action="store_true",
        help="Nao salvar o CSV arrumado.",
    )
    parser.add_argument(
        "--sem-grafico",
        action="store_true",
        help="Nao salvar o grafico.",
    )
    parser.add_argument(
        "--interativo",
        action="store_true",
        help="Pergunta a aba e parametros pelo terminal, gera CSV e grafico automaticamente.",
    )
    return parser.parse_args()


def fluxo_argumentos(args: argparse.Namespace) -> None:
    """Mantem o modo antigo parametrizado por argumentos."""
    slug_aba = slugificar(args.aba)
    caminho_csv = args.saida_csv or (Path("PowerBI") / f"tabela_vagas_{slug_aba}.csv")
    caminho_grafico = args.saida_grafico or (Path("plots") / f"grafico_vagas_{slug_aba}.png")

    dados_arrumados, ordem_trimestres, _ = carregar_tabela_vagas(
        caminho_excel=args.caminho_excel,
        nome_aba=args.aba,
        linha_cabecalho=args.linha_cabecalho,
        linha_inicio_dados=args.linha_dados,
    )

    faltantes = [geo for geo in args.paises if geo not in dados_arrumados["geo"].unique()]
    if faltantes:
        print(f"Aviso: estes geos nao foram encontrados e serao ignorados: {', '.join(faltantes)}")

    paises_validos = [geo for geo in args.paises if geo in dados_arrumados["geo"].unique()]
    if not paises_validos:
        raise SystemExit("Nenhum geo valido restou para plotar. Ajuste os nomes e tente de novo.")

    if not args.sem_csv:
        caminho_csv.parent.mkdir(parents=True, exist_ok=True)
        dados_arrumados.to_csv(caminho_csv, index=False)
        print(f"Tabela arrumada salva em {caminho_csv}")

    if not args.sem_grafico:
        plotar_taxa_vagas(dados_arrumados, ordem_trimestres, paises_validos, args.aba, caminho_grafico)
        print(f"Grafico salvo em {caminho_grafico}")


def main() -> None:
    args = receber_argumentos()
    if args.interativo:
        fluxo_interativo(args.caminho_excel)
    else:
        fluxo_argumentos(args)


if __name__ == "__main__":
    main()
