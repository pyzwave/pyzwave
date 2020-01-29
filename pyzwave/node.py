# -*- coding: utf-8 -*-
import logging

from pyzwave.adapter import Adapter
from pyzwave.message import Message
from pyzwave.util import MessageWaiter

_LOGGER = logging.getLogger(__name__)


class Node(MessageWaiter):
    """
    Base class for a Z-Wave node
    """

    def __init__(self, nodeId: int, adapter: Adapter, cmdClasses: list):
        super().__init__()
        self._adapter = adapter
        self._basicDeviceClass = 0
        self._flirs = False
        self._genericDeviceClass = 0
        self._isFailed = False
        self._listening = False
        self._nodeId = nodeId
        self._specificDeviceClass = 0

    @property
    def adapter(self) -> Adapter:
        """The adapter"""
        return self._adapter

    @property
    def basicDeviceClass(self) -> int:
        """Return this nodes basic device class"""
        return self._basicDeviceClass

    @basicDeviceClass.setter
    def basicDeviceClass(self, basicDeviceClass: int):
        self._basicDeviceClass = basicDeviceClass

    @property
    def flirs(self) -> bool:
        """Returns if this node is a FLiRS node or not"""
        return self._flirs

    @flirs.setter
    def flirs(self, flirs: bool):
        self._flirs = flirs

    @property
    def genericDeviceClass(self) -> int:
        """Returns this nodes generic device class"""
        return self._genericDeviceClass

    @genericDeviceClass.setter
    def genericDeviceClass(self, genericDeviceClass: int):
        self._genericDeviceClass = genericDeviceClass

    @property
    def isFailed(self) -> bool:
        """Returns is this node is considered failing or not"""
        return self._isFailed

    @isFailed.setter
    def isFailed(self, isFailed: bool):
        self._isFailed = isFailed

    @property
    def listening(self) -> bool:
        """Returns True if this node is listening. False if it is a sleeping node"""
        return self._listening

    @listening.setter
    def listening(self, listening: bool):
        self._listening = listening

    @property
    def nodeId(self) -> int:
        """The node id"""
        return self._nodeId

    async def send(
        self, cmd: Message, sourceEP: int = 0, destEP: int = 0, timeout: int = 3
    ) -> bool:
        """Send a message to this node"""
        return await self._adapter.sendToNode(
            self._nodeId, cmd, sourceEP=sourceEP, destEP=destEP, timeout=timeout
        )

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        """Send a message and wait for the response"""
        self.addWaitingSession(waitFor)
        await self.send(cmd, **kwargs)
        return await self.waitForMessage(waitFor, timeout=timeout)

    @property
    def specificDeviceClass(self) -> int:
        """Returns this nodes specific device class"""
        return self._specificDeviceClass

    @specificDeviceClass.setter
    def specificDeviceClass(self, specificDeviceClass: int):
        self._specificDeviceClass = specificDeviceClass
