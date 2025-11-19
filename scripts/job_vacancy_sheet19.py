#!/usr/bin/env python3
"""
Ferramenta simples para extrair a planilha 19 do ficheiro da Eurostat e gerar um gráfico.

Uso recomendado:
    python scripts/job_vacancy_sheet19.py \
        --excel-path data/job_vacancies.xlsx \
        --output plots/sheet19_job_vacancies.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_COUNTRIES = [
    "European Union - 27 countries (from 2020)",
    "Euro area \u2013 20 countries (from 2023)",
    "Germany",
    "France",
    "Spain",
]


def _build_columns(header_row: Sequence[object]) -> List[str]:
    """Gera os nomes de coluna propagando os rótulos de trimestre e colunas de sinalizador."""
    columns: List[str] = []
    for idx, value in enumerate(header_row):
        if idx == 0:
            columns.append("geo")
            continue
        if pd.isna(value):
            columns.append(f"{columns[-1]}_flag")
        else:
            columns.append(str(value))
    return columns


def load_sheet19_table(excel_path: Path, sheet_name: str = "Sheet 19") -> Tuple[pd.DataFrame, List[str]]:
    """Transforma a planilha 19 em um DataFrame arrumado (geo, trimestre, taxa de vagas)."""
    raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    header_row = raw.iloc[10]
    columns = _build_columns(header_row)

    data = raw.iloc[12:].reset_index(drop=True)
    data.columns = columns
    data = data[data["geo"].notna()]

    value_columns = [col for col in columns if col not in {"geo"} and not col.endswith("_flag")]
    tidy = (
        data[["geo"] + value_columns]
        .replace({":": pd.NA})
        .melt(id_vars="geo", var_name="quarter", value_name="vacancy_rate")
    )
    tidy["vacancy_rate"] = pd.to_numeric(tidy["vacancy_rate"], errors="coerce")
    tidy = tidy.dropna(subset=["vacancy_rate"])
    tidy["quarter"] = pd.Categorical(tidy["quarter"], categories=value_columns, ordered=True)
    return tidy, value_columns


def plot_job_vacancies(
    tidy_data: pd.DataFrame,
    quarters_order: Sequence[str],
    countries: Iterable[str],
    output_path: Path,
) -> None:
    """Gera um gráfico de linhas simples para os países selecionados."""
    countries = list(countries)
    subset = tidy_data[tidy_data["geo"].isin(countries)].copy()
    if subset.empty:
        raise ValueError("No rows found for the requested countries.")

    subset = subset.sort_values(["geo", "quarter"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    for geo, group in subset.groupby("geo"):
        ax.plot(group["quarter"].astype(str), group["vacancy_rate"], marker="o", label=geo)

    ax.set_title("Eurostat Job Vacancy Rate – Sheet 19")
    ax.set_ylabel("Vacancy rate (%)")
    ax.set_xlabel("Quarter")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plota a evolução das vagas de trabalho (planilha 19 da Eurostat).")
    parser.add_argument(
        "--excel-path",
        type=Path,
        default=Path("data") / "job_vacancies.xlsx",
        help="Path to the Eurostat Excel workbook.",
    )
    parser.add_argument(
        "--sheet-name",
        default="Sheet 19",
        help="Worksheet that contains the job vacancy table (default: Sheet 19).",
    )
    parser.add_argument(
        "--countries",
        nargs="+",
        default=DEFAULT_COUNTRIES,
        help="Geo labels to plot (default: a few EU benchmarks).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("plots") / "sheet19_job_vacancies.png",
        help="Where to save the generated chart.",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=Path("data") / "sheet19_job_vacancies_tidy.csv",
        help="Where to store the tidy table for Power BI (set to empty string to skip).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tidy, quarter_order = load_sheet19_table(args.excel_path, args.sheet_name)

    missing = [geo for geo in args.countries if geo not in tidy["geo"].unique()]
    if missing:
        print(
            "Warning: the following countries were not present in the sheet "
            f"and will be ignored: {', '.join(missing)}"
        )

    countries = [geo for geo in args.countries if geo in tidy["geo"].unique()]
    if not countries:
        raise SystemExit("No valid countries left to plot. Please double-check the labels in the sheet.")

    if args.csv_output:
        csv_path = Path(args.csv_output)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        tidy.to_csv(csv_path, index=False)
        print(f"Tidy dataset saved to {csv_path}")

    plot_job_vacancies(tidy, quarter_order, countries, Path(args.output))
    print(f"Chart saved to {args.output}")


if __name__ == "__main__":
    main()
