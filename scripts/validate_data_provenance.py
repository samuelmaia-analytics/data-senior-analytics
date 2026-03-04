from pathlib import Path

import yaml

REQUIRED_KEYS = [
    "provenance_status",
    "source_type",
    "source_platform",
    "dataset_name",
    "dataset_url",
    "owner",
    "version_or_snapshot_date",
    "license",
    "retrieval_method",
    "retrieval_date",
    "local_storage_path",
    "commit_data_files",
    "data_dictionary_url",
]

PENDING_TOKEN = "PENDING_CONFIRMATION"


def main() -> int:
    config_path = Path("config/data_source.yaml")
    if not config_path.exists():
        print("Data provenance check failed: config/data_source.yaml not found.")
        return 1

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    dataset = data.get("project_dataset") or {}

    missing = [key for key in REQUIRED_KEYS if key not in dataset]
    if missing:
        print("Data provenance check failed: missing keys:")
        for key in missing:
            print(f"- {key}")
        return 1

    status = str(dataset.get("provenance_status", "")).strip()
    if status not in {"pending_confirmation", "approved"}:
        print(
            "Data provenance check failed: provenance_status must be 'pending_confirmation' or 'approved'."
        )
        return 1

    if status == "pending_confirmation":
        print("Data provenance check passed with warning: status is pending_confirmation.")
        return 0

    # status == approved
    blocked_fields = [
        "dataset_name",
        "dataset_url",
        "owner",
        "license",
        "data_dictionary_url",
    ]

    unresolved = []
    for field in blocked_fields:
        value = str(dataset.get(field, "")).strip()
        if not value or PENDING_TOKEN in value or "/PENDING/" in value:
            unresolved.append(field)

    if unresolved:
        print("Data provenance check failed: approved status requires real values for:")
        for field in unresolved:
            print(f"- {field}")
        return 1

    print("Data provenance check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
