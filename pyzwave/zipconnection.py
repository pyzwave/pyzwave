# -*- coding: utf-8 -*-

import asyncio
import logging

from pyzwave.message import Message
from pyzwave.commandclass import (
    NetworkManagementInclusion,
    NetworkManagementProxy,
    Zip,
    ZipND,
)
from pyzwave.connection import Connection
from .adapter import Adapter, TxOptions
from .types import dsk_t

_LOGGER = logging.getLogger(__name__)


class ZIPConnection(Adapter):
    """Class for connecting to a zipgateway or zipnode"""

    def __init__(self, address, psk):
        super().__init__()
        self._seq = 0
        self._address = address
        self._keepAlive = None
        self._psk = psk
        self._conn = Connection()
        self._conn.onMessage(self.onPacket)

    async def addNode(self, txOptions: TxOptions) -> bool:
        raise NotImplementedError()

    async def addNodeDSKSet(
        self, accept: bool, inputDSKLength: int, dsk: dsk_t
    ) -> bool:
        raise NotImplementedError()

    async def addNodeKeysSet(
        self, grantCSA: bool, accept: bool, grantedKeys: NetworkManagementInclusion.Keys
    ) -> bool:
        raise NotImplementedError()

    async def addNodeStop(self) -> bool:
        raise NotImplementedError()

    async def connect(self):
        await self._conn.connect(self._address, self._psk)
        self.resetKeepAlive()

    async def getFailedNodeList(self) -> list:
        raise NotImplementedError()

    async def getMultiChannelCapability(
        self, nodeId: int, endpoint: int
    ) -> NetworkManagementProxy.MultiChannelCapabilityReport:
        raise NotImplementedError()

    async def getMultiChannelEndPoints(self, nodeId: int) -> int:
        raise NotImplementedError()

    async def getNodeList(self) -> set:
        raise NotImplementedError()

    async def getNodeInfo(
        self, nodeId: int
    ) -> NetworkManagementProxy.NodeInfoCachedReport:
        raise NotImplementedError()

    def keepAlive(self):
        """Send a keepalive message"""
        msg = Zip.ZipKeepAlive(ackRequest=True, ackResponse=False,)
        self._conn.send(msg.compose())
        self.resetKeepAlive()

    def onPacket(self, pkt):
        """Called when a packed has recevied from the connection"""
        try:
            zipPkt = Message.decode(pkt)
        except Exception:
            _LOGGER.error("Could not decode message. Raw message:")
            _LOGGER.error("%s", pkt)
            return False
        if isinstance(zipPkt, Zip.ZipPacket):
            if zipPkt.ackResponse:
                self.ackReceived(zipPkt)
                return True
            if zipPkt.nackResponse:
                if zipPkt.nackWaiting:
                    # Waiting: the preceding Z/IP Packet encapsulated Z-Wave Command is not yet
                    # delivered to the destination and delivery will be attempted later on
                    # Threat these as normal acks
                    self.ackReceived(zipPkt)
                    return True
                _LOGGER.error("Nack response not implemented %s", zipPkt.debugString())
                # self.nackReceived(zipPkt.seqNo)
                return False
            if zipPkt.ackRequest:
                _LOGGER.error("This message needs an ack response. Not implemented")
                return False
            if zipPkt.zwCmdIncluded:
                self.commandReceived(zipPkt)
        elif isinstance(zipPkt, Zip.ZipKeepAlive):
            if zipPkt.ackResponse:
                # Ignore a response
                return True
            _LOGGER.error("This message needs an ack response. Not implemented")
            return False
        elif isinstance(zipPkt, ZipND.ZipNodeAdvertisement):
            self.commandReceived(zipPkt)
        else:
            _LOGGER.warning("Received unknown Z/IP packet from zipgateway: %s", zipPkt)
            return False
        return True

    @property
    def psk(self) -> bytes:
        """The psk used for the connection"""
        return self._psk

    async def removeFailedNode(
        self, nodeId: int
    ) -> NetworkManagementInclusion.FailedNodeRemoveStatus.Status:
        raise NotImplementedError()

    async def removeNode(self) -> bool:
        raise NotImplementedError()

    async def removeNodeStop(self) -> bool:
        raise NotImplementedError()

    def resetKeepAlive(self):
        """Reset the keepalive timeout"""
        if self._keepAlive:
            # Timer running, reset it
            self._keepAlive.cancel()
        self._keepAlive = asyncio.get_event_loop().call_later(25, self.keepAlive)

    async def send(self, cmd, sourceEP=0, destEP=0, timeout=3) -> bool:
        self._seq = (self._seq + 1) & 0xFF
        msg = Zip.ZipPacket(
            ackRequest=True,
            ackResponse=False,
            nackResponse=False,
            nackWaiting=False,
            nackQueueFull=False,
            nackOptionError=False,
            headerExtIncluded=False,
            zwCmdIncluded=True,
            moreInformation=False,
            secureOrigin=True,
            seqNo=self._seq,
            sourceEP=sourceEP,
            destEP=destEP,
            command=cmd,
        )
        self._conn.send(msg.compose())
        self.resetKeepAlive()
        try:
            await self.waitForAck(msg.seqNo, timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return True

    async def setNodeInfo(self, generic, specific, cmdClasses):
        raise NotImplementedError()
