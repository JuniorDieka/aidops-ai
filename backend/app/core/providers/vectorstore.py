from abc import ABC, abstractmethod
from typing import Any

from app.core.models import DocumentChunk


class VectorStoreProvider(ABC):
    @abstractmethod
    async def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        pass

    @abstractmethod
    async def delete_by_source(self, source_file: str) -> None:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass


class PineconeVectorStore(VectorStoreProvider):
    def __init__(self, api_key: str, environment: str, index_name: str) -> None:
        from pinecone import Pinecone

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    async def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        import asyncio

        vectors = [
            (
                chunk.id,
                chunk.embedding,
                {
                    "content": chunk.content,
                    "source_file": chunk.source_file,
                    "page": chunk.page,
                    "section": chunk.section,
                    "language": chunk.language,
                    "ingested_at": chunk.ingested_at.isoformat(),
                },
            )
            for chunk in chunks
            if chunk.embedding
        ]
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.index.upsert, vectors)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        import asyncio

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.index.query(
                vector=query_embedding, top_k=top_k, filter=filter_metadata, include_metadata=True
            ),
        )

        chunks_with_scores = []
        for match in results.matches:
            chunk = DocumentChunk(
                id=match.id,
                content=match.metadata["content"],
                source_file=match.metadata["source_file"],
                page=match.metadata.get("page"),
                section=match.metadata.get("section"),
                language=match.metadata.get("language", "en"),
            )
            chunks_with_scores.append((chunk, match.score))

        return chunks_with_scores

    async def delete_by_source(self, source_file: str) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self.index.delete, {"filter": {"source_file": source_file}}
        )

    async def count(self) -> int:
        import asyncio

        loop = asyncio.get_event_loop()
        stats = await loop.run_in_executor(None, self.index.describe_index_stats)
        return stats.total_vector_count


class FAISSVectorStore(VectorStoreProvider):
    def __init__(self, dimension: int, index_path: str = "./faiss_index") -> None:
        import faiss
        import os
        import pickle

        self.dimension = dimension
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.metadata_file = os.path.join(index_path, "metadata.pkl")

        os.makedirs(index_path, exist_ok=True)

        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, "rb") as f:
                self.metadata_store = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata_store: dict[int, DocumentChunk] = {}

    def _save(self) -> None:
        import faiss
        import pickle

        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata_store, f)

    async def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        import asyncio
        import numpy as np

        loop = asyncio.get_event_loop()

        embeddings = np.array([chunk.embedding for chunk in chunks if chunk.embedding]).astype(
            "float32"
        )

        if len(embeddings) == 0:
            return

        current_count = self.index.ntotal
        await loop.run_in_executor(None, self.index.add, embeddings)

        for i, chunk in enumerate(chunks):
            if chunk.embedding:
                self.metadata_store[current_count + i] = chunk

        await loop.run_in_executor(None, self._save)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        import asyncio
        import numpy as np

        loop = asyncio.get_event_loop()
        query_vector = np.array([query_embedding]).astype("float32")

        distances, indices = await loop.run_in_executor(None, self.index.search, query_vector, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            if idx in self.metadata_store:
                chunk = self.metadata_store[idx]
                if filter_metadata:
                    if all(
                        chunk.metadata.get(k) == v or getattr(chunk, k, None) == v
                        for k, v in filter_metadata.items()
                    ):
                        score = 1.0 / (1.0 + distance)
                        results.append((chunk, score))
                else:
                    score = 1.0 / (1.0 + distance)
                    results.append((chunk, score))

        return results

    async def delete_by_source(self, source_file: str) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._delete_by_source_sync, source_file)

    def _delete_by_source_sync(self, source_file: str) -> None:
        import faiss
        import numpy as np

        indices_to_keep = [
            i for i, chunk in self.metadata_store.items() if chunk.source_file != source_file
        ]

        if len(indices_to_keep) == self.index.ntotal:
            return

        embeddings_to_keep = np.array(
            [self.metadata_store[i].embedding for i in indices_to_keep]
        ).astype("float32")

        self.index = faiss.IndexFlatL2(self.dimension)
        if len(embeddings_to_keep) > 0:
            self.index.add(embeddings_to_keep)

        new_metadata_store = {i: self.metadata_store[old_i] for i, old_i in enumerate(indices_to_keep)}
        self.metadata_store = new_metadata_store

        self._save()

    async def count(self) -> int:
        return self.index.ntotal
