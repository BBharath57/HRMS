"""
RAG pipeline for HR Assistant: shared retriever and llm for knowledge agent.
"""
import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq

load_dotenv()

INDEX_NAME = "hrms-index"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY
)
vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.4,
    api_key=GROQ_API_KEY
)
