# Data Analytics Workflow

[Versao em Portugues](README.md)

[![CI](https://img.shields.io/github/actions/workflow/status/samuelmaia-analytics/data-senior-analytics/ci.yml?branch=main&label=CI)](https://github.com/samuelmaia-analytics/data-senior-analytics/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?logo=streamlit&logoColor=white)](https://data-analytics-sr.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-0f172a.svg)](LICENSE)

Portfolio analytics project that turns tabular files into a practical analytical workflow: ingestion, data cleaning, quality scoring, dashboard analysis, and SQLite persistence.

Live demo: https://data-analytics-sr.streamlit.app

Note: the public repository name may be updated in the future to better reflect the current project positioning.

## Project summary
This project was built to present a business-oriented analytics workflow with documentation, data quality checks, and practical governance foundations.

## Business problem
Business teams often receive spreadsheets with inconsistent structure and need fast answers:
- is this data reliable enough for analysis?
- where are the main revenue and concentration signals?
- what action should come first before sharing findings?

## Proposed solution
The repository applies a layered workflow:
- CSV/XLSX or demo dataset intake
- automated curation and standardization
- quality score and practical action suggestions
- Streamlit analytical view (KPI, EDA, trends, concentration)
- optional SQLite persistence with retention and privacy metadata

## Skills demonstrated
- business-oriented analytics
- data quality and data documentation practices
- practical analytical workflow with reproducible steps
- dashboard communication for decision support
- testing, linting, and CI foundations
- work style aligned with Junior Data Analyst, Data Analyst, BI Analyst, and early/intermediate Analytics Engineer paths

## Technical stack
- `Python`, `Pandas`, `NumPy`
- `Streamlit`, `Plotly`
- `SQLite`
- `Pytest`, `Ruff`, `Black`, `GitHub Actions`

## Dashboard features
- `Overview`: KPI, decision risk, confidence, and next actions
- `Upload`: data upload plus automated curation
- `Data`: raw vs curated comparison
- `EDA`: statistics, correlation, and missing profile
- `Visualizations`: distribution, business mix, and trend analysis
- `Database`: persisted dataset catalog and inspection
- `Settings`: runtime and governance metadata

## Run locally
```bash
git clone https://github.com/samuelmaia-analytics/data-senior-analytics.git
cd data-senior-analytics
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
python -m streamlit run dashboard/app.py
```

## Tests
```bash
python -m pytest
```

## Demo link
- https://data-analytics-sr.streamlit.app

## For recruiters and tech leads
This repository is positioned for opportunities such as:
- Junior Data Analyst / Data Analyst
- Junior BI Analyst / BI Analyst
- early/intermediate Analytics Engineer
- freelance data projects and remote data opportunities

## What this project demonstrates
- clear translation from business question to analytical workflow
- data quality controls and traceable documentation
- practical dashboard delivery with stakeholder-ready communication
- governance simulation and privacy-aware handling as portfolio good practices

## Future improvements
- add connectors for APIs and external databases
- expand contract tests for additional scenarios
- publish use-case variants (sales, retention, operations)
- extend quality and observability automation

## License
Licensed under MIT. See [LICENSE](LICENSE).
