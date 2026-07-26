# RFP Assistant

A local-first RFP response builder for generating vendor answers from historical RFP documents and exporting responses into a Word template.

## What It Does

- Upload or load an RFP question template in `.docx` format.
- Add RFP questions one by one or paste a question list.
- Generate answers from local indexed documents.
- Show source document references for generated answers.
- Export answers into the Word RFP template.
- Store and search historical approved answers.
- Runs locally on Windows with FastAPI, FAISS, Sentence Transformers, and Ollama.

## Windows Deployment

Use this process on a new Windows PC.

### 1. Copy The Project

Copy this repository to the target PC, for example:

```text
C:\rfp-assistant
```

You can use Git:

```bat
git clone https://github.com/umarauthentic/rfp-assistant.git
cd rfp-assistant
```

Or download the repository as a ZIP from GitHub and unzip it.

### 2. Run The Installer

Double-click:

```text
install_windows.bat
```

The installer will:

- Install Python 3.14 using `winget` if Python is missing.
- Install Ollama using `winget` if Ollama is missing.
- Create a local Python virtual environment.
- Install Python dependencies from `requirements.txt`.
- Create `.env` from `.env.example` if needed.
- Pull the configured Ollama model.
- Build the local document index.

Default local model:

```text
llama3.2
```

### 3. Start The Web App

Double-click:

```text
run_app.bat
```

Then open:

```text
http://localhost:8001
```

The script also opens the browser automatically.

### 4. Re-index Documents

If you add, remove, or change files under:

```text
data\documents
```

Run:

```text
reingest_documents.bat
```

## Configuration

The app reads settings from `.env`.

Default local configuration:

```env
APP_HOST=0.0.0.0
APP_PORT=8001
APP_PASSWORD=
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
TOP_K_DOCS=8
MIN_DOC_SCORE=0.15
```

`APP_PASSWORD` is optional. Leave it empty for local-only use. Set it before sharing the app through a tunnel so the browser prompts for a password:

```env
APP_PASSWORD=replace-with-a-long-random-password
```

To use a stronger local model, install it with Ollama:

```bat
ollama pull llama3.1:8b
```

Then update `.env`:

```env
OLLAMA_MODEL=llama3.1:8b
```

Restart `run_app.bat` after changing `.env`.

## Running Locally

Start the application:

```bat
run_app.bat
```

The script starts Ollama, then starts FastAPI with:

```bat
uvicorn app.main:app --host %APP_HOST% --port %APP_PORT%
```

By default, the app listens on:

```text
http://localhost:8001
```

The FastAPI health check is available at:

```text
http://localhost:8001/health
```

## Remote Access With Cloudflare Tunnel

Do not expose Ollama directly. Keep `OLLAMA_BASE_URL=http://localhost:11434` and expose only the application port, which defaults to `8001`.

For a temporary development tunnel, install `cloudflared`, start the app, then run:

```bat
cloudflared tunnel --url http://localhost:8001
```

Cloudflare will print a temporary HTTPS URL like:

```text
https://<random-name>.trycloudflare.com
```

Use that URL to reach the RFP Assistant remotely while the tunnel is running.

Important limitations:

- The computer must remain powered on.
- Ollama must remain running.
- The RFP Assistant application must remain running.
- Temporary tunnel URLs can change after restarting `cloudflared`.
- Use a named Cloudflare Tunnel for a stable domain.
- Enable authentication before sharing the application publicly. At minimum, set `APP_PASSWORD` in `.env`; for broader access, put Cloudflare Access in front of the named tunnel.
- Never commit `.env`, tunnel credentials, API keys, passwords, or Cloudflare credential files.

## Project Scripts

- `install_windows.bat` - first-time Windows setup.
- `run_app.bat` - starts Ollama and the FastAPI web app.
- `reingest_documents.bat` - rebuilds the document vector index.
- `setup_windows.bat` - older basic setup script.
- `run_local.bat` - older local development run script.

## Main API Endpoints

- `GET /health`
- `POST /upload`
- `POST /ingest/documents`
- `POST /query`
- `POST /rfp/template/upload`
- `GET /rfp/template/questions`
- `POST /rfp/answer-one`
- `POST /rfp/generate`
- `POST /memory/save`
- `GET /memory/list`

## Notes

- Ollama must be running for answer generation.
- Local models avoid hosted API rate limits, but answer speed depends on the target PC.
- `llama3.2` is the default local model because it is still lightweight while usually producing better RFP answers than `phi3:mini`.
- Generated RFP files are saved under `data\generated_rfps`.
- Uploaded RFP templates are saved under `data\rfp_templates`.
