# -*- coding: utf-8 -*-
from pyzwave.adapter import Adapter
from pyzwave.message import Message


class Node:
    """
    Base class for a Z-Wave node
    """

    def __init__(self, nodeId: int, adapter: Adapter):
        self._adapter = adapter
        self._nodeId = nodeId

    @property
    def adapter(self) -> Adapter:
        """The adapter"""
        return self._adapter

    def messageReceived(self, message: Message) -> Message:
        """Called when a message is received directed to this node"""

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
