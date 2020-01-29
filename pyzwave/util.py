# -*- coding: utf-8 -*-

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class Listenable:
    """Inheritable class to implement listaner interface between classes"""

    def __init__(self):
        super().__init__()
        self._listeners = []

    def addListener(self, listener):
        """Add class as listener for messages"""
        self._listeners.append(listener)

    def speak(self, message, *args):
        """Send message to listeners"""
        for listener in self._listeners:
            method = getattr(listener, message, None)
            if not method:
                continue
            try:
                method(self, *args)
            except Exception as error:
                _LOGGER.warning("Error calling listener.%s: %s", message, error)


class MessageWaiter:
    """Inheritable class to implement listening for specific messages"""

    def __init__(self):
        super().__init__()
        self._sessions = {}

    def addWaitingSession(self, msgType):
        """
        Setup the session to wait for _before_ doing the wait. Do this to avoid
        a race condition where the message is received before we wait for it
        """
        hid = msgType.hid()
        session = self._sessions.get(hid, None)
        if not session:
            session = asyncio.get_event_loop().create_future()
            self._sessions[hid] = session
        return session

    def messageReceived(self, message) -> bool:
        """Called when a message is received directed to this node"""
        session = self._sessions.pop(message.hid(), None)
        if session:
            session.set_result(message)
            return True
        return False

    async def waitForMessage(self, msgType, timeout: int = 3):
        """Async method for waiting for a specific message to arrive from the node."""
        session = self.addWaitingSession(msgType)
        try:
            await asyncio.wait_for(session, timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for message %s", msgType)
            raise
        finally:
            self._sessions.pop(msgType.hid(), None)
        return session.result()
