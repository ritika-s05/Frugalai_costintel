from typing import Literal

from pydantic import BaseModel
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = 0.7
    max_tokens: int | None = None

from pydantic import BaseModel


class Choice(BaseModel):
    index: int
    finish_reason: str
    message: Message


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    model: str
    choices: list[Choice]
    usage: Usage