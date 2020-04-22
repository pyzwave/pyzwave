# -*- coding: utf-8 -*-
import asyncio
from enum import Enum, auto
from contextlib import contextmanager
import logging
from typing import Dict

from pyzwave.adapter import Adapter
from pyzwave.commandclass import (
    CommandClass,
    NetworkManagementInclusion,
    Supervision,
    Zip,
)
from pyzwave.message import Message
from pyzwave.util import Listenable, MessageWaiter

from pyzwave.const.ZW_classcmd import COMMAND_CLASS_ZWAVEPLUS_INFO

_LOGGER = logging.getLogger(__name__)


def supervision(func):
    """Decoratior for handling calls wrapped in supervision messages"""

    async def __wrapper__(self, message: Message, flags):
        if not isinstance(message, Supervision.Get):
            return await func(self, message, flags)
        # Handle supervision calls
        if await func(self, message.command, flags):
            await self.send(
                Supervision.Report(
                    moreStatusUpdates=False,
                    wakeUpRequest=False,
                    sessionID=message.sessionID,
                    status=0xFF,
                    duration=0,
                )
            )
            return True
        await self.send(
            Supervision.Report(
                moreStatusUpdates=False,
                wakeUpRequest=False,
                sessionID=message.sessionID,
                status=0x00,
                duration=0,
            )
        )
        return False

    return __wrapper__


class StorageStatus(Enum):
    """Storage status flag"""

    CLEAN = auto()
    LOCKED_CLEAN = auto()
    LOCKED_DIRTY = auto()


class Node(Listenable, MessageWaiter):
    """
    Base class for a Z-Wave node
    """

    def __init__(self, nodeId: int, adapter: Adapter, cmdClasses: list):
        super().__init__()
        self._adapter = adapter
        self._basicDeviceClass = 0
        self._controlled = {}
        # Flag is this node need to be saved to persistant storage
        self._storageStatus: StorageStatus = StorageStatus.CLEAN
        self._endpoint = 0
        self._flirs = False
        self._genericDeviceClass = 0
        self._isFailed = False
        self._listening = False
        self._nodeId = nodeId
        self._specificDeviceClass = 0
        self._supported = {}
        i = 0
        supported = True
        securityS0 = False
        while i < len(cmdClasses):
            cmdClass = cmdClasses[i]
            if cmdClass == 0xF1 and cmdClasses[i + 1] == 0x00:
                # Security Scheme 0 Mark
                securityS0 = True
                supported = True
                i += 2
                continue
            if cmdClass == 0xEF:
                # Support/Control mark
                supported = False
                i += 1
                continue
            clsObject = CommandClass.load(cmdClass, securityS0, self)
            if supported:
                self._supported[cmdClass] = clsObject
                clsObject.addListener(self)
            else:
                self._controlled[cmdClass] = clsObject
            # _LOGGER.info(
            #     "Load command class for %X %s", cmdClass, clsObject,
            # )
            i += 1

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

    def commandClassUpdated(self, _commandClass: CommandClass):
        """Called by the command classes if their data is updated"""
        if self._storageStatus == StorageStatus.CLEAN:
            # Signal update needed
            self.speak("nodeUpdated")
        elif self._storageStatus == StorageStatus.LOCKED_CLEAN:
            # Storage is locked, move to dirty
            self._storageStatus = StorageStatus.LOCKED_DIRTY

    @property
    def endpoint(self) -> int:
        """Returns the endpoint if this is a subnode. 0 if it is the root node"""
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint: int):
        self._endpoint = endpoint

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

    @supervision
    async def handleMessage(self, message: Message, flags: Zip.HeaderExtension) -> bool:
        """Handle and incomming message. Route it to the correct handler"""
        handled = False
        if self.messageReceived(message) is True:
            # Message has already been handled
            handled = True
        cmdClass: CommandClass = self.supported.get(message.cmdClass())
        if cmdClass:
            retval = await cmdClass.handleMessage(message, flags)
            if retval:
                return retval
        if handled:
            return True
        for retval in await self.ask("onMessage", message):
            if retval:
                return retval
        # Message was not handled
        _LOGGER.warning("Unhandled message %s from node %s", message, self.nodeId)
        _LOGGER.debug(message.debugString())
        return False

    async def interview(self):
        """
        (Re)interview this node. It is recommended to apply the :meth:`storageLock()`
        before calling this function.
        """
        for _, cmdClass in self._supported.items():
            try:
                await cmdClass.interview()
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout interviewing %s", cmdClass.name)

    @property
    def isFailed(self) -> bool:
        """Returns is this node is considered failing or not"""
        return self._isFailed

    @isFailed.setter
    def isFailed(self, isFailed: bool):
        self._isFailed = isFailed

    @property
    def isZWavePlus(self) -> bool:
        """Returns True if this is a Z-Wave Plus node"""
        return self.supports(COMMAND_CLASS_ZWAVEPLUS_INFO)

    @property
    def listening(self) -> bool:
        """Returns True if this node is listening. False if it is a sleeping node"""
        return self._listening

    @listening.setter
    def listening(self, listening: bool):
        self._listening = listening

    @property
    def nodeId(self) -> str:
        """The node id in the format nodeid:channel"""
        return "{}:{}".format(self._nodeId, self._endpoint)

    async def remove(self) -> bool:
        """
        Remove this node from the network. This only works if the node is
        marked as failed in the Z-Wave chip
        """
        status = await self.adapter.removeFailedNode(self.rootNodeId)
        if status == NetworkManagementInclusion.FailedNodeRemoveStatus.Status.DONE:
            return True
        _LOGGER.warning("Could not remove failed node, reason %s", status)
        return False

    @property
    def rootNodeId(self) -> int:
        """Return the root node id"""
        return self._nodeId

    async def send(self, cmd: Message, timeout: int = 3) -> bool:
        """Send a message to this node"""
        return await self._adapter.sendToNode(
            self._nodeId, cmd, sourceEP=0, destEP=self._endpoint, timeout=timeout
        )

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        """Send a message and wait for the response"""
        self.addWaitingSession(waitFor)
        retval = await self.send(cmd, **kwargs)
        if not retval:
            # Node did not wakeup in time!
            raise asyncio.TimeoutError()
        return await self.waitForMessage(waitFor, timeout=timeout)

    @contextmanager
    def storageLock(self):
        """
        Suppresses (temporarily) the signals to store settings persistant.

        Some memories do not like to be written to often, such as flash memories
        found in embedded boards. If the application knows the node will be updated
        a lock can be added so it will only be written to disc once all operations has
        been finished.
        To use this lock use the with-statement:

        .. code-block:: python

            with node.storageLock():
                # Do operations with the node here.
                # Nothing will be stored to disk.
                node.interview()
            # The storage will happen here, only once
        """
        try:
            self._storageStatus = StorageStatus.LOCKED_CLEAN
            yield
        finally:
            if self._storageStatus == StorageStatus.LOCKED_DIRTY:
                self.speak("nodeUpdated")
            self._storageStatus = StorageStatus.CLEAN

    @property
    def specificDeviceClass(self) -> int:
        """Returns this nodes specific device class"""
        return self._specificDeviceClass

    @specificDeviceClass.setter
    def specificDeviceClass(self, specificDeviceClass: int):
        self._specificDeviceClass = specificDeviceClass

    @property
    def supported(self) -> Dict[int, CommandClass]:
        """Return a dict of command classes this node supports"""
        return self._supported

    def supports(self, commandClass: int) -> bool:
        """Returns if this node supports a specific command class or not"""
        return commandClass in self._supported


class NodeEndPoint(Node):
    """Base class for a sub node for nodes supporting command class multi channel"""

    def __init__(self, parent: Node, endpoint: int, adapter: Adapter, cmdClasses: list):
        super().__init__(parent.rootNodeId, adapter, cmdClasses)
        self._parent = parent
        self.endpoint = endpoint

    @property
    def basicDeviceClass(self) -> int:
        """Return this nodes basic device class"""
        return self._parent.basicDeviceClass

    @property
    def flirs(self) -> bool:
        """Returns if this node is a FLiRS node or not"""
        return self._parent.flirs

    @property
    def isFailed(self) -> bool:
        """Returns is this node is considered failing or not"""
        return self._parent.isFailed

    @property
    def listening(self) -> bool:
        """Returns True if this node is listening. False if it is a sleeping node"""
        return self._parent.listening

    @property
    def parent(self) -> Node:
        """Returns the parent node"""
        return self._parent
