from pathlib import Path
import importlib

REQUIRED_PATHS = [
    Path("dashboard/app.py"),
    Path(".streamlit/config.toml"),
    Path("requirements.txt"),
    Path("runtime.txt"),
]

REQUIRED_IMPORTS = [
    "streamlit",
    "pandas",
    "numpy",
    "plotly",
]


def check_paths() -> list[str]:
    missing = []
    for path in REQUIRED_PATHS:
        if not path.exists():
            missing.append(f"Missing file: {path}")
    return missing


def check_imports() -> list[str]:
    failures = []
    for module in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Import failed for {module}: {exc}")
    return failures


def main() -> int:
    issues = []
    issues.extend(check_paths())
    issues.extend(check_imports())

    if issues:
        print("Streamlit Cloud preflight failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Streamlit Cloud preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
