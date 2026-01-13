import os
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    async def process_file(self, file_path: str, metadata: Dict) -> List[Document]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            for doc in docs:
                doc.metadata.update(metadata)
            
            chunks = self.text_splitter.split_documents(docs)
            
            enriched_chunks = []
            for chunk in chunks:
                enriched_chunk = self._enrich_chunk_context(chunk, metadata)
                enriched_chunks.append(enriched_chunk)
                
            return enriched_chunks
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            raise e

    def _enrich_chunk_context(self, chunk: Document, metadata: Dict) -> Document:
        source = metadata.get("source", "Unknown Document")
        doc_type = metadata.get("type", "General")
        
        context_header = f"DOMARIN: REGULATORY_COMPLIANCE\nSOURCE_DOC: {source}\nDOC_TYPE: {doc_type}\nCONTEXT_LAYER: Global\n---\n"
        chunk.page_content = f"{context_header}{chunk.page_content}"
        
        return chunk
