from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os

class RAGService:
    def __init__(self):
        # Load embedding model (lightweight)
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384
            self.index = faiss.IndexFlatL2(self.dimension)
            self.stored_leads = [] # Keep metadata in memory for sync (for MVP)
        except Exception as e:
            print(f"RAG Init Error (Model download might fail first time?): {e}")
            self.model = None

    def index_leads(self, df):
        if not self.model:
            return
            
        # Create text representation for embedding
        # e.g., "Source: Google, Time: 120s, Pages: 5"
        texts = []
        metadata = []
        
        for _, row in df.iterrows():
            text = f"Source: {row.get('Source', 'Unknown')}, TimeOnSite: {row.get('TimeOnSite', 0)}, PagesVisited: {row.get('PagesVisited', 0)}, MeetingBooked: {row.get('MeetingBooked', 0)}"
            texts.append(text)
            metadata.append(row.to_dict())
            
        embeddings = self.model.encode(texts)
        
        # Add to FAISS
        self.index.add(np.array(embeddings).astype('float32'))
        self.stored_leads.extend(metadata)
        print(f"Indexed {len(texts)} leads for RAG.")

    def search_similar(self, lead_data, k=3):
        if not self.model or self.index.ntotal == 0:
            return []
            
        # Embed query
        query_text = f"Source: {lead_data.get('Source', 'Unknown')}, TimeOnSite: {lead_data.get('TimeOnSite', 0)}, PagesVisited: {lead_data.get('PagesVisited', 0)}, MeetingBooked: {lead_data.get('MeetingBooked', 0)}"
        query_embedding = self.model.encode([query_text])
        
        # Search
        D, I = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        results = []
        indices = I[0]
        distances = D[0]
        
        for idx, dist in zip(indices, distances):
            if idx < len(self.stored_leads) and idx >= 0:
                item = self.stored_leads[idx]
                # Add similarity score (lower distance = better)
                item['similarity_score'] = float(dist)
                results.append(item)
                
        return results

# Global instance
rag_service = RAGService()
