from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set Kaggle provenance and mark as approved.")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--dataset-url", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--snapshot-date", required=False, default=date.today().isoformat())
    parser.add_argument("--retrieval-date", required=False, default=date.today().isoformat())
    parser.add_argument("--retrieval-method", required=False, default="manual_download")
    parser.add_argument("--data-dictionary-url", required=False, default="")
    return parser.parse_args()


def update_yaml(args: argparse.Namespace) -> None:
    path = Path("config/data_source.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("project_dataset", {})

    project = data["project_dataset"]
    project.update(
        {
            "provenance_status": "approved",
            "source_type": "kaggle",
            "source_platform": "Kaggle",
            "dataset_name": args.dataset_name,
            "dataset_url": args.dataset_url,
            "owner": args.owner,
            "version_or_snapshot_date": args.snapshot_date,
            "license": args.license,
            "retrieval_method": args.retrieval_method,
            "retrieval_date": args.retrieval_date,
            "local_storage_path": "data/raw/",
            "commit_data_files": False,
            "data_dictionary_url": args.data_dictionary_url or args.dataset_url,
            "notes": "Approved Kaggle provenance metadata.",
        }
    )

    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def update_markdown(args: argparse.Namespace) -> None:
    md_path = Path("docs/DATA_PROVENANCE.md")
    content = f"""# Data Provenance - Kaggle

## Status
- Fonte oficial do projeto: **Kaggle**
- Dados brutos versionados no Git: **não**
- Registro obrigatório antes de release: **sim**
- Status atual da proveniência: **approved**

## Registro da Fonte
- Dataset (nome exato no Kaggle): `{args.dataset_name}`
- URL oficial: `{args.dataset_url}`
- Owner/Publicador: `{args.owner}`
- Licença: `{args.license}`
- Data do snapshot utilizado: `{args.snapshot_date}`
- Data de download: `{args.retrieval_date}`
- Método de obtenção: `{args.retrieval_method}`
- Dicionário de dados: `{args.data_dictionary_url or args.dataset_url}`

## Regras de Governança
- Sempre registrar a URL oficial do Kaggle e a data de snapshot usada.
- Não commitar arquivos brutos em `data/raw/`.
- Dados de exemplo sintéticos (`*_exemplo.csv`) são apenas para demonstração local.
- Qualquer relatório executivo deve citar o dataset e sua licença.

## Evidência de Reprodutibilidade
- Configuração de fonte: [config/data_source.yaml](../config/data_source.yaml)
- Script de validação de proveniência: [scripts/validate_data_provenance.py](../scripts/validate_data_provenance.py)
- Script de geração sintética (opcional): [scripts/generate_sample_data.py](../scripts/generate_sample_data.py)
"""
    md_path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    update_yaml(args)
    update_markdown(args)
    print("Kaggle provenance updated and marked as approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
