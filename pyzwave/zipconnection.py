# -*- coding: utf-8 -*-

import asyncio
import logging

from pyzwave.message import Message
from pyzwave.commandclass import Zip
from pyzwave.dtlsconnection import DTLSConnection
from .adapter import Adapter

_LOGGER = logging.getLogger(__name__)


class ZIPConnection(Adapter):
    """Class for connecting to a zipgateway or zipnode"""

    def __init__(self, address, psk):
        super().__init__()
        self._seq = 0
        self._address = address
        self._psk = psk
        self._conn = DTLSConnection()
        self._conn.onMessage(self.onMessage)

    async def connect(self):
        await self._conn.connect(self._address, self._psk)

    def onMessage(self, pkt):
        """Called when a packed has recevied from the connection"""
        zipPkt = Message.decode(pkt)
        if not isinstance(zipPkt, Zip.ZipPacket):
            _LOGGER.warning("Received non Z/IP packet from zipgateway: %s", zipPkt)
            return False
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
        return True

    @property
    def psk(self) -> bytes:
        """The psk used for the connection"""
        return self._psk

    async def send(self, cmd, sourceEP=0, destEP=0, timeout=3):
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
        try:
            await self.waitForAck(msg.seqNo, timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return True
