from typing import Any, Literal
import pydantic
from .config import Config, ForeignConfig


class DataMessageBody(pydantic.BaseModel):
    variant: Literal["data"] = "data"
    message_body: dict[str, Any]


class LogMessageBody(pydantic.BaseModel):
    variant: Literal["log"] = "log"
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]
    subject: str
    body: str


class ConfigMessageBody(pydantic.BaseModel):
    variant: Literal["config"] = "config"
    status: Literal["received", "accepted", "rejected", "startup"]
    config: Config | ForeignConfig


class MessageQueueItem(pydantic.BaseModel):
    identifier: int = pydantic.Field(
        ..., description="The identifier of the message"
    )
    timestamp: float
    message_body: DataMessageBody | LogMessageBody | ConfigMessageBody
