import os
import time
from pathlib import Path

from dotenv import load_dotenv
import ngrok


def _get_ngrok_authtoken() -> str | None:
    token = os.getenv("NGROK_AUTHTOKEN")
    if token:
        return token

    config_path = Path(os.getenv("LOCALAPPDATA", "")) / "ngrok" / "ngrok.yml"
    if not config_path.exists():
        return None

    for line in config_path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() == "authtoken":
            return value.strip().strip('"').strip("'") or None

    return None


def main() -> None:
    load_dotenv()

    app_port = int(os.getenv("APP_PORT", "8001"))
    domain = os.getenv("NGROK_DOMAIN") or None
    authtoken = _get_ngrok_authtoken()

    if not authtoken:
        raise RuntimeError(
            "ngrok authtoken not found. Run `ngrok config add-authtoken YOUR_TOKEN` "
            "or set NGROK_AUTHTOKEN in your shell."
        )

    forward_args = {
        "addr": f"localhost:{app_port}",
        "authtoken": authtoken,
    }
    if domain:
        forward_args["domain"] = domain

    listener = ngrok.forward(**forward_args)
    print(f"ngrok tunnel established: {listener.url()}", flush=True)
    print("Press Ctrl+C to stop the tunnel.", flush=True)

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Stopping ngrok tunnel.", flush=True)


if __name__ == "__main__":
    main()
