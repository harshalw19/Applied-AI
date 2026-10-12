# ScalerGPT 📚

A **RAG chatbot** over your own notes — FastAPI + OpenAI + ChromaDB, running as a
two-container application orchestrated with Docker Compose.

Part of the *Dockerize Everything: ML → LLM → Agents* masterclass.
This is **Project 2 of 3** (after QuickBite ETA, before DeskBuddy).

> **What it does:** you drop `.md` / `.txt` notes into `docs/`, run one ingest command,
> and then ask questions in plain English. The app finds the most relevant passages and
> has GPT answer using only those passages.

---

## ⚠️ Read this first — three rules that prevent 90% of problems

**1. After editing ANY file, you must rebuild.**
```bash
docker compose up -d --build
```
Without `--build`, Compose reuses the cached image and your edits never reach the
container. You will edit a file, restart, see no change, and lose ten minutes.

> **Mental model:** the image is a *photograph*, not a *mirror*. Editing the source file
> does not update the photograph — you have to take a new one.

**2. Do not paste commands with trailing `#` comments into zsh.**
macOS zsh does not treat `#` as a comment in interactive mode. If you paste
`docker compose ps -a   # some note` and the note contains an apostrophe, your terminal
hangs showing `quote>`. Press **Ctrl+C** and re-run the command without the comment.

**3. `docker compose ps` hides dead containers.**
If a service is missing from the list, it exited. Use `docker compose ps -a` to see it,
then `docker compose logs <service>` for the reason.

---

## 🆕 What's new versus the ML project

QuickBite ETA was a single container. This one adds four new ideas:

| New concept | Why it appears here |
|---|---|
| **Secrets via `.env`** | We now call a paid API. The key must never be baked into the image. |
| **Docker Compose** | Two containers (app + vector DB) that start together and talk to each other. |
| **Service-name networking** | The app reaches the database at `http://chroma:8000` — no IP addresses. |
| **Volumes** | The vector DB has *state*. It must survive `docker compose down`. |

---

## 📁 What's in this folder

| File | Purpose |
|---|---|
| `app.py` | FastAPI service — `/ask` runs retrieve → augment → generate |
| `ingest.py` | Reads `docs/*.md` and `docs/*.txt`, chunks them, embeds them into Chroma |
| `docs/` | Sample knowledge base (3 markdown notes). Replace with your own! |
| `requirements.txt` | Pinned Python dependencies |
| `Dockerfile` | Recipe for the **app** container (Chroma uses a prebuilt image) |
| `docker-compose.yml` | Defines both services, the network, and the volume |
| `.env.example` | Template for your API key — copy to `.env` |
| `.dockerignore` | Keeps `.env`, `venv/`, `.git/` out of the image |
| `.gitignore` | Keeps `.env` out of version control |

---

## ✅ Prerequisites

1. **Docker Desktop** running (whale 🐳 icon steady in the menu bar).
2. **An OpenAI API key** with credit — <https://platform.openai.com/api-keys>.

This project makes real paid API calls, but they are tiny: embedding the three sample
docs plus a handful of questions costs well under one US cent using
`text-embedding-3-small` and `gpt-4o-mini`.

You do **not** need Python installed locally.

---

## 🚀 Step-by-step

### Step 1 — Extract and open in VS Code
Unzip and move the folder to e.g. `~/Projects/scalergpt`, then:
```bash
code ~/Projects/scalergpt
```
Or VS Code → **File → Open Folder**.

