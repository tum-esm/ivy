from typing import Literal
import pydantic
from .config import ForeignConfig


class DataMessageBody(pydantic.BaseModel):
    """The body of a data message, defined by `body.variant == "data"`."""

    variant: Literal["data"] = pydantic.Field(
        "data",
        description="Indicating the variant of the message. All possible message bodies have this field.",
    )
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
    """The body of a log message, defined by `body.variant == "log"`."""

    variant: Literal["log"] = pydantic.Field(
        "log",
        description="Indicating the variant of the message. All possible message bodies have this field.",
    )
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]
    subject: str = pydantic.Field(
        ...,
        description="The subject of the log message. Try to move specific details"
        + "to the body because then messages can be grouped by the subject - i.e. "
        + '"give me all messages reporting high system load".',
        examples=["Starting procedure", "System load too high"],
    )
    body: str = pydantic.Field(
        ...,
        description="The body of the log message",
        examples=["Here are some more details on the procedure starting", "The system load is 87%"],
    )


class ConfigMessageBody(pydantic.BaseModel):
    """The body of a config message, defined by `body.variant == "config"`."""

    variant: Literal["config"] = pydantic.Field(
        "config",
        description="Indicating the variant of the message. All possible message bodies have this field.",
    )
    status: Literal["received", "accepted", "rejected", "startup"] = pydantic.Field(
        ...,
        description='The status of the config. "received" is sent out by the backend '
        + 'process upon arrival. "accepted" means the config passed the tests and will '
        + 'be used after the termination that is issues upon acceptance. "rejected" '
        + "means the config did either not fulfil the schema or not pass the tests. "
        + '"startup" means that a mainloop using this config was started.',
    )
    config: ForeignConfig


class MessageArchiveItem(pydantic.BaseModel):
    timestamp: float = pydantic.Field(
        ...,
        description="Unix timestamp on the system when this message was created",
    )
    message_body: DataMessageBody | LogMessageBody | ConfigMessageBody

    def __hash__(self) -> int:
        return hash(self.timestamp)


class MessageQueueItem(MessageArchiveItem):
    identifier: int = pydantic.Field(..., description="The identifier of the message")

    def __hash__(self) -> int:
        return self.identifier
