"""
DeskBuddy Agent - an LLM with hands.

The agent loop:
  1. Show the LLM the conversation + a menu of available tools
  2. If the LLM answers in words -> done
  3. If the LLM says "run tool X with these arguments" -> we call the
     tools service over HTTP, paste the result back, and loop again
  4. Max 5 laps (a safety fuse so a confused model can't loop forever)

Memory:
  Conversation history is stored in Redis per session_id, so the agent
  remembers context across requests - and across container restarts,
  because Redis has a volume.
"""
import json
import os
import sys

import httpx
import redis
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="DeskBuddy Agent")

# --- Fail loudly and clearly if the key is missing --------------------------
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if not API_KEY or API_KEY.startswith("sk-paste"):
    sys.exit(
        "\n[DeskBuddy] OPENAI_API_KEY is missing.\n"
        "  Fix: cp .env.example .env, put your real key in it, then\n"
        "       docker compose up -d --force-recreate\n"
    )

llm = OpenAI(api_key=API_KEY)

# --- Service addresses: SERVICE NAMES, not IPs (Compose networking) ---------
# redis-py connects lazily (only on first command), so no retry loop needed:
# by the time the first /chat request arrives, Redis is long since ready.
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True,
)
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:7000")

# --- The tool menu we show the LLM ------------------------------------------
# Each entry describes one tool: its name, what it does, and what inputs
# it expects. The LLM reads these descriptions to decide when to use them.
TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a math expression, e.g. '23*47' or '(100-8)/4'",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def call_tool(name: str, args: dict) -> dict:
    """Actually execute a tool by calling the tools microservice over HTTP."""
    try:
        if name == "calculator":
            return httpx.post(f"{TOOLS_URL}/calculator", json=args, timeout=10).json()
        if name == "get_datetime":
            return httpx.get(f"{TOOLS_URL}/datetime", timeout=10).json()
        return {"error": f"unknown tool: {name}"}
    except Exception as e:
        return {"error": f"tool call failed: {e}"}


class Chat(BaseModel):
    session_id: str
    message: str


@app.get("/")
def health():
    return {
        "status": "DeskBuddy Agent is live 🤖",
        "tools_url": TOOLS_URL,
        "redis_host": os.getenv("REDIS_HOST", "redis"),
    }


@app.post("/chat")
def chat(req: Chat):
    # --- 1. Load this session's memory from Redis ---------------------------
    key = f"history:{req.session_id}"
    history = [json.loads(m) for m in r.lrange(key, 0, -1)]
    history.append({"role": "user", "content": req.message})

    # --- 2. The agent loop: think -> act -> observe -> repeat ---------------
    msg = None
    for _ in range(5):  # safety fuse: max 5 laps
        resp = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            tools=TOOL_DEFS,
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            break  # the LLM answered in words - we're done

        # The LLM asked to run one or more tools
        history.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:
            result = call_tool(tc.function.name, json.loads(tc.function.arguments))
            history.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                }
            )

    # --- 3. Save memory back to Redis and return the answer -----------------
    history.append({"role": "assistant", "content": msg.content})
    r.delete(key)
    for m in history:
        r.rpush(key, json.dumps(m))

    return {"answer": msg.content}
