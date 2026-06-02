# Data Analytics Workflow

[English version](README.en.md)

[![CI](https://img.shields.io/github/actions/workflow/status/samuelmaia-analytics/data-senior-analytics/ci.yml?branch=main&label=CI)](https://github.com/samuelmaia-analytics/data-senior-analytics/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?logo=streamlit&logoColor=white)](https://data-analytics-sr.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-0f172a.svg)](LICENSE)

Projeto de portfólio para transformar arquivos tabulares em um fluxo analítico prático: ingestão, limpeza, score de qualidade, visualização e persistência em SQLite.

Demo online: https://data-analytics-sr.streamlit.app

Nota: o nome público do repositório pode ser alterado futuramente para refletir melhor o posicionamento atual do projeto.

## Resumo do projeto
Este app foi construído para mostrar uma rotina analítica completa com foco em valor de negócio, documentação e controles básicos de qualidade e governança.

## Problema de negócio
Equipes de negócio recebem planilhas com estruturas diferentes e precisam responder rápido:
- o dado está confiável para análise?
- onde estão os principais sinais de receita e concentração?
- qual ação priorizar antes de compartilhar resultados?

## Solução proposta
O projeto aplica um fluxo analítico em camadas:
- carga de CSV/XLSX ou dataset demo
- limpeza e padronização automática
- score de qualidade com recomendações práticas
- visão analítica no Streamlit (KPI, EDA, tendências, concentração)
- persistência opcional em SQLite com metadados de retenção e privacidade

## Competências demonstradas
- análise de dados orientada ao negócio
- SQL + Python para transformação e validação
- qualidade de dados (`Quality Score`, completude, duplicidade)
- documentação técnica e rastreabilidade de dados
- testes automatizados, lint e CI
- fluxo analítico prático para contexto de BI e analytics engineering inicial/intermediário

## Stack técnica
- `Python`, `Pandas`, `NumPy`
- `Streamlit`, `Plotly`
- `SQLite`
- `Pytest`, `Ruff`, `Black`, `GitHub Actions`

## Funcionalidades do dashboard
- `Overview`: KPI, risco de decisão, confiança e recomendações
- `Upload`: carga e curadoria automática
- `Data`: comparação entre base bruta e curada
- `EDA`: estatísticas, correlação e perfil de ausências
- `Visualizations`: distribuição, mix e tendência temporal
- `Database`: catálogo e inspeção de dados persistidos
- `Settings`: metadados de execução e governança aplicada

## Como rodar localmente
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

## Como testar
```bash
python -m pytest
```

## Link da demo
- https://data-analytics-sr.streamlit.app

## Para recrutadores e leads
Este projeto é útil para avaliação de perfil em oportunidades como:
- Analista de Dados Júnior / Analista de Dados
- Analista de BI Júnior / Analista de BI
- Analytics Engineer inicial/intermediário
- projetos freelance de dados e trabalhos remotos

## O que este projeto demonstra
- capacidade de organizar um problema de negócio em fluxo analítico reproduzível
- cuidado com qualidade de dados e documentação de apoio
- comunicação de resultados em dashboard focado em decisão
- aplicação de boas práticas de governança e privacidade em projeto de portfólio

## Melhorias futuras
- adicionar novos conectores de dados (APIs e banco externo)
- incluir mais testes de contrato para cenários de regressão
- publicar versões de dashboard por caso de uso (vendas, retenção, operações)
- ampliar automações de qualidade e observabilidade

## Licença
Licenciado sob MIT. Veja [LICENSE](LICENSE).
