# -*- coding: utf-8 -*-

import asyncio
import logging

from .util import Listenable

_LOGGER = logging.getLogger(__name__)


class Adapter(Listenable):
    def __init__(self):
        super().__init__()
        self._ackQueue = {}
        self._sessions = {}

    def ackReceived(self, ackId):
        event = self._ackQueue.pop(ackId, None)
        if not event:
            _LOGGER.warning("Received ack for command not waiting for")
            return
        event.set()

    def commandReceived(self, cmd):
        session = self._sessions.pop(cmd.hid(), None)
        if session:
            session.set_result(cmd)

    async def connect(self):
        raise NotImplementedError()

    async def getNodeList(self):
        raise NotImplementedError()

    async def send(self, cmd, sourceEP=0, destEP=0):
        raise NotImplementedError()

    async def sendAndReceive(self, cmd, waitFor, **kwargs):
        await self.send(cmd)
        return await self.waitForMessage(waitFor)

    async def waitForAck(self, ackId, timeout=3):
        if ackId in self._ackQueue:
            raise Exception("Duplicate ackid used!")
        event = asyncio.Event()
        self._ackQueue[ackId] = event
        try:
            await asyncio.wait_for(event.wait(), timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for response")
            del self._ackQueue[ackId]
            raise

    async def waitForMessage(self, msgType, timeout=3):
        hid = msgType.hid()
        session = self._sessions.get(hid, None)
        if not session:
            session = asyncio.get_event_loop().create_future()
            self._sessions[hid] = session
        try:
            await asyncio.wait_for(session, timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for message")
            raise
        return session.result()
