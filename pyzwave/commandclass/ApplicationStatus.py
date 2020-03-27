from enum import IntEnum

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_APPLICATION_STATUS,
    APPLICATION_BUSY,
)
from pyzwave.message import Message
from pyzwave.types import enum_t, uint8_t
from . import registerCmdClass, ZWaveMessage


registerCmdClass(COMMAND_CLASS_APPLICATION_STATUS, "APPLICATION_STATUS")


class Status(IntEnum):
    """Status enum describing the application busy reason"""

    TRY_AGAIN_LATER = 0
    TRY_AGAIN_IN_WAIT_TIME_SECONDS = 1
    REQUEST_QUEUED_EXECUTED_LATER = 2


@ZWaveMessage(COMMAND_CLASS_APPLICATION_STATUS, APPLICATION_BUSY)
class ApplicationBusy(Message):
    """Command Class message COMMAND_CLASS_APPLICATION_STATUS APPLICATION_BUSY"""

    NAME = "APPLICATION_BUSY"

    attributes = (("status", enum_t(Status, uint8_t)), ("waitTime", uint8_t))
