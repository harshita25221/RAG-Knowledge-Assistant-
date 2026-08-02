# Meritech AI Knowledge Assistant 🤖

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cut52pbptmjykaqucftgua.streamlit.app/)

**🌐 Live Demo:** [Click here to try the app](https://4bhomdgvsctfeoyyko2vx4.streamlit.app/)

Welcome to the **Meritech AI Knowledge Assistant**! This is a Retrieval-Augmented Generation (RAG) based conversational AI application built to act as a friendly customer support assistant for Meritech network products. It seamlessly answers queries based on your technical documents.

## 🌟 Key Features

- **Retrieval-Augmented Generation (RAG)**: Connects large language models (LLMs) with your custom data to provide accurate and contextually relevant answers.
- **Local Privacy-First AI**: Runs entirely on your local machine using **Ollama** and locally stored vector databases. No data is sent to external API providers.
- **Multi-format Document Support**: Ingests and processes `.pdf`, `.docx`, and `.xlsx` files to build its knowledge base.
- **Context-Aware Conversations**: Employs SQLite to remember past conversations, allowing for seamless follow-up questions.
- **Streamlit Web Interface**: A sleek, modern, and user-friendly web application for chatting with the assistant.
- **Fast Similarity Search**: Utilizes **ChromaDB** for rapid in-memory/local vector storage and retrieval.

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM Framework**: [LangChain](https://www.langchain.com/)
- **Local Model Provider**: [Ollama](https://ollama.ai/) (`qwen2.5:1.5b`)
- **Embeddings**: [FastEmbed](https://qdrant.github.io/fastembed/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Database (Chat History)**: SQLite

## 🚀 Getting Started

Follow these steps to set up and run the assistant on your local machine.

### Prerequisites

1. **Python 3.9+** installed on your system.
2. **Ollama** installed on your machine. [Download Ollama here](https://ollama.ai/download).

### 1. Set Up Ollama & The Model

Before running the app, make sure Ollama is running in the background and that you have pulled the required Qwen model:

```bash
ollama run qwen2.5:1.5b
```
*(You can close the ollama chat interface after the download finishes, but ensure the Ollama background service is running).*

### 2. Clone the Repository

```bash
git clone https://github.com/harshita25221/RAG-Knowledge-Assistant-.git
cd RAG-Knowledge-Assistant-
```

### 3. Create a Virtual Environment & Install Dependencies

```bash
python -m venv venv
# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

### 4. Run the Application

Launch the Streamlit web interface:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

## 📂 Project Structure

```text
├── app.py                  # Main Streamlit application entry point
├── chat.py                 # Core RAG logic, LangChain integration, and ChatBot class
├── evaluate_rag.py         # Script to evaluate RAG responses
├── requirements.txt        # Python dependencies
├── .gitignore              # Files and directories to ignore in version control
├── assets/                 # CSS and image assets for the UI frontend
├── components/             # Reusable UI components (header, sidebar, chat views)
├── utils/                  # Helper utilities and mock data
├── meritech_db/            # (Auto-generated) ChromaDB vector storage directory
└── chat_history.db         # (Auto-generated) SQLite database for conversation memory
```

## 🧠 How it Works

1. **Document Ingestion**: The system loads PDFs, Docs, or Excel files and splits them into smaller text chunks.
2. **Embedding**: The text chunks are converted into mathematical vectors using `FastEmbed` and stored locally in `ChromaDB`.
3. **Query Reformulation**: When you ask a question, the assistant uses conversation history to reformulate it into a standalone query.
4. **Retrieval**: The system searches `ChromaDB` for the 5 most relevant document chunks based on the queried vectors.
5. **Generation**: The retrieved context and your question are passed to the local `qwen2.5:1.5b` model via Ollama to generate a precise, context-aware answer.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.
