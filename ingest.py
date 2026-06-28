from pathlib import Path

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from app.config import GOOGLE_API_KEY, DOCS_DIR, CHROMA_DIR

def load_documents():
    docs = []
    docs_path = Path(DOCS_DIR)

    for file in docs_path.iterdir():
        if file.suffix == ".txt" or file.suffix == ".md":
            loader = TextLoader(str(file), encoding="utf-8")
            docs.extend(loader.load())
        elif file.suffix == ".pdf":
            loader = PyPDFLoader(str(file))
            docs.extend(loader.load())

    return docs

def main():
    documents = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print(f"Ingested {len(chunks)} finance chunks into {CHROMA_DIR}")

if __name__ == "__main__":
    main()