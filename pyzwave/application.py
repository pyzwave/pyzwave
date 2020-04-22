# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict

from pyzwave.adapter import Adapter
from pyzwave.commandclass import NetworkManagementInclusion, Zip
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
        return nodeEP

    async def loadNode(self, nodeId: int) -> list:
        """Load a node"""
        if nodeId == self.adapter.nodeId:
            # Ignore ourself
            return []
        nodes = []
        nodeInfo = await self.adapter.getNodeInfo(nodeId)
        node = Node(nodeId, self.adapter, list(nodeInfo.commandClass))
        nodes.append(node)
        node.addListener(self._storage)
        node.basicDeviceClass = nodeInfo.basicDeviceClass
        # node.flirs = ?
        node.genericDeviceClass = nodeInfo.genericDeviceClass
        # node.isFailed = ?
        node.listening = nodeInfo.listening
        node.specificDeviceClass = nodeInfo.specificDeviceClass
        self._nodes[node.nodeId] = node

        if node.supports(COMMAND_CLASS_MULTI_CHANNEL_V2):
            endpoints = await self.adapter.getMultiChannelEndPoints(nodeId)
            for endpoint in range(1, endpoints + 1):
                nodes.append(await self.loadEndPointNode(node, endpoint))
        return nodes

    async def messageReceived(
        self,
        _sender,
        rootNodeId: int,
        endPoint: int,
        message: Message,
        flags: Zip.HeaderExtension,
    ):
        """Called when a message is received from a node"""
        nodeId = "{}:{}".format(rootNodeId, endPoint)
        node = self._nodes.get(nodeId)
        if node:
            reply = await node.handleMessage(message, flags)
            if reply:
                # Message was handled
                return True
            return False
        if rootNodeId != self.adapter.nodeId:
            # Unknown node. Should not happen
            _LOGGER.warning(
                "Received message from unknown node %s: %s", nodeId, message
            )
            return False
        # Message from the Z-Wave chip
        await self.ask("messageReceived", message)
        # TODO, check retval from above and see if message was handled
        return True

    async def nodeListUpdated(self, _sender):
        """Called when the node list has been updated"""
        nodeList = await self.adapter.getNodeList()
        nodesToRemove = []
        for nodeId, node in self._nodes.items():
            if node.rootNodeId in nodeList:
                continue
            nodesToRemove.append(nodeId)
        for nodeId in nodesToRemove:
            del self._nodes[nodeId]
            await self.ask("nodeRemoved", nodeId)
        # For clients supporting batch removing
        if nodesToRemove:
            await self.ask("nodesRemoved", nodesToRemove)

        # Find new nodes
        newNodes = []
        for nodeId in nodeList:
            if "{}:0".format(nodeId) in self._nodes:
                continue
            newNodes.extend(await self.loadNode(nodeId))

        if newNodes:
            await self.ask("nodesAdded", newNodes)
        for node in newNodes:
            await self.ask("nodeAdded", node)

    @property
    def nodes(self) -> Dict[int, Node]:
        """All nodes in the network"""
        return self._nodes

    async def onMessageReceived(self, _speaker: Any, msg: Message) -> bool:
        """Listener method from the adapter for any unhandled messages"""
        if not isinstance(msg, Zip.ZipPacket):
            # Ignore non ZipPacket
            return False
        command = msg.command
        if isinstance(command, NetworkManagementInclusion.NodeAddStatus):
            await self.ask("addNodeStatus", command)
            return True
        if isinstance(command, NetworkManagementInclusion.NodeRemoveStatus):
            await self.ask("removeNodeStatus", command)
            if (
                command.status
                != NetworkManagementInclusion.NodeRemoveStatus.Status.DONE
            ):
                return True
            if command.nodeID == 0:
                # Fire this case since it may be used to exclude nodes not in our network
                await self.ask("nodeRemoved", 0)
                await self.ask("nodesRemoved", [0])
            return True
        if command is None:
            return False
        for response in await self.ask("messageReceived", command):
            if response is True:
                # It was handled
                return True
        _LOGGER.info("Unhandled message! %s", command.debugString())
        return False

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

        await self.ask("nodesAdded", list(self._nodes.values()))
        for _, node in self._nodes.items():
            await self.ask("nodeAdded", node)
