import logging


class CommandClassMessageCollection(dict):
    def __init__(self):
        self.reverseMapping = {}

    def __call__(self, cmdClass, cmd):
        def decorator(message):
            hid = (cmdClass << 8) | (cmd & 0xFF)
            self[hid] = message
            self.reverseMapping[message] = (cmdClass, cmd)
            return message

        return decorator


ZWaveMessage = CommandClassMessageCollection()  # pylint: disable=invalid-name
cmdClasses = {}


def registerCmdClass(cmdClass, name):
    cmdClasses[cmdClass] = name


# pylint: disable=wrong-import-position
from . import NetworkManagementProxy, Zip
