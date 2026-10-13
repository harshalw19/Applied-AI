# DeskBuddy 🤖

An **agentic AI system** — an LLM that doesn't just answer, it *does things*.
Three containers working together, orchestrated with Docker Compose:

```
 you ──▶ agent (port 9000) ──▶ tools (private, port 7000)
              │
              └──▶ redis (private, conversation memory)
```

| Container | Role | Office analogy |
|---|---|---|
| **agent** | LLM + tool-calling loop | The manager — decides what needs doing |
| **tools** | Calculator + clock microservice | The departments — do the actual work |
| **redis** | Per-session conversation memory | The office register — remembers who said what |

Part of the *Dockerize Everything: ML → LLM → Agents* masterclass.
This is **Project 3 of 3** (after QuickBite ETA and ScalerGPT).

---

## ⚠️ Read this first — the rules that prevent 90% of problems

**1. After editing ANY file, you must rebuild.**
```bash
docker compose up -d --build
```
The image is a *photograph*, not a *mirror*. Editing a file does not update the
photograph — you have to take a new one.

**2. `docker compose ps` hides dead containers.**
If a service is missing from the list, it exited. Use `docker compose ps -a`,
then `docker compose logs <service>` for the reason.

**3. Don't paste commands with trailing `#` comments into zsh.**
If your terminal shows `quote>`, press **Ctrl+C** and re-run without the comment.

**4. Edited `.env`? Recreate, don't just restart.**
```bash
docker compose up -d --force-recreate
```
Environment variables are read once, at container start.

---

## 🆕 What's new versus the LLM project

| New concept | Why it appears here |
|---|---|
| **Three services, two custom builds** | `agent/` and `tools/` each have their own code, requirements, and Dockerfile — microservices made physical. |
| **A service with NO published port** | `tools` has no `ports:` section. The outside world cannot reach it *at all* — only the agent can, over the private network. |
| **The agent loop** | The LLM is shown a menu of tools and may say "run calculator with 23*47" — we execute it and feed the result back, in a loop. |
| **Stateful memory in Redis** | Conversation history per `session_id`, surviving container restarts via a volume. |

---

## 📁 What's in this folder

| File | Purpose |
|---|---|
| `agent/app.py` | The agent: loads memory from Redis, runs the think→act→observe loop, calls tools over HTTP |
| `agent/requirements.txt` | fastapi, uvicorn, openai, redis, httpx |
| `agent/Dockerfile` | Standard 6-liner, serves on port 9000 |
| `tools/app.py` | Plain FastAPI microservice: `POST /calculator`, `GET /datetime` |
| `tools/requirements.txt` | Just fastapi + uvicorn — tools have no AI in them |
| `tools/Dockerfile` | Standard 6-liner, serves on port 7000 |
| `docker-compose.yml` | All three services, the private network, the volume |
| `.env.example` | Template for your OpenAI key — copy to `.env` |
| `.dockerignore` / `.gitignore` | Keep secrets and junk out of images and git |

---

## ✅ Prerequisites

1. **Docker Desktop** running (whale 🐳 icon steady in the menu bar).
2. **An OpenAI API key** with credit — <https://platform.openai.com/api-keys>.
   The demo uses `gpt-4o-mini`; a full run costs a fraction of a cent.

You do **not** need Python installed locally.

---

## 🚀 Step-by-step

### Step 1 — Extract and open in VS Code
Unzip and move the folder to e.g. `~/Projects/deskbuddy`, then:
```bash
code ~/Projects/deskbuddy
```

### Step 2 — Create your `.env` file ⚠️ don't skip
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your real key:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```
No quotes, no spaces around the `=`. Verify: `ls -la .env`

(If you already did ScalerGPT, you can copy that project's `.env` — same key.)

### Step 3 — Confirm Docker Desktop is running
Whale 🐳 icon steady in the menu bar.

### Step 4 — Start all three containers
```bash
docker compose up -d --build
```
First run takes 2–4 minutes: it builds TWO images (agent and tools) and pulls
Redis from Docker Hub. Watch the output — you'll see both builds happen.

### Step 5 — Verify all three are up
```bash
docker compose ps -a
```
Expect `deskbuddy-agent`, `deskbuddy-tools`, and `deskbuddy-redis` — all **Up**.
If any says **Exited**, run `docker compose logs <service>` and check the
Troubleshooting table below.

### Step 6 — Health check
```bash
curl http://localhost:9000/
```
```json
{"status": "DeskBuddy Agent is live 🤖", "tools_url": "http://tools:7000", "redis_host": "redis"}
```

### Step 7 — Prove the tools service is private 🔒
This is a feature, not a bug — try to reach tools from your Mac:
```bash
curl http://localhost:7000/
```
**Connection refused — on purpose.** The `tools` service has no `ports:` section
in the compose file, so it has no street entrance. Only the agent, living inside
the same private Docker network, can reach it at `http://tools:7000`.

To prove it works *from the inside*, step into the agent's container and call it:
```bash
docker compose exec agent python -c "import httpx; print(httpx.get('http://tools:7000/').json())"
```
```json
{'status': 'DeskBuddy Tools is live 🧰'}
```
Same URL that failed from your Mac, works from a neighbor. *Internal ports for
neighbors, published ports for visitors.*

