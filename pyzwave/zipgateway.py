# -*- coding: utf-8 -*-

import asyncio
import ipaddress
import logging

from pyzwave.message import Message
from pyzwave.commandclass import (
    NetworkManagementInclusion,
    NetworkManagementProxy,
    Zip,
    ZipGateway,
    ZipND,
)
from pyzwave.adapter import TxOptions
from pyzwave.connection import Connection
from pyzwave.zipconnection import ZIPConnection
from pyzwave.types import dsk_t

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

    async def addNode(self, txOptions: TxOptions) -> bool:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.NodeAdd(
            seqNo=self._nmSeq,
            mode=NetworkManagementInclusion.NodeAdd.Mode.ANY_S2,
            txOptions=txOptions,
        )
        try:
            # We do not get any immediate response
            await self.send(cmd)
        except asyncio.TimeoutError:
            return False
        return True

    async def addNodeDSKSet(
        self, accept: bool, inputDSKLength: int, dsk: dsk_t
    ) -> bool:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.NodeAddDSKSet(
            seqNo=self._nmSeq, accept=accept, inputDSKLength=inputDSKLength, dsk=dsk,
        )
        try:
            await self.send(cmd)
        except asyncio.TimeoutError:
            return False
        return True

    async def addNodeKeysSet(
        self, grantCSA: bool, accept: bool, grantedKeys: NetworkManagementInclusion.Keys
    ) -> bool:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.NodeAddKeysSet(
            seqNo=self._nmSeq,
            grantCSA=grantCSA,
            accept=accept,
            grantedKeys=grantedKeys,
        )
        try:
            await self.send(cmd)
        except asyncio.TimeoutError:
            return False
        return True

    async def addNodeStop(self) -> bool:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.NodeAdd(
            seqNo=self._nmSeq,
            mode=NetworkManagementInclusion.NodeAdd.Mode.STOP,
            txOptions=TxOptions.NULL,
        )
        try:
            await self.send(cmd)
        except asyncio.TimeoutError:
            return False
        return True

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

    async def getFailedNodeList(self) -> list:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementProxy.FailedNodeListGet(seqNo=self._nmSeq,)
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.FailedNodeListReport
            )
        except asyncio.TimeoutError:
            return set()
        return report.failedNodeList

    async def getMultiChannelEndPoints(self, nodeId: int) -> int:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementProxy.MultiChannelEndPointGet(
            seqNo=self._nmSeq, nodeID=nodeId
        )
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.MultiChannelEndPointReport
            )
        except asyncio.TimeoutError:
            # No response
            return 0
        return report.individualEndPoints + report.aggregatedEndPoints

    async def getMultiChannelCapability(
        self, nodeId: int, endpoint: int
    ) -> NetworkManagementProxy.MultiChannelCapabilityReport:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementProxy.MultiChannelCapabilityGet(
            seqNo=self._nmSeq, nodeID=nodeId, endPoint=endpoint
        )
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.MultiChannelCapabilityReport
            )
        except asyncio.TimeoutError:
            # No response
            return NetworkManagementProxy.MultiChannelCapabilityReport()
        return report

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
        self._nodeId = report.nodeListControllerId
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

    async def __handleNodeListReport__(
        self, report: NetworkManagementProxy.NodeListReport
    ):
        """Update nodes from a nodeListReport"""
        # Find removed nodes
        for nodeId in list(self._nodes.keys()):
            if nodeId in report.nodes:
                continue
            del self._nodes[nodeId]

        # Find new nodes
        for nodeId in report.nodes:
            if nodeId in self._nodes:
                continue
            # Retrieve ip
            self._nodes[nodeId] = {"ip": await self.ipOfNode(nodeId)}
        self.speak("nodeListUpdated")

    async def ipOfNode(self, nodeId) -> ipaddress.IPv6Address:
        """Returns the IPv6 address of the node"""
        msg = ZipND.ZipInvNodeSolicitation(local=False, nodeId=nodeId)
        self._conn.send(msg.compose())
        response = await self.waitForMessage(ZipND.ZipNodeAdvertisement, timeout=3)
        return response.ipv6

    async def removeFailedNode(
        self, nodeId: int
    ) -> NetworkManagementInclusion.FailedNodeRemoveStatus.Status:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.FailedNodeRemove(
            seqNo=self._nmSeq, nodeID=nodeId
        )
        try:
            # The timeout might need to be increased. The Z-Wave may need to query the
            # network for a response first and this may take time on a large network
            report = await self.sendAndReceive(
                cmd, NetworkManagementInclusion.FailedNodeRemoveStatus, timeout=10
            )
        except asyncio.TimeoutError:
            return NetworkManagementInclusion.FailedNodeRemoveStatus.Status.REMOVE_FAIL
        return report.status

    async def removeNode(self) -> bool:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.NodeRemove(
            seqNo=self._nmSeq, mode=NetworkManagementInclusion.NodeRemove.Mode.ANY
        )
        try:
            # We do not get any immediate response
            await self.send(cmd)
        except asyncio.TimeoutError:
            return False
        return True

    async def removeNodeStop(self) -> bool:
        self._nmSeq = self._nmSeq + 1
        cmd = NetworkManagementInclusion.NodeRemove(
            seqNo=self._nmSeq, mode=NetworkManagementInclusion.NodeRemove.Mode.STOP
        )
        try:
            # We do not get any immediate response
            await self.send(cmd)
        except asyncio.TimeoutError:
            return False
        return True

    def onMessageReceived(self, connection: ZIPConnection, message: Message):
        """Called when a message is received from any node connection. Not unsolicited."""
        sourceEP = 0
        if isinstance(message, Zip.ZipPacket):
            sourceEP = message.sourceEP
            message = message.command
        for nodeId, nodeConnection in self._connections.items():
            if connection != nodeConnection:
                continue
            flags = 0  # Set flags such as encapsulation type
            self.speak("messageReceived", nodeId, sourceEP, message, flags)
            return
        _LOGGER.warning("Got message from unknown sender %s: %s", connection, message)

    def onUnsolicitedMessage(self, pkt, address):
        """
        Called when an unsolicited message is received.
        We do not know the node id the message is from. Only the ip address.
        """
        zipPkt = Message.decode(pkt)
        sourceIp = ipaddress.IPv6Address(address[0])
        sourceEP = zipPkt.sourceEP

        if isinstance(zipPkt.command, NetworkManagementProxy.NodeListReport):
            return asyncio.ensure_future(self.__handleNodeListReport__(zipPkt.command))

        # Find the node this was from
        for nodeId, node in self._nodes.items():
            if node.get("ip") != sourceIp:
                continue
            if zipPkt.ackRequest:
                # This message needs an ack response.
                ackReponse = zipPkt.response(success=True)
                self._unsolicitedConnection.sendTo(ackReponse.compose(), address)

            self.speak(
                "messageReceived",
                nodeId,
                sourceEP,
                zipPkt.command,
                zipPkt.headerExtension,
            )
            return True
        _LOGGER.warning(
            "Got message from unknown sender %s: %s", sourceIp, zipPkt.command
        )
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
