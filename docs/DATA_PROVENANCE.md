# Data Provenance - Kaggle

## Status
- Fonte oficial do projeto: **Kaggle**
- Dados brutos versionados no Git: **não**
- Registro obrigatório antes de release: **sim**
- Status atual da proveniência: **approved**

## Registro da Fonte
- Dataset (nome): `Credit Risk Benchmark Dataset`
- URL de referência: `https://www.kaggle.com/datasets?datasetId=7083324`
- Kaggle Dataset ID: `7083324`
- Kaggle Source ID (datasetVersion): `11324518`
- Owner/Publicador: `not_available_in_notebook_metadata`
- Licença: `not_available_in_notebook_metadata`
- Data do snapshot identificado no notebook: `2025-05-01`
- Data de registro no projeto: `2026-03-03`
- Método de obtenção: `kaggle_notebook_datasource`
- Notebook de evidência: `data/raw/classifica-o-de-inadimpl-ncia.ipynb`

## Observação de Rastreabilidade
- Este registro foi extraído dos metadados internos do notebook Kaggle (`metadata.kaggle.dataSources`).
- Quando disponível, substituir `owner` e `license` pelos valores oficiais da página pública do dataset.

## Regras de Governança
- Sempre registrar a URL oficial do Kaggle e a data de snapshot usada.
- Não commitar arquivos brutos em `data/raw/`.
- Dados de exemplo sintéticos (`*_exemplo.csv`) são apenas para demonstração local.
- Qualquer relatório executivo deve citar o dataset e sua licença.

## Evidência de Reprodutibilidade
- Configuração de fonte: [config/data_source.yaml](../config/data_source.yaml)
- Script de validação de proveniência: [scripts/validate_data_provenance.py](../scripts/validate_data_provenance.py)
- Script de geração sintética (opcional): [scripts/generate_sample_data.py](../scripts/generate_sample_data.py)
