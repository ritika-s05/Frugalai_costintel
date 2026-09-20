import json

from sqlalchemy.orm import Session

from app.models.llm_req import LLMRequest
from app.providers.base import ProviderResult
from app.schemas.chat import ChatCompletionRequest


def save_llm_request(
    db: Session,
    request: ChatCompletionRequest,
    result: ProviderResult,
    estimated_cost: float,
    actual_cost: float,
) -> LLMRequest:
    record = LLMRequest(
        provider=result.provider,
        model_name=result.model,
        prompt=json.dumps(
            [message.model_dump() for message in request.messages]
        ),
        response=result.content,
        input_tokens=result.prompt_tokens,
        output_tokens=result.completion_tokens,
        total_tokens=result.total_tokens,
        estimated_cost=estimated_cost,
        actual_cost=actual_cost,
        latency_ms=result.latency_ms,
        cache_hit=False,
        routed=False,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise