# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Dict

from pyzwave.adapter import Adapter
from pyzwave.commandclass import CommandClass, Supervision
from pyzwave.message import Message
from pyzwave.util import Listenable, MessageWaiter

from pyzwave.const.ZW_classcmd import COMMAND_CLASS_ZWAVEPLUS_INFO

_LOGGER = logging.getLogger(__name__)


def supervision(func):
    """Decoratior for handling calls wrapped in supervision messages"""

    async def __wrapper__(self, message: Message):
        if not isinstance(message, Supervision.Get):
            return await func(self, message)
        # Handle supervision calls
        if await func(self, message.command):
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


class Node(Listenable, MessageWaiter):
    """
    Base class for a Z-Wave node
    """

    def __init__(self, nodeId: int, adapter: Adapter, cmdClasses: list):
        super().__init__()
        self._adapter = adapter
        self._basicDeviceClass = 0
        self._controlled = {}
        self._dirty = False  # Flag is this node need to be saved to persistant storage
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
        self._dirty = True

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
    async def handleMessage(self, message: Message) -> bool:
        """Handle and incomming message. Route it to the correct handler"""
        if self.messageReceived(message) is True:
            # Message has already been handled
            return True
        cmdClass: CommandClass = self.supported.get(message.cmdClass())
        if cmdClass:
            retval = await cmdClass.handleMessage(message)
            if retval:
                return retval
        for retval in await self.ask("onMessage", message):
            if retval:
                return retval
        # Message was not handled
        _LOGGER.warning("Unhandled message %s from node %s", message, self.nodeId)
        return False

    async def interview(self):
        """(Re)interview this node"""
        for _, cmdClass in self._supported.items():
            try:
                await cmdClass.interview()
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout interviewing %s", cmdClass.NAME)
        if self._dirty:
            self.speak("nodeUpdated")
            self._dirty = False

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
        await self.send(cmd, **kwargs)
        return await self.waitForMessage(waitFor, timeout=timeout)

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
