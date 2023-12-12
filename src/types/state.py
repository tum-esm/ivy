from typing import Optional
import datetime
import pydantic


class SystemState(pydantic.BaseModel):
    """State values determined in the system checks procedure."""

    last_boot_time: Optional[datetime.datetime] = pydantic.Field(
        default=None,
        description="The last boot time of the system",
        examples=["2021-01-01T00:00:00.000000"],
    )
    last_5_min_load: Optional[float] = pydantic.Field(
        default=None,
        description="The average CPU load in the last 5 minutes in percent",
        examples=[1, 15.5, 85, 99.5],
    )


class State(pydantic.BaseModel):
    """Central state used to communicate between prodedures and with the mainloop."""

    system: SystemState = pydantic.Field(
        default=SystemState(),
        description="The state of the system",
    )
