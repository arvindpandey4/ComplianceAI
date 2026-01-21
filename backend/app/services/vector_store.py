import os
import pickle
from typing import List, Tuple
from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import SentenceTransformerEmbeddings # Removed
from langchain_community.embeddings import FastEmbedEmbeddings # Added
from langchain_core.documents import Document
# from sentence_transformers import CrossEncoder # Removed to save memory

class VectorStoreService:
    _instance = None

    def __new__(cls, index_path: str = "data/faiss_index"):
        if cls._instance is None:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, index_path: str = "data/faiss_index"):
        if getattr(self, "initialized", False):
            return
            
        self.index_path = index_path
        
        # Switched to FastEmbed (ONNX) - <200MB RAM
        # Using the same model architecture to maintain index compatibility if possible,
        # but for fresh deploy, FastEmbed's default is optimal.
        # We specify the model that matches 'all-MiniLM-L6-v2' best or default.
        # FastEmbed default is BAAI/bge-small-en-v1.5 which is better than MiniLM.
        # However, if we want to reuse existing index, we need compatible dims (384).
        # BAAI/bge-small-en-v1.5 has 384 dims.
        # threads=1 is CRITICAL for 512MB RAM instances to prevent OOM
        self.embeddings = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            threads=1,
            cache_dir="data/fastembed_cache"
        )
        
        # Reranking Disabled for Free Tier (Save RAM)
        # self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.reranker = None
        
        self.vector_db = None
        self._load_index()
        self.initialized = True

    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                self.vector_db = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("Loaded existing FAISS index.")
            except Exception as e:
                print(f"Failed to load index: {e}. Creating new one.")
                self.vector_db = None
        else:
            print("No existing index found. Starting fresh.")
        
        # Explicit garbage collection to free up memory after initialization
        import gc
        gc.collect()

    def add_documents(self, documents: List[Document]):
        if not documents:
            return

        if self.vector_db is None:
            self.vector_db = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_db.add_documents(documents)
        
        self.save_index()

    def search(self, query: str, k: int = 4) -> List[Document]:
        if self.vector_db is None:
            return []
        
        # 1. Standard Vector Search (Fast, low RAM)
        # We removed reranking to fit in 512MB RAM
        candidates_with_scores = self.vector_db.similarity_search_with_score(query, k=k)
        
        # Return docs directly
        return [doc for doc, score in candidates_with_scores]

    def save_index(self):
        if self.vector_db:
            self.vector_db.save_local(self.index_path)
