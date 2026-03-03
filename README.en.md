# Data Senior Analytics

[Versão em Português (PT-BR)](README.md)

![Python](https://img.shields.io/badge/Python-3.14.2-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41.1-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.4.2-013243?logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.5.2-3F4F75?logo=plotly&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-1.15.2-8CAAE6?logo=scipy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Business-oriented analytics application that transforms raw tabular data into actionable insights through exploratory analysis, statistical testing, and an interactive dashboard.

Live demo: https://data-analytics-sr.streamlit.app

## Summary
- [Executive Summary](#executive-summary)
- [Data Governance (Kaggle)](#data-governance-kaggle)
- [Business Problem](#business-problem)
- [Data Strategy](#data-strategy)
- [Architecture Overview](#architecture-overview)
- [Detailed Architecture and ADRs](#detailed-architecture-and-adrs)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Reproducibility (How to Run)](#reproducibility-how-to-run)
- [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
- [Quality Gates](#quality-gates)
- [Contact](#contact)
- [License](#license)

## Executive Summary
This project delivers an end-to-end senior-level analytics workflow: data ingestion, quality diagnostics, exploratory analysis, statistical validation, and insight communication.

It was designed so recruiters and technical leaders can quickly evaluate skills in:
- Business-oriented data analysis
- Analytics engineering and software quality
- Value delivery through an interactive analytical product

## Data Governance (Kaggle)
- Official analytical dataset source: **Kaggle (real dataset)**
- Raw data is not versioned in Git (`data/raw/*` is ignored)
- `*_exemplo.csv` files are synthetic and intended only for local demo
- Mandatory provenance records:
  - [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md)
  - [config/data_source.yaml](config/data_source.yaml)

## Business Problem
Business teams often rely on spreadsheets and manual analyses, resulting in:
- Low speed for generating insights
- Inconsistent analytical quality
- Low decision traceability

The solution provides a reusable analytics layer where stakeholders upload data and quickly obtain quality diagnostics, patterns, relationships, and trends.

## Data Strategy
### Data Sources
- Primary source: real Kaggle dataset (registered in `docs/DATA_PROVENANCE.md`)
- Input formats: `.csv`, `.xlsx`

### Processing and Analytical Modeling
- Extraction with encoding handling for robust ingestion
- Automatic detection of column types (numeric, categorical, date, id)
- Missing values and outlier diagnostics
- Descriptive statistics and correlation analysis
- Hypothesis testing (t-test, ANOVA, chi-square, Pearson, Spearman)
- Optional SQLite persistence for reproducibility and reuse

## Architecture Overview
```mermaid
flowchart TD
    A[User upload CSV/XLSX] --> B[File Extractor src/data/file_extractor.py]
    B --> C[Transformer src/data/transformer.py]
    C --> D[EDA src/analysis/exploratory.py]
    C --> E[SQLite persistence src/data/sqlite_manager.py]
    D --> F[Streamlit app dashboard/app.py]
    E --> F
    F --> G[Decision support insights]
```

```mermaid
flowchart LR
    subgraph Presentation
        UI[dashboard/app.py]
    end

    subgraph Analytical_Domain
        EX[exploratory.py]
        TR[transformer.py]
        FX[file_extractor.py]
    end

    subgraph Persistence
        DB[(SQLite)]
        SM[sqlite_manager.py]
    end

    UI --> EX
    UI --> TR
    UI --> FX
    UI --> SM
    SM --> DB
```

## Detailed Architecture and ADRs
- Full technical architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Architecture Decision Records:
  - [ADR-0001-streamlit-presentation-layer.md](docs/DECISIONS/ADR-0001-streamlit-presentation-layer.md)
  - [ADR-0002-sqlite-persistence.md](docs/DECISIONS/ADR-0002-sqlite-persistence.md)
  - [ADR-0003-kaggle-provenance-gate.md](docs/DECISIONS/ADR-0003-kaggle-provenance-gate.md)

## Project Structure
```text
.
|-- dashboard/
|   `-- app.py
|-- src/
|   |-- analysis/
|   |   `-- exploratory.py
|   `-- data/
|       |-- file_extractor.py
|       |-- transformer.py
|       `-- sqlite_manager.py
|-- config/
|   |-- config.yaml
|   |-- data_source.yaml
|   `-- settings.py
|-- scripts/
|   |-- automation.py
|   |-- check_encoding.py
|   `-- generate_sample_data.py
|-- docs/
|   `-- DATA_PROVENANCE.md
|-- data/
|-- tests/
|-- requirements.txt
|-- requirements-dev.txt
|-- runtime.txt
|-- streamlit_app.py
|-- README.md
`-- README.en.md
```

## Tech Stack
- Language: Python
- Application framework: Streamlit
- Data processing: Pandas, NumPy
- Statistics: SciPy
- Visualization: Plotly
- Persistence: SQLite
- Configuration: YAML + Python settings layer

## Reproducibility (How to Run)
### Prerequisites
- Python 3.11+
- pip

### Local Run
```bash
git clone https://github.com/samuelmaia-data-analyst/data-senior-analytics.git
cd data-senior-analytics

python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements-dev.txt

# optional: generate synthetic local dataset for demo
python scripts/generate_sample_data.py

streamlit run dashboard/app.py
```

Local URL: http://localhost:8501

## Streamlit Cloud Deployment
### Recommended setup
- Main file path: `streamlit_app.py`
- Python runtime: `runtime.txt`
- Production dependencies: `requirements.txt`
- Secrets: configure in Streamlit Cloud dashboard based on `.streamlit/secrets.example.toml`

### Runbook
- [docs/STREAMLIT_CLOUD.md](docs/STREAMLIT_CLOUD.md)

## Quality Gates`r`n`r`nOperational shortcut (`make`):`r`n```bash`r`nmake quality`r`n```
```bash
python -m ruff check src config scripts dashboard tests
python -m pytest
python scripts/check_encoding.py
python scripts/streamlit_cloud_preflight.py`npython scripts/validate_data_provenance.py
```

## Contact
Samuel Maia

Senior Data Analyst

LinkedIn: https://linkedin.com/in/samuelmaia-data-analyst

GitHub: https://github.com/samuelmaia-data-analyst

Email: smaia2@gmail.com

## License
This project is licensed under the MIT License.



