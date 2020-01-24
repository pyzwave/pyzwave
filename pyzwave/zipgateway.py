# -*- coding: utf-8 -*-

import asyncio
import logging

from pyzwave.message import Message
from pyzwave.commandclass import NetworkManagementProxy, ZipGateway, ZipND
from pyzwave.zipconnection import ZIPConnection

_LOGGER = logging.getLogger(__name__)


class ZIPGateway(ZIPConnection):
    """Class for communicating with a zipgateway"""

    def __init__(self, address, psk):
        super().__init__(address, psk)
        self._connections = {}
        self._nmSeq = 0

    async def connect(self):
        await super().connect()
        await self.setGatewayMode(1)

    async def connectToNode(self, nodeId) -> ZIPConnection:
        """Returns a connection to the node"""
        if nodeId in self._connections:
            return self._connections[nodeId]

        ipv6 = await self.ipOfNode(nodeId)

        connection = ZIPConnection(ipv6.compressed, self.psk)
        connection.addListener(self)
        await connection.connect()
        self._connections[nodeId] = connection
        return connection

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

    async def sendToNode(self, nodeId: int, cmd: Message, **kwargs) -> bool:
        conn = await self.connectToNode(nodeId)
        return await conn.send(cmd, **kwargs)

    async def ipOfNode(self, nodeId):
        """Returns the IPv6 address of the node"""
        msg = ZipND.ZipInvNodeSolicitation(local=False, nodeId=nodeId)
        self._conn.send(msg.compose())
        response = await self.waitForMessage(ZipND.ZipNodeAdvertisement, timeout=3)
        return response.ipv6

    async def setGatewayMode(self, mode: int, timeout: int = 3) -> bool:
        try:
            report = await self.sendAndReceive(
                ZipGateway.GatewayModeGet(),
                ZipGateway.GatewayModeReport,
                timeout=timeout,
            )
            if report.mode != mode:
                await self.send(ZipGateway.GatewayModeSet(mode=mode))
        except asyncio.TimeoutError:
            _LOGGER.error("Got timeout waiting for gateway mode report")
            return False
        return True

    async def setNodeInfo(self, generic, specific, cmdClasses):
        raise NotImplementedError()
