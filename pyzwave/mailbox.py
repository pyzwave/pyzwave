# -*- coding: utf-8 -*-
import asyncio
from ipaddress import IPv6Address
import logging

import crcmod.predefined

from pyzwave.adapter import Adapter
from pyzwave.commandclass import Mailbox, Zip
from pyzwave.message import Message

_LOGGER = logging.getLogger(__name__)


class QueueItem:
    """
    Class for holding one queue entry. It is also responsible for sending
    it's heartbeats
    """

    def __init__(self, nodeId: int, handle: int, data: bytes, adapter):
        self._adapter = adapter
        self._nodeId = nodeId
        self._handle = handle
        self._data = data
        self._task = None

    @property
    def checksum(self) -> int:
        """Return a checksum of the data"""
        # From the docs
        # To avoid duplicate entries, the Mailbox Service MUST maintain a list of CRC16
        # checksums for each mailbox entry. All mailbox entries MUST be unique, if a
        # matching CRC16 exists for an incoming package, the incoming package MUST be
        # discarded.
        crc16 = crcmod.predefined.mkCrcFun("crc-aug-ccitt")
        return crc16(self._data)

    @property
    def data(self) -> bytes:
        """The qctual queue data"""
        return self._data

    def start(self):
        """Start the task for sending heartbeats to the mailbox proxy"""
        self._task = asyncio.ensure_future(self._runner())

    def stop(self):
        """Stop sending heartbeats"""
        if self._task:
            self._task.cancel()

    async def _runner(self):
        i = 0
        while True:
            i += 1
            await asyncio.sleep(60)
            operation = Mailbox.Queue.Operation.WAITING
            if i % 10 == 0:
                operation = Mailbox.Queue.Operation.PING
            await self._adapter.sendToNode(
                self._nodeId,
                Mailbox.Queue(
                    last=False,
                    operation=operation,
                    queueHandle=self._handle,
                    mailboxEntry=self._data,
                ),
            )


class MailboxService:
    """Mailbox for storing messages for sleeping nodes"""

    def __init__(self, adapter):
        self._adapter: Adapter = adapter
        self._adapter.addListener(self)
        self._lastQueueId = None
        self._queue = {}

    async def initialize(self, ipaddress: IPv6Address, port: int) -> bool:
        """Initialize the mailbox"""
        msg = Mailbox.ConfigurationSet(
            mode=Mailbox.Mode.ENABLE_MAILBOX_PROXY_FORWARDING,
            forwardingDestinationIPv6Address=ipaddress,
            udpPortNumber=port,
        )
        return await self._adapter.send(msg)

    async def __popQueue__(self, nodeId: int, queueHandle: int):
        _LOGGER.debug("Pop queue (%d)", len(self._queue.get(queueHandle, [])))
        if not self._queue.get(queueHandle, None):
            return await self._adapter.sendToNode(
                nodeId,
                Mailbox.Queue(
                    last=True,
                    operation=Mailbox.Queue.Operation.POP,
                    queueHandle=queueHandle,
                ),
            )
        queueItem = self._queue[queueHandle].pop()
        ret = await self._adapter.sendToNode(
            nodeId,
            Mailbox.Queue(
                last=len(self._queue[queueHandle]) == 0,
                operation=Mailbox.Queue.Operation.POP,
                queueHandle=queueHandle,
                mailboxEntry=queueItem.data,
            ),
        )
        _LOGGER.info("Sent message from queue: %s", ret)
        if ret:
            queueItem.stop()
        return True

    async def __pushQueue__(self, nodeId: int, queueHandle: int, message: bytes):
        queueItem = QueueItem(nodeId, queueHandle, message, self._adapter)
        checksum = queueItem.checksum
        for item in self._queue.setdefault(queueHandle, []):
            if item.checksum == checksum:
                # Message has already been queueud
                return False
        ret = await self._adapter.sendToNode(
            nodeId,
            Mailbox.Queue(
                last=False,
                operation=Mailbox.Queue.Operation.WAITING,
                queueHandle=queueHandle,
                mailboxEntry=message,
            ),
        )
        if ret:
            queueItem.start()
            self._queue[queueHandle].append(queueItem)
        return ret

    async def messageReceived(
        self,
        _sender,
        rootNodeId: int,
        _endPoint: int,
        message: Message,
        _flags: Zip.HeaderExtension,
    ):
        """Handle incoming mailbox messages"""
        if isinstance(message, Mailbox.WakeupNotification):
            self._lastQueueId = message.queueHandle
            return await self.__popQueue__(rootNodeId, message.queueHandle)

        if (
            isinstance(message, Mailbox.Queue)
            and message.operation == Mailbox.Queue.Operation.ACK
        ):
            queueHandle = message.queueHandle or self._lastQueueId
            return await self.__popQueue__(rootNodeId, queueHandle)

        if (
            isinstance(message, Mailbox.Queue)
            and message.operation == Mailbox.Queue.Operation.PUSH
        ):
            return await self.__pushQueue__(
                rootNodeId, message.queueHandle, message.mailboxEntry
            )
