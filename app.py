import os
import streamlit as st
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

DATA_DIR = "data"
FAISS_DIR = "faiss_store"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)

st.set_page_config(page_title="Enterprise Document Intelligence", layout="wide")
st.title("Enterprise Orchestrator")



if "vector_store_built" not in st.session_state:
    st.session_state.vector_store_built = False


# File Upload
st.sidebar.header("Upload Documents")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_path = os.path.join(DATA_DIR, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

    

    #with st.spinner("Building FAISS index (one-time process)..."):
        docs = load_all_documents(DATA_DIR)
        store = FaissVectorStore(FAISS_DIR)
        store.build_from_documents(docs)
        store.load()
    #st.sidebar.success("Files uploaded successfully!")
    st.session_state.vector_store_built = True
    #st.sidebar.success("Vector store ready!")


if not st.session_state.vector_store_built:
    if os.path.exists(os.path.join(FAISS_DIR, "index.faiss")):
        st.session_state.vector_store_built = True


# Query Section
st.header("Ask a Question")

query = st.text_input("Enter your query")

if st.button("Search"):

    if not st.session_state.vector_store_built:
        st.warning("Please upload documents first.")
    else:
        with st.spinner("Searching..."):
            rag_search = RAGSearch()
            result = rag_search.search_and_summarize(query, top_k=3)

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Source")
        st.write(result["source"])
