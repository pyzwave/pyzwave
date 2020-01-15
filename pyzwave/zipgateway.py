# -*- coding: utf-8 -*-

import asyncio
import logging

import socket
from struct import pack, unpack

from pyzwave.message import Message
from pyzwave.commandclass import NetworkManagementProxy, Zip
from pyzwave.dtlsconnection import DTLSConnection
from .adapter import Adapter

_LOGGER = logging.getLogger(__name__)


class ZIPGateway(Adapter):
    def __init__(self):
        super().__init__()
        self.nm_seq = 0
        self.seq = 0
        self.imaEnabled = False
        self.more_info = False
        self._conn = DTLSConnection()
        self._conn.onMessage(self.onMessage)

    async def connect(self, address, psk):
        await self._conn.connect(address, psk)

    async def getNodeList(self):
        self.nm_seq = self.nm_seq + 1
        cmd = NetworkManagementProxy.NodeListGet.create(seqNo=self.nm_seq)
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.NodeListReport
            )
        except asyncio.TimeoutError:
            # No response
            return {}
        return report.nodes

    def onMessage(self, pkt):
        zipPkt = Message.decode(pkt)
        if not isinstance(zipPkt, Zip.ZipPacket):
            _LOGGER.warning("Received non Z/IP packet from zipgateway: %s", zipPkt)
            return
        if zipPkt.ackResponse:
            self.ackReceived(zipPkt.seqNo)
            return
        if zipPkt.nackResponse:
            _LOGGER.error("NAck response not implemented")
            # self.nackReceived(zipPkt.seqNo)
            return
        if zipPkt.ackRequest:
            _LOGGER.error("This message needs an ack response. Not implemented")
            return
        if zipPkt.zwCmdIncluded:
            self.commandReceived(zipPkt.command)

    async def send(self, cmd, sourceEP=0, destEP=0):
        self.seq = (self.seq + 1) & 0xFF
        msg = Zip.ZipPacket.create(command=cmd)
        msg.ackRequest = True
        msg.seqNo = self.seq
        msg.sourceEP = sourceEP
        msg.destEP = destEP
        self._conn.send(msg.compose())
        try:
            await self.waitForAck(msg.seqNo)
        except asyncio.TimeoutError:
            return False
        return True
