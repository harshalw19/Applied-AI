from langchain_text_splitters import RecursiveCharacterTextSplitter
dummy_document = """# Bengaluru Overview

## Tech Industry
Bengaluru is known as India's Silicon Valley. Tech parks like Electronic City and Whitefield host thousands of tech companies. Major firms include Infosys, Wipro, and TCS.

## Climate
The city sits at 920 meters altitude. This gives it pleasantly cool weather year-round. Average temperatures rarely exceed 30 degrees.

## Food
Bengaluru's food scene is legendary. South Indian classics like masala dosa and idli thrive here. Filter coffee shops dot every street corner."""


#importing file 
with open("/home/harshalwarukar/Desktop/Applied-AI/Langchain/summarizer_langchain.py", "r") as file:
    your_long_document = file.read()
    #rint(your_long_document)  # print first 500 chars to check

splitter = RecursiveCharacterTextSplitter(
    chunk_size=80,        # aim for ~800 chars per chunk
    chunk_overlap=10,     # adjacent chunks share 100 chars (context glue)
)

chunks = splitter.split_text(your_long_document)
print(len(chunks))    # → e.g. 47 chunks ready to embed
print(chunks)
