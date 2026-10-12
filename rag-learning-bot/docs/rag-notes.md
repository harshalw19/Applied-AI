# Retrieval Augmented Generation

RAG stands for Retrieval Augmented Generation. It is a technique for making a large
language model answer questions about private data that it was never trained on, without
fine tuning the model itself.

The pipeline has three stages. First, retrieval: the user's question is converted into a
vector and compared against a vector database to find the most semantically similar chunks
of source material. Second, augmentation: those retrieved chunks are inserted into the
prompt as context. Third, generation: the language model writes an answer grounded in that
supplied context rather than in its own memory.

An embedding is a numerical representation of text as a list of floating point numbers.
Text with similar meaning produces vectors that sit close together in that space, which is
what makes semantic search possible. Keyword search would miss the connection between
"container" and "Docker box", but embeddings capture it.

A vector database such as Chroma stores these embeddings alongside the original text and
supports fast nearest neighbour lookup. Chroma can run as a standalone server in its own
container, which lets your application container stay small and stateless.

Chunking matters a great deal for RAG quality. Chunks that are too large dilute relevance
and waste tokens, while chunks that are too small lose the surrounding context needed to
make sense of the text. Splitting on paragraph boundaries is a reasonable starting point.
