# -*- coding: utf-8 -*-

import logging
from typing import Dict

from pyzwave.message import Message
from pyzwave.node import Node
from pyzwave.const.ZW_classcmd import (
    GENERIC_TYPE_STATIC_CONTROLLER,
    SPECIFIC_TYPE_GATEWAY,
)

_LOGGER = logging.getLogger(__name__)


class Application:
    """
    Base class for managing the Z-Wave system
    """

    def __init__(self, adapter):
        self.adapter = adapter
        self.adapter.addListener(self)
        self._typeInfo = (GENERIC_TYPE_STATIC_CONTROLLER, SPECIFIC_TYPE_GATEWAY)
        self._nodes = {}
        self._cmdClasses = []

    def setNodeInfo(self, generic, specific, cmdClasses):
        """Set the application NIF (Node Information Frame)"""
        self._typeInfo = (generic, specific)
        self._cmdClasses = cmdClasses

    @property
    def nodes(self) -> Dict[int, Node]:
        """All nodes in the network"""
        return self._nodes

    async def shutdown(self):
        """Shut down the application gracefully"""

    async def startup(self):
        """Start and initialize the application and the adapter"""
        for nodeId in await self.adapter.getNodeList():
            self._nodes[nodeId] = Node(nodeId, self.adapter)
