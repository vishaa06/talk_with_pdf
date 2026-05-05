import os
#import google.generativeai as genai
#from llama_index.readers.file import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

# load once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

"""load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")  

genai.configure(api_key=api_key)

EMBED_MODEL = "models/embedding-001"
EMBED_DIM=768"""

splitter = SentenceSplitter(
    chunk_size=200,
    chunk_overlap=50,
)

def load_and_chunk_pdf(path:str):
    if not os.path.exists(path):
        print(f"❌ Error: File not found at {path}")
        return []
    docs = SimpleDirectoryReader(input_files=[path]).load_data()
    texts =[d.text for d in docs if getattr(d,"text",None)]
    chunks=[]
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

"""def embed_texts(texts:list[str]) -> list[list[float]]:
    embeddings = []
    
    for text in texts:
        try:
            response = genai.embed_content(
                model=EMBED_MODEL,
                content=text
            )
            embeddings.append(response["embedding"])

        except Exception as e:
            print(f"Error embedding text: {e}")
            embeddings.append([0.0] * EMBED_DIM)  
    
    return embeddings"""

def embed_texts(texts: list[str]) -> list[list[float]]:
    #embeddings = []
    if not texts:
        return []

    #for text in texts:
    embeddings = embedding_model.encode(texts)

     # ✅ Debug (ADD HERE)
    for i, text in enumerate(texts[:3]):
        print("\n--- Sample Chunk ---")
        print(text[:100])
        print("Embedding sum:", sum(embeddings[i]))

    return [emb.tolist() for emb in embeddings]