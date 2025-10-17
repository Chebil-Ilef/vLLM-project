

1. Copy and edit the backend env file

```bash
cp chatbot-system/.env.example chatbot-system/.env
# Edit chatbot-system/.env and set VLLM_URL, VLLM_API_KEY, VLLM_MODEL and any other secrets
```

2. Build and start with Docker Compose

```bash
docker compose build
docker compose up
```

This will:
- Start Neo4j accessible on http://localhost:7474 and bolt at bolt://localhost:7687 (credentials from `.env` or defaults in `.env.example`).
- Start the backend on http://localhost:5000
- Start the frontend on http://localhost:8080

Notes and troubleshooting
- If you want to use local code changes for rapid backend development, the compose file mounts `./chatbot-system` into the container. For production, remove the `volumes` mount to use the image contents only.
- Make sure `VLLM_URL`/`VLLM_API_KEY`/`VLLM_MODEL` are set in `chatbot-system/.env` before starting the backend.
- If the backend fails to start due to missing Python packages, run `docker compose build --no-cache` to rebuild.
