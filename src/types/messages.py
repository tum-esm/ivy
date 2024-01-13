from typing import Any, Literal
import pydantic
from .config import ForeignConfig


class DataMessageBody(pydantic.BaseModel):
    variant: Literal["data"] = "data"
    data: dict[str, float | int]


class LogMessageBody(pydantic.BaseModel):
    variant: Literal["log"] = "log"
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]
    subject: str
    body: str


class ConfigMessageBody(pydantic.BaseModel):
    variant: Literal["config"] = "config"
    status: Literal["received", "accepted", "rejected", "startup"]
    config: ForeignConfig


class MessageArchiveItem(pydantic.BaseModel):
    timestamp: float
    message_body: DataMessageBody | LogMessageBody | ConfigMessageBody


class MessageQueueItem(MessageArchiveItem):
    identifier: int = pydantic.Field(
        ..., description="The identifier of the message"
    )
