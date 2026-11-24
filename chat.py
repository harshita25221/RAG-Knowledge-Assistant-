#We are using Ollama because it allows LLMs to run locally on your machine, without using cloud services like OpenAI which requires API calling. 
from langchain_community.vectorstores import Chroma 
#Chroma is being used as a vector store to store the embeddings of the documents because it is in-memory and allows fast retrieval and also it is good for development purposes as it stores embeddings directly in memory. 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredExcelLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os
import threading
import chromadb

_chroma_clients = {}
_chroma_lock = threading.Lock()

def get_chroma_client(path: str):
    abs_path = os.path.abspath(path)
    with _chroma_lock:
        if abs_path not in _chroma_clients:
            _chroma_clients[abs_path] = chromadb.PersistentClient(path=abs_path)
        return _chroma_clients[abs_path]


GROQ_MODEL = "llama-3.3-70b-versatile"

def get_groq_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass
    return key

GROQ_API_KEY = get_groq_api_key()
#The manual_folder is being used to store the knowledge base permnanently on the local machine. 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_DIR = os.path.join(BASE_DIR, "meritech_db")
manual_folder = DEFAULT_DB_DIR
#The chat_log_file is being used to store the chat history in a SQLite database file.
#sqllite is a self-contained serverless database engine. It stores the database as the single file, right inside your project folder.
chat_log_file = "sqlite:///chat_history.db"

