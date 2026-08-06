# Transfer RFP Assistant To A New PC

This guide explains which files come from GitHub and which local configuration must be copied or recreated manually.

## Why ngrok May Fail On The New PC

The repository does not include private local configuration. This is intentional.

The following are ignored by Git:

- `.env`
- `vector_store/`
- `data/documents/`
- `data/rfp_templates/`
- `data/generated_rfps/`
- `*.log`

ngrok authentication is also not stored in the repository. On Windows, the ngrok token is usually stored here:

```text
%LOCALAPPDATA%\ngrok\ngrok.yml
```

If the new PC does not have an ngrok auth token, `run_ngrok.bat` will fail with an authentication/authtoken error.

## Transfer Checklist

### 1. Get The Latest Code

On the new PC:

```bat
git clone https://github.com/umarauthentic/rfp-assistant.git
cd rfp-assistant
```

If the repo is already cloned:

```bat
git pull origin main
```

### 2. Install The App

Run:

```bat
install_windows.bat
```

This creates the virtual environment and installs Python dependencies.

### 3. Create The `.env` File

Copy `.env.example` to `.env`:

```bat
copy .env.example .env
```

Then edit `.env`.

Recommended minimum values:

```env
APP_HOST=0.0.0.0
APP_PORT=8001
APP_USERNAME=rfp
APP_PASSWORD=replace-with-a-long-random-password
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_PROVIDER=ollama
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DATA_DIR=data
VECTOR_DIR=vector_store
NGROK_DOMAIN=
```

Important:

- Do not commit `.env`.
- Use the same `APP_USERNAME` and `APP_PASSWORD` only if you want the same login on the new PC.
- Leave `NGROK_DOMAIN` empty for a temporary ngrok URL.
- Set `NGROK_DOMAIN` only if that domain is reserved in the same ngrok account.

### 4. Configure ngrok Authentication

Get the ngrok authtoken from the ngrok dashboard, then run this on the new PC:

```bat
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

If the ngrok CLI is not installed, set the token in the terminal before starting the tunnel:

```bat
set NGROK_AUTHTOKEN=YOUR_NGROK_AUTHTOKEN
run_ngrok.bat
```

Do not put `NGROK_AUTHTOKEN` in `.env` if the repo might be shared.

### 5. Transfer Documents

Copy your knowledge documents from the old PC to:

```text
data\documents
```

Supported source file types:

- `.docx`
- `.pdf`
- `.pptx`
- `.xlsx`
- `.txt`
- `.md`

### 6. Rebuild The Document Index

After copying documents, run:

```bat
reingest_documents.bat
```

Or start the app and click:

```text
Re-ingest Knowledge Docs
```

The `vector_store` folder does not need to be copied if you re-ingest on the new PC.

### 7. Start The App

Run:

```bat
run_app.bat
```

Then open:

```text
http://localhost:8001
```

Check health:

```text
http://localhost:8001/health
```

### 8. Start The Remote Tunnel

In a second terminal, run:

```bat
run_ngrok.bat
```

If successful, it prints a URL like:

```text
https://example-id.ngrok-free.app
```

Use that URL to access the app remotely.

## Common ngrok Problems

### Authtoken Not Found

Run:

```bat
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

Or temporarily set:

```bat
set NGROK_AUTHTOKEN=YOUR_NGROK_AUTHTOKEN
```

### Reserved Domain Error

If `.env` has `NGROK_DOMAIN=some-domain`, that domain must be reserved in your ngrok account.

To test with a temporary URL, set:

```env
NGROK_DOMAIN=
```

Then restart `run_ngrok.bat`.

### App Not Reachable Through ngrok

Make sure the app is already running locally:

```text
http://localhost:8001/health
```

Then start ngrok again:

```bat
run_ngrok.bat
```

### Login Does Not Work

Check the new PC's `.env`:

```env
APP_USERNAME=rfp
APP_PASSWORD=your-password
```

Restart `run_app.bat` after changing `.env`.
