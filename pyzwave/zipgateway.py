# -*- coding: utf-8 -*-

import asyncio
import logging

import socket
from struct import pack, unpack

from pyzwave.message import Message
from pyzwave.commandclass import NetworkManagementProxy, Zip
from pyzwave.zipconnection import ZIPConnection
from .adapter import Adapter

_LOGGER = logging.getLogger(__name__)


class ZIPGateway(ZIPConnection):
    def __init__(self):
        super().__init__()

    async def getNodeList(self):
        self.nm_seq = self.nm_seq + 1
        cmd = NetworkManagementProxy.NodeListGet(seqNo=self.nm_seq)
        try:
            report = await self.sendAndReceive(
                cmd, NetworkManagementProxy.NodeListReport
            )
        except asyncio.TimeoutError:
            # No response
            return {}
        return report.nodes
