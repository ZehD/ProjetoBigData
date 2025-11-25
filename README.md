# Vagas de TI vs. Crescimento da IA (Eurostat + Power BI)

Repositorio com dados publicos para comparar a evolucao das vagas tradicionais de TI com funcoes ligadas a IA. A base principal e a **ei_lmjv_q_r2** (Eurostat), com taxas de vagas no setor Information and Communication para paises europeus entre 2023 e 2025.

## Visao geral

- **Objetivo**: gerar tabelas arrumadas e graficos para contar a historia de queda de vagas de TI versus aumento de papeis de IA.
- **Fonte**: arquivo XLSX do Eurostat (qualquer aba que siga o layout padrao: primeira coluna `geo`, demais colunas por trimestre + flags).
- **Ferramentas**: Python 3.10+, pandas, openpyxl, matplotlib; Power BI para dashboard final.

## Fluxo de trabalho

1. Coloque o arquivo baixado `job_vacancies.xlsx` em `data/`.
2. Rode o script generico apontando a aba desejada (padrao: `Sheet 19`). Opcao rapida interativa:
   ```bash
   python scripts/gerar_grafico_vagas.py --interativo
   ```
   Ou modo parametrizado:
   ```bash
   python scripts/gerar_grafico_vagas.py \
       --caminho-excel data/job_vacancies.xlsx \
       --aba "Sheet 19" \
       --paises "European Union - 27 countries (from 2020)" "Germany"
   ```
   - CSV arrumado: `PowerBI/tabela_vagas_<aba>.csv` (troque com `--saida-csv` ou pule com `--sem-csv`).
   - Grafico de linhas: `plots/grafico_vagas_<aba>.png` (troque com `--saida-grafico` ou pule com `--sem-grafico`).
3. Para trocar de aba basta mudar `--aba` (ex.: `--aba "Sheet 20"`). Se a linha do cabecalho ou dos dados mudar, ajuste `--linha-cabecalho` e `--linha-dados` (indices zero-based).

## Power BI

1. Importe `PowerBI/tabela_vagas_<aba>.csv` via `Get Data -> Text/CSV`.
2. Mantenha `trimestre` como texto para preservar a ordem definida pelo script.
3. Use graficos de linha comparando `taxa_vaga` por `geo` para contar a narrativa desejada (queda em TI vs. crescimento em IA, blocos UE27 vs. Eurozona, etc.).

## Requisitos tecnicos

- Python 3.10 ou superior.
- Bibliotecas: `pandas`, `openpyxl`, `matplotlib`.
  ```bash
  pip install pandas openpyxl matplotlib
  ```
