# -*- coding: utf-8 -*-

import logging
from typing import Dict

from pyzwave.adapter import Adapter
from pyzwave.message import Message
from pyzwave.node import Node
from pyzwave.const.ZW_classcmd import (
    GENERIC_TYPE_STATIC_CONTROLLER,
    SPECIFIC_TYPE_GATEWAY,
)
from pyzwave.util import Listenable

_LOGGER = logging.getLogger(__name__)


class Application(Listenable):
    """
    Base class for managing the Z-Wave system
    """

    def __init__(self, adapter: Adapter):
        super().__init__()
        self.adapter = adapter
        self.adapter.addListener(self)
        self._typeInfo = (GENERIC_TYPE_STATIC_CONTROLLER, SPECIFIC_TYPE_GATEWAY)
        self._nodes = {}
        self._cmdClasses = []

    def setNodeInfo(self, generic, specific, cmdClasses):
        """Set the application NIF (Node Information Frame)"""
        self._typeInfo = (generic, specific)
        self._cmdClasses = cmdClasses

    def messageReceived(self, _sender, nodeId: int, message: Message, _flags: int):
        """Called when a message is received from a node"""
        node = self._nodes.get(nodeId)
        if not node:
            # Unknown node. Should not happen
            _LOGGER.warning(
                "Received message from unknown node %s: %s", nodeId, message
            )
            return False
        _reply = node.messageReceived(message)
        return True

    @property
    def nodes(self) -> Dict[int, Node]:
        """All nodes in the network"""
        return self._nodes

    async def shutdown(self):
        """Shut down the application gracefully"""

    async def startup(self):
        """Start and initialize the application and the adapter"""
        for nodeId in await self.adapter.getNodeList():
            nodeInfo = await self.adapter.getNodeInfo(nodeId)
            node = Node(nodeId, self.adapter, [x for x in nodeInfo.commandClass])
            node.basicDeviceClass = nodeInfo.basicDeviceClass
            # node.flirs = ?
            node.genericDeviceClass = nodeInfo.genericDeviceClass
            # node.isFailed = ?
            node.listening = nodeInfo.listening
            node.specificDeviceClass = nodeInfo.specificDeviceClass
            self._nodes[nodeId] = node
