import sys
import os

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma

def get_retrieved_documents(query: str, k=5):
    manual_folder = "./meritech_db"
    embeddings = FastEmbedEmbeddings()
    vector_store = Chroma(
        persist_directory=manual_folder,
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
    return retriever.invoke(query)

if __name__ == "__main__":
    docs = get_retrieved_documents("what is sigma-pa")
    for d in docs:
        print("----")
        print(d.page_content)