### Step 8 — Talk to the agent 🎉
Give it a task that needs **two different tools**:
```bash
curl -X POST http://localhost:9000/chat -H "Content-Type: application/json" -d '{"session_id": "demo", "message": "What is 23*47, and what time is it right now?"}'
```
The agent will call the calculator AND the clock, then compose one answer
mentioning both **1081** and the current time.

### Step 9 — Prove it has memory 🧠
Same `session_id`, follow-up question with no numbers in it:
```bash
curl -X POST http://localhost:9000/chat -H "Content-Type: application/json" -d '{"session_id": "demo", "message": "Now double that multiplication result"}'
```
It answers **2162** — it remembered 1081 from the previous request, because the
history lives in Redis under `history:demo`.

Now change the session and ask the same follow-up:
```bash
curl -X POST http://localhost:9000/chat -H "Content-Type: application/json" -d '{"session_id": "someone-else", "message": "Now double that multiplication result"}'
```
It has no idea what you mean — separate session, separate memory. Per-user
isolation, for free.

### Step 10 — Watch the agent think (the best demo) ⚡
Split your terminal into two panes. In one:
```bash
docker compose logs -f
```
In the other, send a chat request from Step 8 again. You'll see the request
ripple across services live: the agent receiving it, tools serving the
calculator call, the agent responding. This is how multi-service systems are
debugged in real life.

`Ctrl+C` stops watching (the containers keep running).

### Step 11 — Memory survives restarts ♻️
```bash
docker compose down
docker compose up -d
curl -X POST http://localhost:9000/chat -H "Content-Type: application/json" -d '{"session_id": "demo", "message": "What was that multiplication answer again?"}'
```
All three containers were destroyed and recreated, yet it still knows —
Redis stores its data in the `agent_memory` volume.

To actually wipe all memory:
```bash
docker compose down -v
```

### Step 12 — Clean up
```bash
docker compose down       # stop everything, keep the memory
docker compose down -v    # stop everything and wipe the memory too
```

---

## 🔍 How the agent loop works (agent/app.py)

```
loop (max 5 times):
    show the LLM:  conversation so far + the tool menu (TOOL_DEFS)
    if the LLM answers in words        -> break, we're done
    if the LLM says "run tool X(args)" -> call the tools service over HTTP,
                                          append the result to the conversation,
                                          go around again
```

- **TOOL_DEFS** is the menu card: each tool's name, description, and expected
  inputs. The LLM reads the descriptions to decide when a tool is needed.
- **Why max 5 laps?** A safety fuse. A confused model could otherwise call tools
  forever — and every lap costs you API tokens.
- **Why does an LLM need a calculator?** LLMs predict text; they are famously
  unreliable at arithmetic. Giving one a calculator is like giving an eloquent
  manager an actual accountant.
- **Why no retry loop for Redis** (unlike ScalerGPT's Chroma)? The Redis client
  connects *lazily* — only when the first command runs, which is your first
  `/chat` request, long after Redis has booted. Chroma's client connects
  immediately at startup, which is why it needed the polite-knocking loop.

---

## 🪤 Troubleshooting

| Problem | Fix |
|---|---|
| Edited a file, nothing changed | Rebuild: `docker compose up -d --build` |
| A service missing from `docker compose ps` | It exited. `docker compose ps -a`, then `docker compose logs <service>`. |
| Agent exits with `OPENAI_API_KEY is missing` | Step 2. Create `.env` with a real key, then `docker compose up -d --force-recreate`. |
| `AuthenticationError` / `401` in agent logs | Key is wrong, or has stray quotes/spaces in `.env`. |
| `RateLimitError` / `insufficient_quota` | No credit on your OpenAI account. Add billing. |
| `curl localhost:7000` fails | **That's correct behavior** — tools is private by design. See Step 7. |
| `port is already allocated` on 9000 | `lsof -i :9000` to find the culprit, or change the mapping to `"9090:9000"`. |
| `tool call failed` inside the answer | Tools container is down: `docker compose ps -a`, `docker compose logs tools`. |
| Agent gives a wrong/odd answer | Check `docker compose logs -f` while asking — you can see whether tools were actually called. |
| Terminal stuck at `quote>` | You pasted a `#` comment into zsh. Ctrl+C, re-run without it. |
| Edited `.env`, no effect | `docker compose up -d --force-recreate` |

---

## 🔑 Key concepts demonstrated

- **Microservice separation** — agent and tools are independent services with
  independent code, dependencies, images, and lifecycles
- **Private services** — omitting `ports:` removes the public entrance entirely;
  the strongest security line in the file is the one that isn't there
- **Service-name networking** — `http://tools:7000`, `host="redis"`; never IPs
- **The agent pattern** — think → act → observe, with a loop cap as a safety fuse
- **Stateful memory** — Redis + a volume = conversations that survive restarts
- **Lazy vs eager connections** — why Redis needs no retry loop but Chroma did

---

## 🏠 Homework

1. **Easy** — Add a third tool to `tools/app.py` (e.g. a random-number endpoint),
   describe it in `TOOL_DEFS`, rebuild, and ask the agent to use it.
2. **Medium** — Add a `GET /history/{session_id}` endpoint to the agent that
   returns the stored conversation from Redis.
3. **Hard** — Add a *weather* tool that calls a free weather API, updating ONLY
   the tools service — prove the agent container never rebuilt (check
   `docker images` timestamps).
4. **Boss level** — Add a fourth service: a minimal HTML chat front end served
   by nginx, talking to the agent. Four containers, one compose file.

---

Made with 🐳 for **Future with Shivank**
