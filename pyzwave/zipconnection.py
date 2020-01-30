# -*- coding: utf-8 -*-

import asyncio
import logging

from pyzwave.message import Message
from pyzwave.commandclass import NetworkManagementProxy, Zip, ZipND
from pyzwave.connection import Connection
from .adapter import Adapter

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

    async def connect(self):
        await self._conn.connect(self._address, self._psk)
        self.resetKeepAlive()

    async def getFailedNodeList(self) -> list:
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
        zipPkt = Message.decode(pkt)
        if isinstance(zipPkt, Zip.ZipPacket):
            if zipPkt.ackResponse:
                self.ackReceived(zipPkt.seqNo)
                return True
            if zipPkt.nackResponse:
                _LOGGER.error("NAck response not implemented")
                # self.nackReceived(zipPkt.seqNo)
                return False
            if zipPkt.ackRequest:
                _LOGGER.error("This message needs an ack response. Not implemented")
                return False
            if zipPkt.zwCmdIncluded:
                self.commandReceived(zipPkt.command)
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
