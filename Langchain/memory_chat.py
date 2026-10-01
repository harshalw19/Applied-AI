# memory_chat.py
# Block 10 — Version 2: memory that builds ITSELF (nothing hardcoded).
# A real chat loop: after every turn we append the new question + answer.
# Run:  python memory_chat.py   (type 'quit' to stop)
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(model="openai/gpt-oss-120b", api_key=os.getenv('GROQ_API_KEY'), base_url="https://api.groq.com/openai/v1")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant. Use the conversation history to stay consistent."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
chain = prompt | model

history = []                                   # ① starts EMPTY — nothing hardcoded

print("Chat with the bot (type 'quit' to exit).")
while True:                                     # ② one loop = one chat turn
    question = input("You: ")
    if question.strip().lower() in {"quit", "exit"}:
        break

    answer = chain.invoke(
        {"history": history, "question": question}).content   # ③ send history so far
    print("Bot:", answer)

    history.append(HumanMessage(question))      # ④ remember what you said...
    history.append(AIMessage(answer))           # ⑤ ...and what it replied
    print(f"   (history now has {len(history)} messages)")
