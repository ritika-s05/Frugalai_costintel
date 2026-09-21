import hashlib
import json
from dataclasses import dataclass
from threading import Lock

import numpy as np
from sentence_transformers import SentenceTransformer

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
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
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

        # Fast path: deterministic exact match.
        with self._lock:
            exact_entry = self._cache.get(cache_key)

        if exact_entry is not None:
            return CacheLookupResult(
                hit=True,
                entry=exact_entry,
                similarity=1.0,
                match_type="exact",
            )

        semantic_text = self._build_semantic_text(request)
        query_embedding = self._embed(semantic_text)

        best_entry = None
        best_similarity = -1.0

        with self._lock:
            entries = list(self._cache.values())

        for entry in entries:
            # Do not reuse responses generated for another model.
            if entry.model != model:
                continue

            similarity = self._cosine_similarity(
                query_embedding,
                entry.embedding,
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_entry = entry

        if (
            best_entry is not None
            and best_similarity >= self.similarity_threshold
        ):
            return CacheLookupResult(
                hit=True,
                entry=best_entry,
                similarity=best_similarity,
                match_type="semantic",
            )

        return CacheLookupResult(
            hit=False,
            entry=None,
            similarity=(
                best_similarity
                if best_entry is not None
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

        entry = CacheEntry(
            cache_key=cache_key,
            model=model,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            finish_reason=finish_reason,
            semantic_text=semantic_text,
            embedding=embedding,
        )

        with self._lock:
            self._cache[cache_key] = entry

        return entry

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def _embed(
        self,
        text: str,
    ) -> np.ndarray:
        embedding = self._embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding

    @staticmethod
    def _cosine_similarity(
        first: np.ndarray,
        second: np.ndarray,
    ) -> float:
        return float(
            np.dot(first, second)
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