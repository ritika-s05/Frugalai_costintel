import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.cache_entry import SemanticCacheEntry
from app.schemas.chat import ChatCompletionRequest


@dataclass
class CacheEntry:
    cache_key: str
    model: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str
    semantic_text: str
    embedding: np.ndarray


@dataclass
class CacheLookupResult:
    hit: bool
    entry: CacheEntry | None = None
    similarity: float | None = None
    match_type: str | None = None


class SemanticCache:
    def __init__(
        self,
        similarity_threshold: float = 0.90,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.similarity_threshold = similarity_threshold
        self._embedding_model = SentenceTransformer(
            embedding_model
        )

    def lookup(
        self,
        request: ChatCompletionRequest,
        model: str,
    ) -> CacheLookupResult:
        cache_key = self._build_cache_key(
            request=request,
            model=model,
        )

        with SessionLocal() as db:
            exact_row = db.scalar(
                select(SemanticCacheEntry).where(
                    SemanticCacheEntry.cache_key == cache_key
                )
            )

            if exact_row is not None:
                exact_row.hit_count += 1
                exact_row.last_hit_at = datetime.utcnow()
                db.commit()

                return CacheLookupResult(
                    hit=True,
                    entry=self._row_to_entry(exact_row),
                    similarity=1.0,
                    match_type="exact",
                )

            semantic_text = self._build_semantic_text(request)
            query_embedding = self._embed(semantic_text)

            rows = db.scalars(
                select(SemanticCacheEntry).where(
                    SemanticCacheEntry.model == model
                )
            ).all()

            best_row = None
            best_similarity = -1.0

            for row in rows:
                stored_embedding = np.array(
                    json.loads(row.embedding),
                    dtype=np.float32,
                )

                similarity = self._cosine_similarity(
                    query_embedding,
                    stored_embedding,
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_row = row

            if (
                best_row is not None
                and best_similarity >= self.similarity_threshold
            ):
                best_row.hit_count += 1
                best_row.last_hit_at = datetime.utcnow()
                db.commit()

                return CacheLookupResult(
                    hit=True,
                    entry=self._row_to_entry(best_row),
                    similarity=best_similarity,
                    match_type="semantic",
                )

            return CacheLookupResult(
                hit=False,
                entry=None,
                similarity=(
                    best_similarity
                    if best_row is not None
                    else None
                ),
                match_type=None,
            )

    def store(
        self,
        request: ChatCompletionRequest,
        model: str,
        content: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        finish_reason: str,
    ) -> CacheEntry:
        cache_key = self._build_cache_key(
            request=request,
            model=model,
        )

        semantic_text = self._build_semantic_text(request)
        embedding = self._embed(semantic_text)

        with SessionLocal() as db:
            existing = db.scalar(
                select(SemanticCacheEntry).where(
                    SemanticCacheEntry.cache_key == cache_key
                )
            )

            if existing is None:
                row = SemanticCacheEntry(
                    cache_key=cache_key,
                    model=model,
                    semantic_text=semantic_text,
                    embedding=json.dumps(embedding.tolist()),
                    content=content,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    finish_reason=finish_reason,
                    hit_count=0,
                    similarity_threshold=self.similarity_threshold,
                )

                db.add(row)
                db.commit()
                db.refresh(row)
            else:
                row = existing

            return self._row_to_entry(row)

    def clear(self) -> None:
        with SessionLocal() as db:
            rows = db.scalars(
                select(SemanticCacheEntry)
            ).all()

            for row in rows:
                db.delete(row)

            db.commit()

    def size(self) -> int:
        with SessionLocal() as db:
            return len(
                db.scalars(
                    select(SemanticCacheEntry)
                ).all()
            )

    def _embed(
        self,
        text: str,
    ) -> np.ndarray:
        return self._embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    @staticmethod
    def _cosine_similarity(
        first: np.ndarray,
        second: np.ndarray,
    ) -> float:
        return float(np.dot(first, second))

    @staticmethod
    def _row_to_entry(
        row: SemanticCacheEntry,
    ) -> CacheEntry:
        return CacheEntry(
            cache_key=row.cache_key,
            model=row.model,
            content=row.content,
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
            finish_reason=row.finish_reason,
            semantic_text=row.semantic_text,
            embedding=np.array(
                json.loads(row.embedding),
                dtype=np.float32,
            ),
        )

    @staticmethod
    def _build_semantic_text(
        request: ChatCompletionRequest,
    ) -> str:
        return "\n".join(
            f"{message.role}: {message.content.strip()}"
            for message in request.messages
        )

    @staticmethod
    def _build_cache_key(
        request: ChatCompletionRequest,
        model: str,
    ) -> str:
        payload = {
            "model": model,
            "messages": [
                message.model_dump()
                for message in request.messages
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        canonical_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()