import asyncio
import logging

from pyzwave.util import Listenable

_LOGGER = logging.getLogger(__name__)


class CommandClassMessageCollection(dict):
    """
    Decorator for registering a CommandClass message to the system
    """

    def __init__(self):
        super().__init__()
        self.reverseMapping = {}

    def __call__(self, cmdClass, cmd):
        def decorator(message):
            hid = (cmdClass << 8) | (cmd & 0xFF)
            self[hid] = message
            self.reverseMapping[message] = (cmdClass, cmd)
            return message

        return decorator


class CommandClassCollection(dict):
    """
    Decorator for registering a CommandClass to the system
    """

    def __init__(self):
        super().__init__()
        self.reverseMapping = {}

    def __call__(self, cmdClass):
        def decorator(cls):
            self[cmdClass] = cls
            registerCmdClass(cmdClass, cls.NAME)
            self.reverseMapping[cls] = cmdClass
            return cls

        return decorator


ZWaveMessage = CommandClassMessageCollection()  # pylint: disable=invalid-name
ZWaveCommandClass = CommandClassCollection()  # pylint: disable=invalid-name
cmdClasses = {}  # pylint: disable=invalid-name


def registerCmdClass(cmdClass, name):
    """
    Function for registering the name of a command class to
    make output prettier
    """
    cmdClasses[cmdClass] = name


# pylint: disable=wrong-import-position,import-self
from . import (
    Basic,
    ManufacturerSpecific,
    NetworkManagementProxy,
    SwitchBinary,
    Version,
    Zip,
    ZipGateway,
    ZipND,
    ZwavePlusInfo,
)
from .CommandClass import CommandClass
