import os
from langchain_groq import ChatGroq
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceBgeEmbeddings

def initialize_llm():
    return ChatGroq(
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile"  # or any other model supported
    )
#alternative "llama3-70b-8192" if above doesnot work

def create_or_load_vector_db(pdf_path, db_path):
    # Use a real huggingface model that works with sentence embeddings
    embeddings = HuggingFaceBgeEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    
    if not os.path.exists(db_path):
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = splitter.split_documents(docs)
        db = Chroma.from_documents(texts, embeddings, persist_directory=db_path)
        db.persist()
    else:
        db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    
    return db
