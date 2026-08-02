import sys
import os

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

def test_chain():
    manual_folder = "./meritech_db"
    embeddings = FastEmbedEmbeddings()
    vector_store = Chroma(
        persist_directory=manual_folder,
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )
    
    llm = ChatGroq(model_name="llama-3.1-8b-instant")
    
    system_prompt = (
        "You are a friendly customer support assistant for Meritech network products.\n"
        "STRICT CONSTRAINTS:\n"
        "1. Answer queries naturally, but ONLY use information explicitly stated in the provided technical context.\n"
        "2. If a user asks about everyday objects, animals, or concepts completely unrelated to Meritech or networking (like 'seagull'), you must NOT explain, define, or discuss that topic at all.\n"
        "3. Instead, simply state politely that the topic is outside the scope of Meritech's technical documentation and ask how you can help them with Meritech products.\n"
        "4. Keep your helpful refusal friendly and at least 5 sentences long.\n\n"
        "Context:\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, chain)
    
    response = retrieval_chain.invoke({"input": "what is sigma-pa"})
    print("8b response:", response["answer"])
    
    llm70 = ChatGroq(model_name="llama3-70b-8192")
    chain70 = create_stuff_documents_chain(llm70, prompt)
    retrieval_chain70 = create_retrieval_chain(retriever, chain70)
    
    response70 = retrieval_chain70.invoke({"input": "what is sigma-pa"})
    print("70b response:", response70["answer"])

if __name__ == "__main__":
    test_chain()
