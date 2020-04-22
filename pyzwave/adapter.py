# -*- coding: utf-8 -*-

import abc
import asyncio
import enum
import logging

from pyzwave.commandclass import NetworkManagementInclusion, NetworkManagementProxy, Zip
from .util import Listenable, MessageWaiter
from .types import dsk_t
from .message import Message

_LOGGER = logging.getLogger(__name__)


class TxOptions(enum.IntFlag):
    """TX Options used for adding nodes to network"""

    NULL = 0x00
    TRANSMIT_OPTION_LOW_POWER = 0x02
    TRANSMIT_OPTION_EXPLORE = 0x20


class Ack:
    """Class for holding session informaion"""

    class Status(enum.Enum):
        """Ack status"""

        PENDING = enum.auto()
        QUEUED = enum.auto()
        RECEIVED = enum.auto()

    def __init__(self):
        self._event = asyncio.Event()
        self._status = Ack.Status.PENDING
        self._expectedDelay = 0

    def received(self):
        """Call this function when this ack has been received"""
        self._status = Ack.Status.RECEIVED
        self._event.set()

    def queued(self, expectedDelay: int):
        """Call this function when the message cannot be delivered right now"""
        if expectedDelay < 0:
            # Node should have been awake by now. Wait 2 minutes to allow
            # the node to be manually woken
            expectedDelay = 120
        # Add some "wiggle room" for the wakeup
        self._expectedDelay = expectedDelay + 60
        self._status = Ack.Status.QUEUED
        self._event.set()

    async def wait(self, timeout):
        """Wait until the node ack the message"""
        await asyncio.wait_for(self._event.wait(), timeout)
        # Message was queued for a sleeping node.
        # Wait longer!
        while self._status == Ack.Status.QUEUED:
            self._event.clear()
            await asyncio.wait_for(self._event.wait(), self._expectedDelay)


class Adapter(Listenable, MessageWaiter, metaclass=abc.ABCMeta):
    """Abstract class for implementing communication with a Z-Wave chip"""

    def __init__(self):
        super().__init__()
        self._ackQueue = {}
        self._nodeId = 0

    def ackReceived(self, zipPkt: Zip.ZipPacket):
        """Call this method when an ack message has been received"""
        ackId = zipPkt.seqNo
        if zipPkt.nackResponse and zipPkt.nackWaiting:
            # Message was queued, signal this and keep ack in queue
            ack = self._ackQueue.get(ackId, None)
            if not ack:
                return False
            ack.queued(zipPkt.headerExtension.expectedDelay)
            return True
        ack = self._ackQueue.pop(ackId, None)
        if not ack:
            _LOGGER.warning("Received ack %d for command not waiting for", ackId)
            return False
        ack.received()
        return True

    @abc.abstractmethod
    async def addNode(self, txOptions: TxOptions) -> bool:
        """Start inclusion mode in the controller"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def addNodeDSKSet(
        self, accept: bool, inputDSKLength: int, dsk: dsk_t
    ) -> bool:
        """
        This command is used to indicate the S2 bootstrapping controller if the DSK is
        accepted and report the user input when needed.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def addNodeKeysSet(
        self, grantCSA: bool, accept: bool, grantedKeys: NetworkManagementInclusion.Keys
    ) -> bool:
        """
        This command is used to inform an S2 bootstrapping controller which keys must be
        granted to the node being bootstrapped.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def addNodeStop(self) -> bool:
        """Stop inclusion mode in the controller"""
        raise NotImplementedError()

    def commandReceived(self, cmd: Message):
        """Call this method when a command has been received"""
        if isinstance(cmd, Zip.ZipPacket):
            msg = cmd.command
        else:
            msg = cmd
        if not self.messageReceived(msg):
            self.speak("onMessageReceived", cmd)

    @abc.abstractmethod
    async def connect(self):
        """Connect the adapter. Must be implemented by subclass"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def getFailedNodeList(self) -> list:
        """Return a list of failing nodes"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def getMultiChannelCapability(
        self, nodeId: int, endpoint: int
    ) -> NetworkManagementProxy.MultiChannelCapabilityReport:
        """Return the multi channel capabilities for an endpoint in a node"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def getMultiChannelEndPoints(self, nodeId: int) -> int:
        """Return the number of multi channel end points implemented by a node"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def getNodeInfo(
        self, nodeId: int
    ) -> NetworkManagementProxy.NodeInfoCachedReport:
        """Return the node info from this node. Possibly cached"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def getNodeList(self) -> set:
        """Return a list of nodes included in the network"""
        raise NotImplementedError()

    @property
    def nodeId(self) -> int:
        """Return the node id of the controller"""
        return self._nodeId

    @nodeId.setter
    def nodeId(self, nodeId: int):
        self._nodeId = nodeId

    @abc.abstractmethod
    async def removeFailedNode(
        self, nodeId: int
    ) -> NetworkManagementInclusion.FailedNodeRemoveStatus.Status:
        """Remove a non-responding node"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def removeNode(self) -> bool:
        """Start exclusion mode in the controller"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def removeNodeStop(self) -> bool:
        """Stop exclusion mode in the controller"""
        raise NotImplementedError()

    @abc.abstractmethod
    async def send(
        self, cmd: Message, sourceEP: int = 0, destEP: int = 0, timeout: int = 3
    ) -> bool:
        """
        Send message to Z-Wave chip. Must be implemented in subclass.

        .. warning::
          This command will block until the message has been ACKed by the node.

          When talking to battery operated (sleeping) nodes this command will
          block until the nodes wakes up or is considered dead. This can be a
          long time (week or even months). Please make sure the code can handle this.
        """
        raise NotImplementedError()

    async def sendToNode(self, nodeId: int, cmd: Message, **kwargs) -> bool:
        """Send message to node. Must be implemented in subclass"""
        raise NotImplementedError()

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        """Send a message and wait for the response"""
        session = self.addWaitingSession(waitFor)
        await self.send(cmd, **kwargs)
        return await self.waitForMessage(waitFor, session=session, timeout=timeout)

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
        ack = Ack()
        self._ackQueue[ackId] = ack
        try:
            await ack.wait(timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for response for ack %s", ackId)
            del self._ackQueue[ackId]
            raise
