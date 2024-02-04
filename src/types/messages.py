from typing import Literal
import pydantic
from .config import ForeignConfig


class DataMessageBody(pydantic.BaseModel):
    variant: Literal["data"] = "data"
    data: dict[str, float | int | str] = pydantic.Field(
        ...,
        description="The data to send to the backend",
        examples=[{"temperature": 19.7}, {"temperature": 19.7, "humidity": 45.3}],
    )

    @pydantic.field_validator("data", mode="after")
    def _check_for_forbidden_keys(
        cls, v: dict[str, float | int | str]
    ) -> dict[str, float | int | str]:
        if "logging" in v.keys():
            raise ValueError("The key 'logging' is reserved")
        if "configuration" in v.keys():
            raise ValueError("The key 'configuration' is reserved")
        return v


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
    identifier: int = pydantic.Field(..., description="The identifier of the message")
