# agent.py
# Block 11 — your first tiny AGENT: an LLM + one tool + a loop.
# The model decides, on its own, when to call the tool.
# Run:  python agent.py
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('GROQ_API_KEY'),
                base_url="https://api.groq.com/openai/v1")  # or set your

# ---- our tiny "database" (a dict standing in for a real one) ----
PRICES = {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699}


# ---- Step 1: the tool is just a normal Python function ----
def get_price(item):
    print(f"🔧 tool called: get_price({item})")        # so you SEE it happen
    return f"₹{PRICES.get(item.lower(), 'unknown')}"    # .get -> no crash if missing


# ---- Step 2: describe the tool so the model knows it exists ----
tools = [{
    "type": "function",
    "function": {
        "name": "get_price",
        "description": "Get the price of a shop item the user asks about.",
        "parameters": {
            "type": "object",
            "properties": {"item": {"type": "string", "description": "the item name"}},
            "required": ["item"],
        },
    },
}]


# ---- Step 3: the loop — think -> maybe call tool -> answer ----
def agent(user_message):
    messages = [{"role": "user", "content": user_message}]

    # 1. send the message + the tools menu; the model may ask for a tool
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", messages=messages, tools=tools)
    msg = response.choices[0].message

    # 2. did it ask for a tool? 

    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)   # 3. read its request...
            result = get_price(args["item"])             #    ...and run the real function
            messages.append({
                "role": "tool",                          # a third role!
                "tool_call_id": call.id,
                "content": result,
            })
        # 4. send everything back so it can answer nicely
        response = client.chat.completions.create(model="openai/gpt-oss-120b", messages=messages)
        msg = response.choices[0].message

    return msg.content


if __name__ == "__main__":
    print(agent("How much are the shoes?"))       # -> uses the tool -> "₹799"
    print(agent("Hi! What can you help with?"))    # -> no tool needed -> just chats
