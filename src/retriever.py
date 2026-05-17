from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .data_loader import load_knowledge_documents
from .schemas import KnowledgeHit


def _chunk_document(source: str, text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and current:
            chunks.append((source, "\n".join(current).strip()))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append((source, "\n".join(current).strip()))
    return [(src, body) for src, body in chunks if body]


class FaultRetriever:
    def __init__(self) -> None:
        docs = load_knowledge_documents()
        self.chunks = [chunk for source, text in docs for chunk in _chunk_document(source, text)]
        if not self.chunks:
            self.sources: list[str] = []
            self.texts: list[str] = []
            self.vectorizer = TfidfVectorizer()
            self.matrix = None
            return
        self.sources = [source for source, _ in self.chunks]
        self.texts = [text for _, text in self.chunks]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=3000)
        self.matrix = self.vectorizer.fit_transform(self.texts)

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeHit]:
        if self.matrix is None:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        order = scores.argsort()[::-1][:top_k]
        hits: list[KnowledgeHit] = []
        for idx in order:
            if scores[idx] <= 0:
                continue
            hits.append(
                KnowledgeHit(
                    source=self.sources[idx],
                    score=round(float(scores[idx]), 3),
                    snippet=self.texts[idx][:700],
                )
            )
        return hits
