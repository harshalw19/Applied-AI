# memory_demo.py
# Block 10 — Version 1: memory with the history typed by hand
# (shows the IDEA: the model only "remembers" because WE re-send past messages).
# Run:  python memory_demo.py
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url="https://api.groq.com/openai/v1", model="openai/gpt-oss-120b")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly tutor."),
    MessagesPlaceholder("history"),     # past turns slot in here
    ("human", "{question}"),
])
chain = prompt | model

# we hardcode the history here just to demonstrate
history = [HumanMessage("My Name is Harshal, I am a Devops and AI Engineer"), AIMessage("Hi Harshal!")]
ques=input("Whats in your mind today? ")
answer = chain.invoke({"history": history, "question": ques})
print(answer.content)   # -> "Your name is Harshal."  (it "remembered" because we re-sent history)
