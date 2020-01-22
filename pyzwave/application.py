# -*- coding: utf-8 -*-

import logging
from typing import Dict

from pyzwave.node import Node

_LOGGER = logging.getLogger(__name__)


class Application:
    """
    Base class for managing the Z-Wave system
    """

    def __init__(self, adapter):
        self.adapter = adapter
        self.adapter.addListener(self)
        self._nodes = {}

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
