# Projeto Big Data – Vagas na Tecnologia (Eurostat)

Ferramentas simples para explorar como a taxa de vagas em TI evoluiu na Europa usando o conjunto **ei_lmjv_q_r2** da Eurostat (planilha 19 do arquivo XLSX). O fluxo atual:

1. Coloque o arquivo baixado (`job_vacancies.xlsx`) dentro de `data/`.
2. Execute `python scripts/job_vacancy_sheet19.py` para gerar:
   - `data/sheet19_job_vacancies_tidy.csv`: tabela arrumada (`geo`, `quarter`, `vacancy_rate`) pronta para Power BI.
   - `plots/sheet19_job_vacancies.png`: gráfico comparando alguns países/agrupamentos.
3. Opcional: use `plots/first_row_progression.png` para visualizar rapidamente a evolução do primeiro elemento da tabela.

## Requisitos

- Python 3.10+
- Bibliotecas: `pandas`, `openpyxl`, `matplotlib` (já instaladas via `pip install -r requirements.txt` quando esse arquivo estiver disponível; por enquanto, instale manualmente).

## Power BI

1. Abra o Power BI Desktop → `Get Data → Text/CSV` e selecione `data/sheet19_job_vacancies_tidy.csv`.
2. Confirme os tipos (especialmente `quarter` como Texto) e carregue.
3. Use gráficos de linha/área para comparar `vacancy_rate` por `geo` ao longo de `quarter`.

Sinta-se à vontade para ajustar o script ou adicionar novas fontes/datasets dentro das pastas `scripts/` e `data/`.
