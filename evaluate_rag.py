import pandas as pd 
import time 
import os
import shutil
from tabulate import tabulate
from chat import ChatBot
from langchain_community.embeddings import FastEmbedEmbeddings, HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import warnings
warnings.filterwarnings("ignore")

test_suites = [
    {
        "query":"What is sigma-PA?",
        "expected_keywords":["packet analyzer", "layers 3-7", "deep packet inspection"],
        "target_source":"Meritech Sigma-pa.pdf"
    },
    {
        "query":"What technologies does Sigma-La support?",
        "expected_keywords":["nr5g", "lte", "gsm", "gprs"],
        "target_source":"Sigma mertich product (2).pdf"},
     {
        "query":"What is sea-gull?",
        "expected_keywords":["don't know", "outside the scope", "no information", "not mentioned"],
        "target_source":None
    },
    {
        "query": "What is the storage formula for Sigma-PA?",
        "expected_keywords": ["storage needed", "network traffic speed", "how long you want to keep it"],
        "target_source": "Meritech Sigma-pa.pdf"
    }
]

JUDGE_MODEL = "qwen2.5:1.5b"
JUDGE_URL = "http://localhost:11434"
judge_llm = ChatOllama(model=JUDGE_MODEL, base_url=JUDGE_URL, temperature=0.0)

def score_mrr(retrieved_docs, expected_source, expected_keywords):
    if not retrieved_docs:
        return 0.0
    for rank, doc in enumerate(retrieved_docs):
        metadata_source = doc.metadata.get("source", "")
        content = doc.page_content.lower()
        is_source_match = expected_source and expected_source in metadata_source
        is_keyword_match = any(kw.lower() in content for kw in expected_keywords) if expected_keywords else False
        if (is_source_match or not expected_source) and is_keyword_match:
            return 1.0 / (rank + 1)
    return 0.0

def extract_score(score_str):
    import re
    matches = re.findall(r"0\.\d+|1\.0|0|1", score_str)
    if matches:
        try:
            return float(matches[0])
        except:
            return 0.0
    return 0.0

def score_relevance(query, answer, expected_keywords):
    prompt = ChatPromptTemplate.from_template(
        "You are an expert evaluator. Assess if the following Answer adequately addresses the Question and contains the necessary concepts.\n"
        "Question: {query}\n"
        "Expected Concepts: {keywords}\n"
        "Answer: {answer}\n"
        "Score ONLY with a single number between 0.0 and 1.0, where 1.0 is perfectly relevant. Output ONLY the number."
    )
    chain = prompt | judge_llm
    try:
        res = chain.invoke({"query": query, "keywords": ", ".join(expected_keywords), "answer": answer}).content.strip()
        return extract_score(res)
    except Exception as e:
        print("Error in relevance scoring:", e)
        return 0.0

def score_faithfulness(query, answer, context_docs):
    context_text = "\n---\n".join([d.page_content for d in context_docs])
    prompt = ChatPromptTemplate.from_template(
        "You are an expert evaluator. Assess if the following Answer is entirely supported by the Context.\n"
        "Question: {query}\n"
        "Context: {context}\n"
        "Answer: {answer}\n"
        "If the answer contains information NOT present in the context (hallucination), give a lower score. "
        "Score ONLY with a single number between 0.0 and 1.0, where 1.0 is perfectly faithful. Output ONLY the number."
    )
    chain = prompt | judge_llm
    try:
        res = chain.invoke({"query": query, "context": context_text, "answer": answer}).content.strip()
        return extract_score(res)
    except Exception as e:
        print("Error in faithfulness scoring:", e)
        return 0.0

def main():
    chunk_sizes = [500, 1000, 1500]
    embeddings_configs = {
        "FastEmbed": FastEmbedEmbeddings(),
        "HF_MiniLM": HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
        "Ollama_Nomic": OllamaEmbeddings(model="nomic-embed-text")
    }
    
    file_paths = ["Meritech Sigma-pa.pdf", "Sigma mertich product (2).pdf"]
    results = []
    
    for size in chunk_sizes:
        for emb_name, emb_model in embeddings_configs.items():
            print(f"\n--- Evaluating Chunk Size: {size}, Embeddings: {emb_name} ---")
            persist_dir = f"./db_eval_{size}_{emb_name}"
            
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir, ignore_errors=True)
                
            bot = ChatBot(chunk_size=size, chunk_overlap=int(size*0.1), embedding_model=emb_model, persist_dir=persist_dir)
            print("Ingesting documents...")
            status = bot._ingest_documents(file_paths)
            print(status)
            
            mrr_scores = []
            rel_scores = []
            faith_scores = []
            retrieval_times = []
            response_times = []
            
            for suite in test_suites:
                query = suite["query"]
                exp_keywords = suite["expected_keywords"]
                exp_source = suite["target_source"]
                
                start_r = time.time()
                retrieved_docs = bot._get_retrieved_documents(query)
                end_r = time.time()
                retrieval_time = end_r - start_r
                
                start_a = time.time()
                answer = bot._ask(query, session_id=f"eval_{size}_{emb_name}")
                end_a = time.time()
                response_time = end_a - start_a
                
                if exp_keywords and exp_keywords[0] == "don't know":
                    mrr = 1.0 
                else:
                    mrr = score_mrr(retrieved_docs, exp_source, exp_keywords)
                
                rel = score_relevance(query, answer, exp_keywords)
                faith = score_faithfulness(query, answer, retrieved_docs)
                
                mrr_scores.append(mrr)
                rel_scores.append(rel)
                faith_scores.append(faith)
                retrieval_times.append(retrieval_time)
                response_times.append(response_time)
                print(f"  Q: '{query}' -> MRR: {mrr:.2f}, Rel: {rel:.2f}, Faith: {faith:.2f}, Retr (s): {retrieval_time:.2f}, Resp (s): {response_time:.2f}")
                
            avg_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0
            avg_rel = sum(rel_scores) / len(rel_scores) if rel_scores else 0
            avg_faith = sum(faith_scores) / len(faith_scores) if faith_scores else 0
            avg_retrieval = sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0
            avg_response = sum(response_times) / len(response_times) if response_times else 0
            
            results.append({
                "Chunk Size": size,
                "Embeddings": emb_name,
                "MRR": round(avg_mrr, 2),
                "Relevance": round(avg_rel, 2),
                "Faithfulness": round(avg_faith, 2),
                "Avg Retrieval Velocity (s)": round(avg_retrieval, 2),
                "Avg Response Time (s)": round(avg_response, 2)
            })
            
            # Clean up db
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir, ignore_errors=True)
                
    df = pd.DataFrame(results)
    print("\n\n=== Final Evaluation Report ===")
    print(tabulate(df, headers='keys', tablefmt='pipe', showindex=False))
    df.to_csv("evaluation_results.csv", index=False)
    print("Report saved to evaluation_results.csv")
    
    # Save a markdown copy as well
    with open("evaluation_report.md", "w") as f:
        f.write("# RAG Evaluation Report\n\n")
        f.write(tabulate(df, headers='keys', tablefmt='pipe', showindex=False))

if __name__ == "__main__":
    main()