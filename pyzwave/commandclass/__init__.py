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


class ZWaveMessageHandler:
    """Decorator for functions handeling command class messages"""

    def __init__(self, message):
        self.hid = message.hid()
        self.func = None

    def __call__(self, func):
        self.func = func
        return self

    def __set_name__(self, owner, name):
        if not hasattr(owner, "__messageHandlers__"):
            owner.__messageHandlers__ = {}
        owner.__messageHandlers__[self.hid] = self.func


def registerCmdClass(cmdClass, name):
    """
    Function for registering the name of a command class to
    make output prettier
    """
    cmdClasses[cmdClass] = name


# pylint: disable=wrong-import-position,import-self
from . import (
    ApplicationStatus,
    Association,
    AssociationGrpInfo,
    Basic,
    Battery,
    Configuration,
    Indicator,
    Mailbox,
    ManufacturerSpecific,
    Meter,
    MultiChannelAssociation,
    NetworkManagementInclusion,
    NetworkManagementProxy,
    NodeProvisioning,
    SensorMultilevel,
    Supervision,
    SwitchBinary,
    Version,
    Zip,
    ZipGateway,
    ZipND,
    ZwavePlusInfo,
)
from .CommandClass import CommandClass, VarDictAttribute
