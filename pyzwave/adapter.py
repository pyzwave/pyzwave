# -*- coding: utf-8 -*-

import abc
import asyncio
import logging

from .util import Listenable, MessageWaiter
from .message import Message

_LOGGER = logging.getLogger(__name__)


class Adapter(Listenable, MessageWaiter, metaclass=abc.ABCMeta):
    """Abstract class for implementing communication with a Z-Wave chip"""

    def __init__(self):
        super().__init__()
        self._ackQueue = {}

    def ackReceived(self, ackId: int):
        """Call this method when an ack message has been received"""
        event = self._ackQueue.pop(ackId, None)
        if not event:
            _LOGGER.warning("Received ack for command not waiting for")
            return False
        event.set()
        return True

    def commandReceived(self, cmd: Message):
        """Call this method when a command has been received"""
        if not self.messageReceived(cmd):
            self.speak("onMessageReceived", cmd)

    @abc.abstractmethod
    async def connect(self):
        """Connect the adapter. Must be implemented by subclass"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def getNodeList(self) -> set:
        """Return a list of nodes included in the network"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def send(
        self, cmd: Message, sourceEP: int = 0, destEP: int = 0, timeout: int = 3
    ) -> bool:
        """Send message to Z-Wave chip. Must be implemented in subclass"""
        raise NotImplementedError()

    async def sendToNode(self, nodeId: int, cmd: Message, **kwargs) -> bool:
        """Send message to node. Must be implemented in subclass"""
        raise NotImplementedError()

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        """Send a message and wait for the response"""
        await self.send(cmd, **kwargs)
        return await self.waitForMessage(waitFor, timeout=timeout)

    @abc.abstractmethod
    async def setNodeInfo(self, generic, specific, cmdClasses):
        """
        Set the application NIF (Node Information Frame). This method
        should not be called directly. Use the corresponding function
        in Application instead.
        """
        raise NotImplementedError()

    async def waitForAck(self, ackId: int, timeout: int = 3):
        """Async method for waiting for the adapter to receive a specific ack id"""
        if ackId in self._ackQueue:
            raise Exception("Duplicate ackid used!")
        event = asyncio.Event()
        self._ackQueue[ackId] = event
        try:
            await asyncio.wait_for(event.wait(), timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for response")
            del self._ackQueue[ackId]
            raise
