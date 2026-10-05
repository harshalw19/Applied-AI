# Class 3 · RAG — Code Files

One file per code block in the HTML guide.

```
embeddings.py   ←→  Block 16
chunk.py        ←→  Block 17
index.py        ←→  Block 19 · step 1
rag.py          ←→  Block 19 · step 2
rerank.py       ←→  Block 20
pdf_chat.py     ←→  Block 21 (mini project)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # add your OPENAI_API_KEY
```

## Run order

```bash
python embeddings.py        # no API key needed
python index.py             # builds ./chroma_db
python rag.py               # uses ./chroma_db
python pdf_chat.py          # the shippable Gradio app
```

`chunk.py` and `rerank.py` are teaching snippets — drop their code into the larger pipeline.
