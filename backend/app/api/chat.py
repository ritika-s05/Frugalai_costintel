import uuid

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAIError
from sqlalchemy.orm import Session

from app.core.exceptions import TokenBudgetExceededError
from app.database.dependencied import get_db
from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    Message,
    Usage,
)
from app.services.gateway import GatewayService


router = APIRouter(
    prefix="/v1",
    tags=["AI Gateway"],
)


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
)
def create_chat_completion(
    request: ChatCompletionRequest,
    db: Session = Depends(get_db),
) -> ChatCompletionResponse:
    try:
        gateway_result = GatewayService().complete(
            request=request,
            db=db,
        )

    except TokenBudgetExceededError as exc:
        raise HTTPException(
            status_code=429,
            detail=f"Request blocked by TokenGuard: {exc}",
        ) from exc

    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail="The upstream model provider request failed.",
        ) from exc

    result = gateway_result.provider_result

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        object="chat.completion",
        model=result.model,
        choices=[
            Choice(
                index=0,
                finish_reason=result.finish_reason,
                message=Message(
                    role="assistant",
                    content=result.content,
                ),
            )
        ],
        usage=Usage(
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
        ),
    )