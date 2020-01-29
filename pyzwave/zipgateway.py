# -*- coding: utf-8 -*-

import asyncio
import ipaddress
import logging

from pyzwave.message import Message
from pyzwave.commandclass import NetworkManagementProxy, ZipGateway, ZipND
from pyzwave.connection import Connection
from pyzwave.zipconnection import ZIPConnection

_LOGGER = logging.getLogger(__name__)


class ZIPGateway(ZIPConnection):
    """Class for communicating with a zipgateway"""

    def __init__(self, address, psk):
        super().__init__(address, psk)
        self._unsolicitedConnection = Connection()
        self._unsolicitedConnection.onMessage(self.onUnsolicitedMessage)
        self._connections = {}
        self._nodes = {}
        self._nmSeq = 0

    async def connect(self):
        await super().connect()
        await self.setGatewayMode(1)
        await self.setupUnsolicitedConnection()

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
        if self._nodes:
            # Return cached list
            return set(self._nodes.keys())
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementProxy.NodeListGet(seqNo=self._nmSeq)
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.NodeListReport
            )
        except asyncio.TimeoutError:
            # No response
            return set()
        self._nodes = {x: {} for x in report.nodes}
        return report.nodes

    async def getNodeInfo(
        self, nodeId: int
    ) -> NetworkManagementProxy.NodeInfoCachedReport:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementProxy.NodeInfoCachedGet(
            seqNo=self._nmSeq, maxAge=15, nodeID=nodeId
        )
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.NodeInfoCachedReport
            )
        except asyncio.TimeoutError:
            return NetworkManagementProxy.NodeInfoCachedReport()
        return report

    async def ipOfNode(self, nodeId):
        """Returns the IPv6 address of the node"""
        msg = ZipND.ZipInvNodeSolicitation(local=False, nodeId=nodeId)
        self._conn.send(msg.compose())
        response = await self.waitForMessage(ZipND.ZipNodeAdvertisement, timeout=3)
        return response.ipv6

    def onUnsolicitedMessage(self, pkt, address):
        """
        Called when an unsolicited message is received.
        We do not know the node id the message is from. Only the ip address.
        """
        zipPkt = Message.decode(pkt)
        sourceIp = ipaddress.IPv6Address(address[0])
        # Find the node this was from
        for nodeId, node in self._nodes.items():
            if node.get("ip") == sourceIp:
                flags = 0  # Set flags such as encapsulation type
                self.speak("messageReceived", nodeId, zipPkt.command, flags)
                return True
        _LOGGER.warning(
            "Got message from unknown sender %s: %s", sourceIp, zipPkt.command
        )
        _LOGGER.debug(zipPkt.debugString())
        return False

    async def sendToNode(self, nodeId: int, cmd: Message, **kwargs) -> bool:
        conn = await self.connectToNode(nodeId)
        return await conn.send(cmd, **kwargs)

    async def setGatewayMode(self, mode: int, timeout: int = 3) -> bool:
        """Set gateway to standalone or portal mode"""
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

    async def setupUnsolicitedConnection(self):
        """
        Setup for listening for unsolicited connections. This function must not be called
        explicitly. It is called by the connect() method automatically
        """
        await self._unsolicitedConnection.listen(self.psk, 4123)
        await self.send(
            ZipGateway.UnsolicitedDestinationSet(
                unsolicitedIPv6Destination=ipaddress.IPv6Address("::ffff:c0a8:31"),
                port=4123,
            )
        )
        # Retrieve node list, and get ip-addresses
        for nodeId in await self.getNodeList():
            if not self._nodes[nodeId].get("ip"):
                self._nodes[nodeId] = {"ip": await self.ipOfNode(nodeId)}
