"""This module contains all type definitions of the codebase and
may implement loading and dumping functionality like `Config.load`."""

from .config import Config, ForeignConfig
from .messages import (
    DataMessageBody,
    LogMessageBody,
    ConfigMessageBody,
    MessageQueueItem,
    MessageArchiveItem,
)
from .state import State
