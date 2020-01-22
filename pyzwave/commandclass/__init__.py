import logging


class CommandClassMessageCollection(dict):
    """
    Decorator for registering a CommandClass to the system
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


ZWaveMessage = CommandClassMessageCollection()  # pylint: disable=invalid-name
cmdClasses = {}  # pylint: disable=invalid-name


def registerCmdClass(cmdClass, name):
    """
    Function for registering the name of a command class to
    make output prettier
    """
    cmdClasses[cmdClass] = name


# pylint: disable=wrong-import-position
from . import Basic, NetworkManagementProxy, SwitchBinary, Zip, ZipND
