# -*- coding: utf-8 -*-

import asyncio
import logging

from pyzwave.commandclass import NetworkManagementProxy, ZipND
from pyzwave.zipconnection import ZIPConnection

_LOGGER = logging.getLogger(__name__)


class ZIPGateway(ZIPConnection):
    """Class for communicating with a zipgateway"""

    def __init__(self, address, psk):
        super().__init__(address, psk)
        self._nmSeq = 0

    async def getNodeList(self) -> set:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementProxy.NodeListGet(seqNo=self._nmSeq)
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.NodeListReport
            )
        except asyncio.TimeoutError:
            # No response
            return {}
        return report.nodes

    async def ipOfNode(self, nodeId):
        """Returns the IPv6 address of the node"""
        msg = ZipND.ZipInvNodeSolicitation(local=False, nodeId=nodeId)
        self._conn.send(msg.compose())
        response = await self.waitForMessage(ZipND.ZipNodeAdvertisement, timeout=3)
        return response.ipv6
