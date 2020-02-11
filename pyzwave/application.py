# -*- coding: utf-8 -*-

import logging
from typing import Dict

from pyzwave.adapter import Adapter
from pyzwave.message import Message
from pyzwave.node import Node, NodeEndPoint
from pyzwave.const.ZW_classcmd import (
    GENERIC_TYPE_STATIC_CONTROLLER,
    SPECIFIC_TYPE_GATEWAY,
    COMMAND_CLASS_MULTI_CHANNEL_V2,
)
from pyzwave.persistantstorage import PersistantStorage
from pyzwave.util import Listenable

_LOGGER = logging.getLogger(__name__)


class Application(Listenable):
    """
    Base class for managing the Z-Wave system
    """

    def __init__(self, adapter: Adapter, storage: PersistantStorage):
        super().__init__()
        self.adapter = adapter
        self.adapter.addListener(self)
        self.addListener(storage)
        self._storage = storage
        self._typeInfo = (GENERIC_TYPE_STATIC_CONTROLLER, SPECIFIC_TYPE_GATEWAY)
        self._nodes = {}
        self._cmdClasses = []

    async def loadEndPointNode(self, node: Node, endpoint: int):
        """Load an endpoint for a node"""
        report = await self.adapter.getMultiChannelCapability(node.rootNodeId, endpoint)
        nodeEP = NodeEndPoint(node, endpoint, self.adapter, list(report.commandClass))
        nodeEP.addListener(self._storage)
        nodeEP.genericDeviceClass = report.genericDeviceClass
        nodeEP.specificDeviceClass = report.specificDeviceClass
        self._nodes[nodeEP.nodeId] = nodeEP
        self.speak("nodeAdded", nodeEP)

    async def loadNode(self, nodeId: int):
        """Load a node"""
        nodeInfo = await self.adapter.getNodeInfo(nodeId)
        node = Node(nodeId, self.adapter, list(nodeInfo.commandClass))
        node.addListener(self._storage)
        node.basicDeviceClass = nodeInfo.basicDeviceClass
        # node.flirs = ?
        node.genericDeviceClass = nodeInfo.genericDeviceClass
        # node.isFailed = ?
        node.listening = nodeInfo.listening
        node.specificDeviceClass = nodeInfo.specificDeviceClass
        self._nodes[node.nodeId] = node
        self.speak("nodeAdded", node)

        if node.supports(COMMAND_CLASS_MULTI_CHANNEL_V2):
            endpoints = await self.adapter.getMultiChannelEndPoints(nodeId)
            for endpoint in range(1, endpoints + 1):
                await self.loadEndPointNode(node, endpoint)

    async def messageReceived(
        self, _sender, rootNodeId: int, endPoint: int, message: Message, _flags: int
    ):
        """Called when a message is received from a node"""
        nodeId = "{}:{}".format(rootNodeId, endPoint)
        node = self._nodes.get(nodeId)
        if not node:
            # Unknown node. Should not happen
            _LOGGER.warning(
                "Received message from unknown node %s: %s", nodeId, message
            )
            return False
        _reply = await node.handleMessage(message)
        return True

    @property
    def nodes(self) -> Dict[int, Node]:
        """All nodes in the network"""
        return self._nodes

    def setNodeInfo(self, generic, specific, cmdClasses):
        """Set the application NIF (Node Information Frame)"""
        self._typeInfo = (generic, specific)
        self._cmdClasses = cmdClasses

    async def shutdown(self):
        """Shut down the application gracefully"""

    async def startup(self):
        """Start and initialize the application and the adapter"""
        for nodeId in await self.adapter.getNodeList():
            await self.loadNode(nodeId)

        for nodeId in await self.adapter.getFailedNodeList():
            _LOGGER.warning("FAILED node %s", nodeId)