### Step 2 — Create your `.env` file ⚠️ don't skip
In the VS Code terminal (`` Ctrl + ` ``):
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your real key:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```
No quotes, no spaces around the `=`. `.env` is already gitignored and dockerignored.

Verify it exists:
```bash
ls -la .env
```

### Step 3 — Confirm Docker Desktop is running
Whale 🐳 icon steady in the menu bar.

### Step 4 — Start both containers
```bash
docker compose up -d --build
```
First run takes 2–4 minutes (builds your app image, pulls Chroma from Docker Hub).

### Step 5 — Verify both are up
```bash
docker compose ps -a
```
Both `scalergpt-app` and `scalergpt-chroma` should show **Up**. If `app` shows
**Exited**, jump to Troubleshooting below.

Check the startup log:
```bash
docker compose logs app
```
Look for `[ScalerGPT] Connected to chroma at chroma:8000`.

### Step 6 — Health check
```bash
curl http://localhost:8000/
```
```json
{"status": "ScalerGPT is live", "docs_indexed": 0, "chroma_host": "chroma", "chroma_port": 8000}
```
`docs_indexed: 0` is expected — nothing loaded yet.

### Step 7 — Ingest the documents
```bash
docker compose exec app python ingest.py
```
```
Ingested 15 chunks from 3 file(s) ✅
Collection now holds 15 chunks total.
```
Note what just happened: you ran a script **inside a live container**. This is exactly
how you'd run database migrations or one-off jobs in production.

Re-check `curl http://localhost:8000/` — `docs_indexed` is now greater than zero.

### Step 8 — Ask a question 🎉
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": "Why should I copy requirements.txt before the rest of my code?"}'
```

Or use the **Swagger UI** at **<http://localhost:8000/docs>** — expand `POST /ask`,
click *Try it out*, type a question, hit *Execute*. Better for live demos.

Questions worth trying:
- *What is the difference between an image and a container?*
- *What happens to my data when I run docker compose down?*
- *Why does chunk size matter in RAG?*
- *What is the capital of France?* ← should say it doesn't know

That last one is the important one. It proves answers are **grounded in your documents**
rather than the model's general memory.

### Step 9 — The volume persistence demo 💡
The strongest moment in this project. Destroy everything, bring it back, watch the data
survive:
```bash
docker compose down
docker compose up -d
curl http://localhost:8000/
```
`docs_indexed` is still greater than zero. You never re-ran `ingest.py`, yet the
embeddings are intact — they live in the `chroma_data` volume, not inside the container.

To actually delete them you must remove the volume:
```bash
docker compose down -v
```

### Step 10 — Watch the logs
```bash
docker compose logs -f          # both services, interleaved
docker compose logs -f app      # just the app
```
`Ctrl+C` to stop following.

### Step 11 — Use your own notes
```bash
rm docs/*.md
cp ~/path/to/your/notes.md docs/
docker compose up -d --build
docker compose exec app python ingest.py
```

### Step 12 — Clean up
```bash
docker compose down       # stop, keep the data
docker compose down -v    # stop and wipe the vector DB
```

---

## 🔑 Two things most people get wrong

### 1. Published port vs internal port

```yaml
  app:
    environment:
      - CHROMA_HOST=chroma
      - CHROMA_PORT=8000     # <-- INTERNAL port

  chroma:
    ports:
      - "8001:8000"          # <-- PUBLISHED port, for your Mac only
```

Chroma listens on port **8000 inside its own container**. The `8001:8000` mapping exists
purely so *you* can reach it from your Mac at `localhost:8001` for debugging.

The app is already **inside** the Docker network, so it uses the internal port `8000`.
Setting `CHROMA_PORT=8001` gives you connection-refused.

> **Analogy:** `8001` is the building's street gate, used by visitors from outside.
> `8000` is the flat number, used by people who already live in the building.

### 2. `depends_on` waits for START, not for READY

`depends_on: [chroma]` only guarantees Chroma's container has been *started* — not that
it is accepting connections. Chroma needs several seconds to boot. If the app connects
immediately it gets `Connection refused` and uvicorn exits.

This is why `app.py` wraps the connection in `connect_to_chroma()`, which retries for up
to 60 seconds and prints its progress. The alternative fix is a `healthcheck` on chroma
plus `depends_on: condition: service_healthy`.

This is one of the most common Compose gotchas in the wild.

---

## 🪤 Troubleshooting

| Problem | Fix |
|---|---|
| Edited a file, nothing changed | You must rebuild: `docker compose up -d --build` |
| `docker compose ps` shows only chroma | The app exited. `docker compose ps -a` to see it, `docker compose logs app` for why. |
| Terminal stuck at `quote>` | You pasted a command containing `#` and an apostrophe into zsh. Press Ctrl+C. |
| `OPENAI_API_KEY is missing` | Step 2. Create `.env` from `.env.example` with a real key, then `docker compose up -d --force-recreate`. |
| `AuthenticationError` / `401` | Key is wrong or has stray quotes/spaces in `.env`. |
| `RateLimitError` / `insufficient_quota` | No credit on your OpenAI account. Add billing. |
| `Could not connect to a Chroma server` at `app.py` line ~29 | You are running the OLD `app.py` without the retry loop. Confirm with `grep -c connect_to_chroma app.py` — if it prints `0`, replace the file and rebuild with `--build`. |
| `Connection refused` to chroma | Check `CHROMA_PORT` is `8000`, not `8001`. |
| `No documents indexed yet` from `/ask` | Run Step 7. |
| `port is already allocated` | `lsof -i :8000` to find the culprit, or change the mapping to `"8080:8000"`. |
| Edited `.env`, no effect | Env vars load at container start: `docker compose up -d --force-recreate` |
| Chroma keeps restarting | `docker compose logs chroma`. Usually a stale volume — `docker compose down -v`. |

---

## 🔑 Key concepts demonstrated

- **Secrets management** — `.env` + `env_file`, never `ENV KEY=...` in a Dockerfile
  (anyone can read that back with `docker history`)
- **Multi-container orchestration** — one `docker compose up` instead of many `docker run`
- **Service discovery** — containers reach each other by service name, never by IP
- **Published vs internal ports**
- **Startup ordering vs startup readiness** — why `depends_on` isn't enough
- **Volumes** — separating disposable compute from persistent state
- **`docker compose exec`** — running one-off commands inside a live container
- **Thin-client architecture** — `chromadb-client` keeps the app image small because the
  heavy database runs in its own container
- **Image immutability** — code is baked in at build time; `--build` is mandatory after edits

---

## 🏠 Homework

1. **Easy** — Add a `/sources` endpoint returning which files are currently indexed.
2. **Medium** — Replace the retry loop with a proper `healthcheck` on chroma plus
   `depends_on: condition: service_healthy`. Compare the two approaches.
3. **Hard** — Swap OpenAI embeddings for a local model so retrieval makes zero paid API
   calls. Compare the resulting image size.
4. **Boss level** — Add a third service: a small Streamlit or static HTML front end that
   calls `/ask`, wired into the same compose file.

---

Made with 🐳 for **Future with Shivank**
