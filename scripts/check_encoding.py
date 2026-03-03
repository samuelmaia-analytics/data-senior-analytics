from pathlib import Path

TEXT_SUFFIXES = {".py", ".md", ".toml", ".yaml", ".yml", ".txt"}
SKIP_DIRS = {".git", "venv", ".venv", "__pycache__"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    invalid_files: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if should_skip(path):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            invalid_files.append(f"{path} -> invalid UTF-8")
            continue

        if "\ufffd" in content:
            invalid_files.append(f"{path} -> contains replacement character (U+FFFD)")

    if invalid_files:
        print("Encoding check failed:")
        for item in invalid_files:
            safe_item = item.encode("ascii", "backslashreplace").decode("ascii")
            print(f"- {safe_item}")
        return 1

    print("Encoding check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
