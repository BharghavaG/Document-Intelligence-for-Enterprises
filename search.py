from multiprocessing import context
import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from langchain_groq import ChatGroq

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "llama-3.1-8b-instant"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from data_loader import load_all_documents
            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
        groq_api_key = "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"
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    # def search_and_summarize(self, query: str, top_k: int = 3) -> str:
    #     results = self.vectorstore.query(query, top_k=top_k)
    #     texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
    #     context = "\n\n".join(texts)
    #     if not context:
    #         return "No relevant documents found."
    #     prompt = f"""Using the given context: '{context}'\n\n answer the query: {query} in a humanly concise way."""
    #     response = self.llm.invoke([prompt])
    #     return response.content

    def search_and_summarize(self, query: str, top_k: int = 3):
        results = self.vectorstore.query(query, top_k=top_k)
        if not results:
            return{
                "answer": "No relevant documents found.",
                "source": None,
                # "confidence": 0.0
            }
        texts = []
        # similarity_scores = []
        best_source = None

        for r in results:
            meta = r.get("metadata")
            # distance = float(r.get("distance"))
            if meta:
                texts.append(meta.get("text", ""))
                # similarity = 1 / (1 + distance)
                # similarity_scores.append(similarity)
                if best_source is None:
                    # best_source = {
                    #     "pdf_name": os.path.basename(meta.get("source", "unknown")),
                    #     "page_number": int(meta.get("page", "unknown")) + 1
                    # }
                    raw_page = meta.get("page", None)

                    if isinstance(raw_page, (int, float)):
                        page_number = int(raw_page) + 1  # convert 0-index to real page
                    else:
                        page_number = "unknown"

                    best_source = {
                        "pdf_name": os.path.basename(meta.get("source", "unknown")),
                        "page_number": page_number
                    }
        context = "\n\n".join(texts)
        prompt = f"""
        You are an enterprise document assistant.

        Using ONLY the given context:
        {context}

        Answer the following question concisely:
        {query}
        """
        response = self.llm.invoke([prompt])
        answer = response.content
        # confidence = float(sum(similarity_scores) / len(similarity_scores))
        return {
            "answer": answer,
            "source": best_source,
            # "confidence": round(confidence, 4)
        }


# Example usage
if __name__ == "__main__":
    rag_search = RAGSearch()
    query = "What is attention mechanism?"
    answer = rag_search.search_and_summarize(query, top_k=3)
    print("answer:", answer)
