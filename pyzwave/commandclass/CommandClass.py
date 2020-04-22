import asyncio
import logging
from typing import Dict, Any

from pyzwave.util import AttributesMixin, Listenable
from pyzwave.commandclass import ZWaveCommandClass
from pyzwave.message import Message

_LOGGER = logging.getLogger(__name__)


class Attribute:
    """An attribute"""


class DictAttribute(Attribute, AttributesMixin):
    """A dict attribute"""


def VarDictAttribute(KeyType, ValueType):  # pylint: disable=invalid-name
    """
    Helper class to store variable attributes as a dictionary.
    All values must be of the same type
    """

    class VarDictAttributeType(dict):
        """Variable dictionary attribute type"""

        def debugString(self, indent=0):
            """
            Convert all attributes in this object to a human readable string used for debug output.
            """
            attrs = []
            for name, value in self.items():
                if hasattr(value, "debugString"):
                    debugString = value.debugString(indent + 1)
                else:
                    debugString = repr(value)
                attrs.append(
                    "{}{} = {}".format("\t" * (indent + 1), repr(name), debugString)
                )
            return "{}:\n{}".format(self.__class__.__name__, "\n".join(attrs))

        def __getstate__(self):
            return {i: value.__getstate__() for i, value in self.items()}

        def __setitem__(self, name, value):
            if isinstance(value, ValueType):
                return super().__setitem__(name, value)
            if hasattr(ValueType, "__setstate__"):
                valueContainer = ValueType()  # pylint: disable=invalid-name
                valueContainer.__setstate__(value)
            else:
                valueContainer = ValueType(value)
            return super().__setitem__(name, valueContainer)

        def __setstate__(self, state):
            for key, value in state.items():
                self[KeyType(key)] = value

    return VarDictAttributeType


def interviewDecorator(interview):
    """Decorator to make sure the command class is ready for interview"""

    async def wrapper():
        commandClass = interview.__self__
        version = commandClass.version
        if version == 0:
            # We cannot interview until we know the version
            version = await commandClass.requestVersion()
        if version == 0:
            _LOGGER.warning(
                "Unable to determine command class version for %s", commandClass.name,
            )
            return
        try:
            commandClass._interviewed = False  # pylint: disable=protected-access
            retval = await interview()
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout interviewing command class %s", commandClass.name)
            return False
        if retval is not False:
            commandClass._interviewed = True  # pylint: disable=protected-access
        commandClass.speak("commandClassUpdated")
        return retval

    return wrapper


class CommandClass(AttributesMixin, Listenable):
    """Base class for a command class"""

    NAME = "UNKNOWN"

    def __init__(self, securityS0, node):
        super().__init__()
        self._node = node
        self._securityS0 = securityS0
        self._interviewed = False
        self._version = 0

    async def handleMessage(self, message: Message, flags) -> bool:
        """Handle and incomming message specific to this command class"""
        # Find internal handlers
        if not message.NAME:
            # Not implemented, do not look for handlers
            return False

        hid = message.hid()
        if self.__messageHandlers__:
            handler = self.__messageHandlers__.get(hid)
            if handler and await handler(self, message, flags):
                # Message was handled, stop further processing
                return True

        components = message.NAME.lower().split("_")
        name = "".join(["on", *map(str.title, components)])
        for retval in await self.ask(name, message, flags):
            if retval:
                return True

        # No message handlers for this kind of message
        return False

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """Return the command class id"""
        return ZWaveCommandClass.reverseMapping.get(self.__class__, 0)

    async def interview(self) -> bool:
        """
        Interview this command class. Must be implemented by subclasses.
        The version has already been interviewed when this method is called.

        Return True if the interview was completed successfully and False or raise
        an exception if the interview did not complete.
        """

    @property
    def interviewed(self) -> bool:
        """Return is this command class has been fully interviewed or not"""
        return self._interviewed

    @property
    def name(self):
        """Return the name of the command class"""
        return self.NAME

    @property
    def node(self):
        """Returns the node this command class belongs to"""
        return self._node

    async def requestVersion(self) -> int:
        """Request the version of this command class"""
        if self.id == 0:
            # Not implemented command class
            return 0
        try:
            answer = await self._node.sendAndReceive(
                Version.VersionCommandClassGet(requestedCommandClass=self.id),
                Version.VersionCommandClassReport,
            )
            self._version = int(answer.commandClassVersion)
        except asyncio.TimeoutError:
            return 0
        self.speak("commandClassUpdated")
        return self._version

    @property
    def securityS0(self) -> bool:
        """Returns if security class S0 is required to access this command class"""
        return self._securityS0

    async def send(self, cmd: Message, timeout: int = 3) -> bool:
        """Send a message to the node. This is a convenience
        wrapper around Node.send."""
        return await self._node.send(cmd, timeout=timeout)

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        """
        Send a message and wait for the response. This is a convenience
        wrapper around Node.sendAndReceive
        """
        return await self._node.sendAndReceive(cmd, waitFor, timeout, **kwargs)

    @property
    def version(self) -> int:
        """Returns the command class version implemented by the node"""
        return self._version

    def __getstate__(self) -> Dict[str, Any]:
        values = super().__getstate__()
        values["interviewed"] = self.interviewed
        values["version"] = self.version
        return values

    def __setstate__(self, state):
        self._version = int(state.get("version", 0))
        self._interviewed = bool(state.get("interviewed", False))
        super().__setstate__(state)

    @staticmethod
    def load(cmdClass: int, securityS0: bool, node):
        """Load and create a new command class instance from the given command class id"""
        # pylint: disable=invalid-name
        CommandClassCls = ZWaveCommandClass.get(cmdClass, None)
        if CommandClassCls:
            instance = CommandClassCls(securityS0, node)
        else:
            instance = UnknownCommandClass(securityS0, node, cmdClass)
        # Decorate the interview function
        instance.interview = interviewDecorator(instance.interview)
        return instance


class UnknownCommandClass(CommandClass):
    """
    Wrapper class for wrapping unknown command classes.
    """

    def __init__(self, securityS0, node, id):
        super().__init__(securityS0, node)
        self._id = id

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        return self._id

    @property
    def name(self):
        return "UNKNOWN (0x{:X})".format(self.id)


# pylint: disable=wrong-import-position
from . import Version
