import os
from src.utils import list_pdf_files, extract_text_from_pdf, chunk_text
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

def ingest_pdfs_to_vectorstore(
    pdf_folder: str,
    persist_directory: str,
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    """
    Read all PDFs, chunk, embed, and persist vector store.
    """
    pdf_files = list_pdf_files(pdf_folder)
    docs = []
    metadata_list = []
    for pdf in pdf_files:
        text = extract_text_from_pdf(pdf)
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        for i, chunk in enumerate(chunks):
            md = {"pdf_path": pdf, "chunk_index": i}
            docs.append(Document(page_content=chunk, metadata=md))
    embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)
    vectordb = Chroma.from_documents(documents=docs, embedding=embedder, persist_directory=persist_directory)
    vectordb.persist()
    print(f"Ingested {len(docs)} chunks from {len(pdf_files)} PDF(s).")
