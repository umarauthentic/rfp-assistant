from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]


def ok(label: str, detail: str = "") -> None:
    print(f"[OK] {label}{': ' + detail if detail else ''}")


def warn(label: str, detail: str = "") -> None:
    print(f"[WARN] {label}{': ' + detail if detail else ''}")


def missing(label: str, detail: str = "") -> None:
    print(f"[MISSING] {label}{': ' + detail if detail else ''}")


def has_ngrok_config_token() -> bool:
    local_app_data = os.getenv("LOCALAPPDATA", "")
    config_path = Path(local_app_data) / "ngrok" / "ngrok.yml"
    if not config_path.exists():
        return False

    for line in config_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() == "authtoken" and value.strip():
            return True

    return False


def main() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        missing(".env", "copy .env.example to .env and edit local settings")
        env = {}
    else:
        ok(".env", str(env_path))
        env = dotenv_values(env_path)

    app_port = env.get("APP_PORT") or "8001"
    app_host = env.get("APP_HOST") or "0.0.0.0"
    app_password = env.get("APP_PASSWORD") or ""
    ngrok_domain = env.get("NGROK_DOMAIN") or ""

    ok("APP_HOST", app_host)
    ok("APP_PORT", app_port)
    if app_password:
        ok("APP_PASSWORD", "configured")
    else:
        warn("APP_PASSWORD", "empty; set this before sharing a remote tunnel")

    if ngrok_domain:
        ok("NGROK_DOMAIN", f"configured as {ngrok_domain}")
    else:
        ok("NGROK_DOMAIN", "empty; ngrok will create a temporary URL")

    if os.getenv("NGROK_AUTHTOKEN"):
        ok("NGROK_AUTHTOKEN", "set in current terminal")
    elif has_ngrok_config_token():
        ok("ngrok authtoken", r"found in %LOCALAPPDATA%\ngrok\ngrok.yml")
    else:
        missing(
            "ngrok authtoken",
            "run `ngrok config add-authtoken YOUR_TOKEN` or set NGROK_AUTHTOKEN",
        )

    documents_dir = ROOT / "data" / "documents"
    if documents_dir.exists():
        files = [path for path in documents_dir.rglob("*") if path.is_file()]
        if files:
            ok("data/documents", f"{len(files)} file(s) found")
        else:
            warn("data/documents", "folder exists but has no files")
    else:
        missing("data/documents", "copy source documents here and re-ingest")

    vector_dir = ROOT / "vector_store"
    if vector_dir.exists() and any(vector_dir.iterdir()):
        ok("vector_store", "index files found")
    else:
        warn("vector_store", "empty or missing; run reingest_documents.bat after copying documents")


if __name__ == "__main__":
    main()
