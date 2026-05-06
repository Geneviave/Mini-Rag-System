from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class QdrantDBClient:

    def __init__(self, db_path: str, distance_metric: str, embedding_dim: int):
        self.client = QdrantClient(path=db_path)
        self.distance = Distance.COSINE if distance_metric == "cosine" else Distance.DOT
        self.embedding_dim = embedding_dim

    def create_collection(self, collection_name: str):
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]

        if collection_name not in names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=self.distance
                )
            )

    def insert_vectors(self, collection_name: str, vectors, payloads, ids):
        from qdrant_client.models import PointStruct
        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
            for i in range(len(vectors))
        ]
        self.client.upsert(collection_name=collection_name, points=points)

    def search(self, collection_name: str, query_vector, top_k: int = 5):
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return results