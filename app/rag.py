from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

from app.config import GOOGLE_API_KEY, CHROMA_DIR, MODEL_NAME

# Setup embeddings and LLM
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)

base_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Token budget retriever to limit context size
class TokenBudgetRetriever(BaseRetriever):
    underlying_retriever: BaseRetriever
    max_characters: int = 6000

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        docs = self.underlying_retriever.invoke(query, config={"callbacks": run_manager.get_child()})
        return self._truncate_docs(docs)

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        docs = await self.underlying_retriever.ainvoke(query, config={"callbacks": run_manager.get_child()})
        return self._truncate_docs(docs)

    def _truncate_docs(self, docs: List[Document]) -> List[Document]:
        truncated_docs = []
        current_chars = 0
        for doc in docs:
            doc_len = len(doc.page_content)
            if current_chars + doc_len > self.max_characters:
                remaining = self.max_characters - current_chars
                if remaining > 100:
                    doc.page_content = doc.page_content[:remaining] + "... (context truncated to fit token budget)"
                    truncated_docs.append(doc)
                break
            truncated_docs.append(doc)
            current_chars += doc_len
        return truncated_docs

retriever = TokenBudgetRetriever(underlying_retriever=base_retriever)

prompt = ChatPromptTemplate.from_template(
    """
You are a finance assistant.
Answer using the provided finance context when relevant.
If the answer is not in the context, say that clearly.

Context:
{context}

Question:
{input}
"""
)

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)