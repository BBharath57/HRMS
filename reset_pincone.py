import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Load Keys
load_dotenv()
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")
INDEX_NAME = "hrms-index"

# 2. Setup Pinecone
pc = Pinecone(api_key=PINECONE_KEY)

# 3. Detect Correct Dimension
print("🔍 Checking model dimension...")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001", 
    google_api_key=GOOGLE_KEY
)
# Generate a test vector to see how big it is
test_vector = embeddings.embed_query("test")
correct_dimension = len(test_vector)
print(f"✅ Model produces vectors of size: {correct_dimension}")

# 4. Delete Old Index
if INDEX_NAME in pc.list_indexes().names():
    print(f"🗑️  Deleting old index '{INDEX_NAME}' (Size mismatch)...")
    pc.delete_index(INDEX_NAME)
    time.sleep(5) # Wait for deletion
else:
    print(f"Index '{INDEX_NAME}' does not exist.")

# 5. Create New Index
print(f"🆕 Creating new index '{INDEX_NAME}' with dimension {correct_dimension}...")
pc.create_index(
    name=INDEX_NAME,
    dimension=correct_dimension, # This will be 3072
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    ) 
)
print("🚀 Success! Pinecone is reset and ready.")