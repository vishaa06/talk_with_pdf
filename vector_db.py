from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class QdrantStorage:
    def __init__(self,url="http://localhost:6333",collection="docs",dim=384):
        self.client=QdrantClient(url=url,timeout=30)
        self.collection=collection
        self.dim=dim
        try:
            self.client.delete_collection(self.collection)
        except:
            pass

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim,distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        if len(vectors) > 0 and len(vectors[0]) != self.dim:
            raise ValueError(f"❌ Vector dimension mismatch. Expected {self.dim}")
        points=[PointStruct(id=ids[i],vector=vectors[i],payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(collection_name=self.collection,points=points)

    def search(self,query_vector,top_k:int=5):
        response=self.client.query_points(
            collection_name=self.collection,    
            query=query_vector,
            with_payload=True,
            limit=top_k
        )
        """contexts=[]
        sources=set()

        for point in results:
            payload = point.payload or {}
            text = payload.get("text","")
            source = payload.get("source","")

            if text:
                contexts.append(text)
                sources.add(source)
        
        return {"contexts":contexts,"sources":list(sources)}"""
        
        results = []
        for point in response.points:
        # Extract payload safely
            payload = point.payload or {}
            results.append({
                "content": payload.get("text", ""),
                "source": payload.get("source", "unknown"),
                "score": point.score
            })
        return results

