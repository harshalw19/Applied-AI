# QuickBite ETA 🛵

A food-delivery **ETA predictor** built with scikit-learn + FastAPI, fully dockerized.
Part of the *Dockerize Everything: ML → LLM → Agents* .

> **Predicts:** how many minutes until a food order arrives, based on distance,
> restaurant prep time, rider availability, and whether it's raining.

---

## 📁 What's in this folder

| File | Purpose |
|---|---|
| `train.py` | Generates synthetic delivery data and trains a RandomForest → saves `eta_model.pkl` |
| `app.py` | FastAPI service that loads the model and exposes `/predict` |
| `requirements.txt` | Pinned Python dependencies (the "shopping list") |
| `Dockerfile` | The recipe — how to build the container image |
| `.dockerignore` | Files that should NOT go into the image |
| `README.md` | This file |

---

## ✅ Prerequisites (macOS)

1. **Docker Desktop** installed and running.
   ```bash
   brew install --cask docker
   ```
   Then open the Docker Desktop app once. You should see a whale 🐳 icon in your menu bar.

2. Verify it works:
   ```bash
   docker --version
   docker run hello-world
   ```

You do **not** need Python, pip, or a virtual environment installed locally.
That's the whole point of this exercise.

---

## 🚀 Step-by-step: run this project

### Step 1 — Extract the folder
Unzip `quickbite-eta.zip` and move the `quickbite-eta` folder somewhere you keep
projects, e.g. `~/Projects/quickbite-eta`.

### Step 2 — Open it in VS Code
Launch VS Code → **File → Open Folder** → select the `quickbite-eta` folder.

Or from the terminal:
```bash
code ~/Projects/quickbite-eta
```

**Recommended VS Code extensions** (optional but handy for the demo):
- *Docker* (by Microsoft) — see your images and containers in the sidebar
- *Python* (by Microsoft) — syntax highlighting for the code walkthrough

### Step 3 — Make sure Docker Desktop is running
Check for the whale 🐳 icon in your menu bar. If it's animating, wait until it's steady.

### Step 4 — Build the image
Open the VS Code integrated terminal with `` Ctrl + ` `` and run:

```bash
docker build -t quickbite-eta:v1 .
```

The first build takes **2–3 minutes** (it pulls the Python base image and installs
scikit-learn). Watch the output — you'll see `Model saved: eta_model.pkl ✅` scroll by,
because the model is trained **inside** the image at build time.

Confirm the image exists:
```bash
docker images
```

### Step 5 — Run the container
```bash
docker run -d -p 8000:8000 --name eta-service quickbite-eta:v1
```

- `-d` → run in the background (detached)
- `-p 8000:8000` → map port 8000 on your Mac to port 8000 inside the container
- `--name eta-service` → give the container a friendly name

Check it's alive:
```bash
docker ps
```

### Step 6 — Test the API

**Option A — curl:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"distance_km": 4.5, "prep_time_min": 15, "rider_available": 1, "is_raining": 1}'
```

Expected response:
```json
{"eta_minutes": 40.5, "message": "Your food arrives in 40.5 min 🍔"}
```

**Option B — Swagger UI (best for live demos):**
Open **http://localhost:8000/docs** in your browser, expand `POST /predict`,
click *Try it out*, edit the values, and hit *Execute*.

Try flipping `"is_raining"` from `0` to `1` and watch the ETA jump by ~9 minutes.

### Step 7 — Explore the running container (optional, great demo moment)
```bash
docker logs -f eta-service          # watch live logs (Ctrl+C to exit)
docker exec -it eta-service bash    # step INSIDE the container
  ls                                # you'll see app.py, eta_model.pkl, etc.
  cat app.py
  exit
```

### Step 8 — Clean up
```bash
docker stop eta-service
docker rm eta-service
docker rmi quickbite-eta:v1         # optional: also delete the image
```

---

## 🐍 Optional: run locally WITHOUT Docker

Useful only if you want to demonstrate the "before Docker" pain for contrast.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python train.py
uvicorn app:app --reload
```

Then visit http://localhost:8000/docs

Deactivate with `deactivate` when done.

---

## 🍎 Apple Silicon (M1/M2/M3/M4) note

If you hit a platform mismatch warning or plan to deploy this image to a cloud
server (which is usually x86), build for AMD64:

```bash
docker build --platform linux/amd64 -t quickbite-eta:v1 .
docker run --platform linux/amd64 -d -p 8000:8000 --name eta-service quickbite-eta:v1
```

---

## 🪤 Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop isn't open. Launch it and wait for the whale icon. |
| `port is already allocated` | Something else is on 8000. Find it with `lsof -i :8000`, or use a different host port: `-p 8080:8000` (then test on `localhost:8080`). |
| `The container name "/eta-service" is already in use` | Remove the old one: `docker rm -f eta-service` |
| Build is very slow / disk full | Check usage with `docker system df`, then clean up with `docker system prune` |
| Platform / arch warning | Add `--platform linux/amd64` to build and run |
| Code changes not showing up | You must rebuild: `docker build -t quickbite-eta:v1 .` then re-run |

---

## 🔑 Key concepts demonstrated here

- **Dockerfile anatomy** — `FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, `CMD`
- **Layer caching** — `requirements.txt` is copied *before* the rest of the code, so
  dependency installation is cached and only re-runs when dependencies actually change
- **Port mapping** — `-p host:container`
- **`.dockerignore`** — keeping `venv/`, `.git/`, and secrets out of the image
- **Build-time training** — the model is baked into the image, so the container is
  fully self-contained at runtime

---

## 🏠 Homework

1. **Easy** — Push this image to Docker Hub: `docker tag` + `docker push`
2. **Medium** — Add a `/batch_predict` endpoint that accepts a list of orders
3. **Hard** — Convert the Dockerfile to a **multi-stage build** and cut the image size by 40%

---

Made with 🐳 for **Future with Shivank**
