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


def interviewDecorator(interview):
    """Decorator to make sure the command class is ready for interview"""

    async def wrapper():
        version = interview.__self__.version
        if version == 0:
            # We cannot interview until we know the version
            version = await interview.__self__.requestVersion()
        if version == 0:
            _LOGGER.warning(
                "Unable to determine command class version for %s",
                interview.__self__.NAME,
            )
            return
        return await interview()

    return wrapper


class CommandClass(AttributesMixin, Listenable):
    """Base class for a command class"""

    NAME = "UNKNOWN"

    def __init__(self, securityS0, node):
        super().__init__()
        self._node = node
        self._securityS0 = securityS0
        self._version = 0

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """Return the command class id"""
        return ZWaveCommandClass.reverseMapping.get(self.__class__, 0)

    async def interview(self):
        """
        Interview this command class. Must be implemented by subclasses.
        The version has already been interviewed when this method is called
        """

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
        values["version"] = self.version
        return values

    def __setstate__(self, state):
        self._version = int(state.get("version", 0))
        super().__setstate__(state)

    @staticmethod
    def load(cmdClass: int, securityS0: bool, node):
        """Load and create a new command class instance from the given command class id"""
        # pylint: disable=invalid-name
        CommandClassCls = ZWaveCommandClass.get(cmdClass, CommandClass)
        instance = CommandClassCls(securityS0, node)
        # Decorate the interview function
        instance.interview = interviewDecorator(instance.interview)
        return instance


# pylint: disable=wrong-import-position
from . import Version
