"""
DeskBuddy Tools - a tiny microservice exposing two tools:
  POST /calculator  -> evaluates a math expression
  GET  /datetime    -> returns the current date & time

Nothing AI about this file. It's a plain worker department.
The agent (a separate container) calls these over the private Docker network.
"""
import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="DeskBuddy Tools")


class Calc(BaseModel):
    expression: str


@app.get("/")
def health():
    return {"status": "DeskBuddy Tools is live 🧰"}


@app.post("/calculator")
def calculator(c: Calc):
    """Evaluate a math expression like '23*47' or '(100-8)/4'."""
    try:
        # Demo only — never use eval on untrusted input in production!
        # The empty __builtins__ blocks access to dangerous functions,
        # but a real system would use a proper math parser.
        result = eval(c.expression, {"__builtins__": {}})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


@app.get("/datetime")
def now():
    """Return the current date and time in ISO format."""
    return {"now": datetime.datetime.now().isoformat()}
