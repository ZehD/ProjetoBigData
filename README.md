# Vagas de TI vs. Crescimento da IA (Eurostat + Power BI)

Este repositório reúne dados públicos para investigar como as vagas em Tecnologia da Informação vêm diminuindo enquanto funções ligadas a Inteligência Artificial ganham espaço. A base principal é **ei_lmjv_q_r2** (Eurostat), que acompanha taxas de vagas no setor “Information and Communication” para países europeus entre 2023‑2025.

## Visão Geral

- 🎯 **Objetivo**: comparar a trajetória das vagas tradicionais de TI com a demanda por papéis de IA, produzindo gráficos que ajudem a contar essa narrativa no Power BI.
- 📊 **Fonte**: arquivo XLSX do Eurostat (planilha 19, com recortes por país/quarter). Novas fontes focadas em IA podem ser adicionadas posteriormente em `data/`.
- 🛠 **Ferramentas**: Python 3.10+, pandas, openpyxl, matplotlib para limpeza/visualização inicial; Power BI para dashboards.

## Fluxo de Trabalho

1. Coloque o arquivo baixado (`job_vacancies.xlsx`) dentro da pasta `data/`.
2. Execute o script abaixo para gerar os artefatos:
   ```bash
   python scripts/job_vacancy_sheet19.py \
       --excel-path data/job_vacancies.xlsx \
       --csv-output PowerBI/sheet19_job_vacancies_tidy.csv \
       --output plots/sheet19_job_vacancies.png
   ```
   - `PowerBI/sheet19_job_vacancies_tidy.csv`: tabela arrumada (`geo`, `quarter`, `vacancy_rate`) pronta para ingestão.
   - `plots/sheet19_job_vacancies.png`: comparação entre blocos (UE27, Eurozona, países selecionados).
3. (Opcional) Rode scripts auxiliares para análises pontuais, como `plots/first_row_progression.png`, que mostra o movimento do primeiro país listado (normalmente UE27).

## Power BI

1. Abra o Power BI Desktop → `Get Data → Text/CSV` → `PowerBI/sheet19_job_vacancies_tidy.csv`.
2. Ajuste os tipos de dados (mantenha `quarter` como texto para preservar a ordem cronológica customizada do script).
3. Utilize gráficos de linha para confrontar `vacancy_rate` por país/bloco, criando narrativas como:
   - Queda de vagas em TI vs. crescimento em países com maior adoção de IA.
   - Diferença entre blocos (UE27, Eurozona, países nórdicos) ao longo dos quarters.

Com o CSV arrumado, você pode combinar facilmente outras fontes (por exemplo, relatórios do LinkedIn, WEF, OECD sobre vagas em IA) criando relacionamentos por país/ano e destacando como o avanço da IA impacta o emprego tech.

## Requisitos Técnicos

- Python 3.10 ou superior.
- Bibliotecas: `pandas`, `openpyxl`, `matplotlib`.
  ```bash
  pip install pandas openpyxl matplotlib
  ```

Sinta-se à vontade para abrir issues ou PRs adicionando novas fontes (Eurostat, OECD, WEF, etc.), scripts comparativos ou dashboards Power BI.***
