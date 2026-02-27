from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory="data/chroma_db", embedding_function=embeddings)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

query = "Where can I see elephants and what is the entry fee?"
docs = retriever.get_relevant_documents(query)

print(f"\nQuery: {query}\n")
for i, doc in enumerate(docs):
    print(f"{i+1}. {doc.page_content[:200]}...")
    print(f"   [metadata: {doc.metadata}]\n")