class ChatBot:
    def __init__(self, chunk_size=1000, chunk_overlap=200, embedding_model=None, persist_dir=None):
        api_key = get_groq_api_key()
        self.chat_model = ChatGroq(model_name=GROQ_MODEL, api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embeddings = embedding_model if embedding_model else FastEmbedEmbeddings()
        self.manual_folder = os.path.abspath(persist_dir) if persist_dir else DEFAULT_DB_DIR
        self.question_retriever = self._create_rewriter()
        self.chat_bot_personality_rules = self._create_personality_rules()
        self.conversation_chain = self._create_conversation_chain()

    
    #Every document loader creates a metadata dictionary for each document, which is used to store the background details of the document, rather than the actual text stored inside it, such as file name, file path etc.     
    #Type Hunting is used to determine the type of data being passed to the function  and the type of output being returned by the function.
    def _load_files(self, file_paths : str)->list:
        """Determines the proper loader based on the file extension and loads the documents from the given file paths."""
        ext = os.path.splitext(file_paths)[-1].lower()
        if not os.path.exists(file_paths):
            raise FileNotFoundError(f"File not found: {file_paths}")
        if ext==".pdf":
            loader = PyPDFLoader(file_paths).load()
        elif ext in [".doc", ".docx"]:
            loader = Docx2txtLoader(file_paths).load()
        elif ext == ".xlsx":
            loader = UnstructuredExcelLoader(file_paths).load()
        else:
            raise ValueError(f"Unsupported File format : {ext}")
        
        return loader 
    
    def _split_documents(self, documents :list)->list:
        """Splits the loaded documents into smaller chunks for faster processing and embedding."""
        chunk = self.text_splitter.split_documents(documents)
        #We are using filter_complex_metadata to filter out any complex metadata like nested dictionaries or lists, because Chroma does not support complex metadata and will throw an error. 
        return filter_complex_metadata(chunk)
    
    def _embed_documents(self, clean_chunks :list):
        """The clean_chunks are embedded and then stored into the vector database "Chroma " for fast retrieval."""
        client = get_chroma_client(self.manual_folder)
        Chroma.from_documents(documents=clean_chunks, embedding=self.embeddings, client=client)


    def _create_rewriter(self) -> ChatPromptTemplate:
        system_prompt = ("Given a chat history and the latest user question"
                         "which might reference context in the chat history,"
                         "formulate a standalone question that can be understood"
                         "without chat history. Do not answer the question,"
                         "just reformulate it if needed and If the question is already standalone, return it as it is.")
        #MessagesPlaceholder holds a list of conversational logs (chat history) and is used to provide context to the model while reformulating the question. 
        return ChatPromptTemplate.from_messages([
           ("system",system_prompt),
           MessagesPlaceholder("chat_history"),
           ("human","{input}")

        ])

    def _create_personality_rules(self)->ChatPromptTemplate:
        system_prompt = (
        "You are a friendly customer support assistant for Meritech network products.\n"
        "STRICT CONSTRAINTS:\n"
        "1. Answer queries naturally, but ONLY use information explicitly stated in the provided technical context.\n"
        "2. If a user asks about everyday objects, animals, or concepts completely unrelated to Meritech or networking (like 'seagull'), you must NOT explain, define, or discuss that topic at all.\n"
        "3. Instead, simply state politely that the topic is outside the scope of Meritech's technical documentation and ask how you can help them with Meritech products.\n"
        "4. Keep your helpful refusal friendly and at least 5 sentences long.\n\n"
        "Context:\n{context}"
    )
        return ChatPromptTemplate.from_messages(
            [("system",system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")])
    
    def _create_conversation_chain(self):
        """The function connects the databases, LLM's, prompts into a single conversational pipeline"""
        if not os.path.exists(self.manual_folder):
            return None
        try:
            client = get_chroma_client(self.manual_folder)
            vector_store = Chroma(
                client=client,
                embedding_function=self.embeddings
            )
            #Turns the database connection to a retriever which is a search engine, to retrieve top 5 most mathematically similar chunks.
            retriever = vector_store.as_retriever(
                search_type = "similarity",
                search_kwargs = {"k":5},
            )
            #SubChain-A
            history_aware_retriever = create_history_aware_retriever(self.chat_model, retriever, self.question_retriever)
            #SubChain-B
            question_answer = create_stuff_documents_chain(self.chat_model, self.chat_bot_personality_rules)
            #Merges Sub-Chain A and Sub-Chain B together.
            master_chain = create_retrieval_chain(history_aware_retriever, question_answer)
            return RunnableWithMessageHistory(
                master_chain, 
                lambda session_id: SQLChatMessageHistory(session_id=session_id, connection=chat_log_file), 
                input_messages_key="input", 
                history_messages_key="chat_history", 
                output_messages_key="answer"
            )
        except Exception as e:
            print(f"Error initializing conversation chain with Chroma: {e}")
            return None
            
    def _ingest_documents(self, file_paths : list[str])->str:
        master_chunk_list = []
        for paths in file_paths:
            raw_docs = self._load_files(paths)

        
            file_chunks = self._split_documents(raw_docs)
            master_chunk_list.extend(file_chunks)
        if not master_chunk_list:
            return "No texts were sucessfully processed"
        self._embed_documents(master_chunk_list)
        self.conversation_chain = self._create_conversation_chain()
        return f"Successfully processed {len(master_chunk_list)} text segments into the knowledge base."
    
    def _get_retrieved_documents(self, query: str, k=5):
        if not os.path.exists(self.manual_folder):
            return []
        try:
            client = get_chroma_client(self.manual_folder)
            vector_store = Chroma(
                client=client,
                embedding_function=self.embeddings)
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k},
            )
            return retriever.invoke(query)
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def _ask(self, query:str, session_id:str = "default_session")->str:
        """A public function to call when u want to chat with the chatbot, it requires your query text and optional session id"""
        if not self.conversation_chain:
            self.conversation_chain = self._create_conversation_chain()
        if not self.conversation_chain:
            return "The knowledge base is empty or being initialized."
        
        response = self.conversation_chain.invoke(
            {"input":query},
            config={"configurable": {"session_id": session_id}}
        )
        return response["answer"]
        

if __name__ == "__main__":
        # Minimal CLI entry to avoid IndentationError and allow quick sanity check
    
    bot = ChatBot()
    print("ChatBot initialized")
    file_path =["Sigma-ml.pdf", "Centra-SD.pdf", "Centra-Experitest.pdf"]
    for paths in file_path:
      if not os.path.exists(paths):
        print(f"File path not found {paths}")
    else:
        documents = bot._ingest_documents(file_path)
        print(documents)
        print("----Testing chatbot answering----")
        user_query = "What is Sigma-Pa ?"
        print(f"User Question : {user_query}")
        reply = bot._ask(user_query, session_id="testing_session_001")
        print(f"\nBot Response:\n{reply}")
