# -*- coding: utf-8 -*-

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class ZipClientProtocol:
    """Internal ZIP Client protocol implementation"""

    def __init__(self, onConLost, onMessage):
        self.onConLost = onConLost
        self.onMessage = onMessage
        self.transport = None

    def connection_made(self, transport):  # pylint: disable=invalid-name
        """Called when a new connection is made"""
        self.transport = transport

    def datagram_received(self, data, addr):  # pylint: disable=invalid-name
        """Called when a new udp packet has arrived"""
        self.onMessage(data, addr)

    def error_received(self, exc):  # pylint: disable=invalid-name,no-self-use
        """Called when error happens"""
        _LOGGER.error("Error received: %s", exc)

    def connection_lost(self, exc):  # pylint: disable=invalid-name
        """Called when connection is lost"""
        _LOGGER.warning("Connection closed %s", exc)
        self.onConLost.set_result(True)


class Connection:
    """Connection object to create a non encrypted connection using PSK"""

    def __init__(self):
        super().__init__()
        self._address = None
        self._psk = None
        self._running = False
        self._sock = None
        self._onMessage = None
        self._server = False

    async def connect(self, address, psk):
        """Connect to remote using psk"""
        self._address = address
        self._psk = psk

        loop = asyncio.get_event_loop()
        onConLost = loop.create_future()
        self._sock, _protocol = await loop.create_datagram_endpoint(
            lambda: ZipClientProtocol(onConLost, self._msgReceived),
            remote_addr=(self._address, 4123),
        )
        asyncio.ensure_future(self.run(onConLost))

    async def listen(self, psk, port):
        """Start server socket"""
        self._server = True
        self._psk = psk
        loop = asyncio.get_event_loop()
        onConLost = loop.create_future()
        self._sock, _protocol = await loop.create_datagram_endpoint(
            lambda: ZipClientProtocol(onConLost, self._msgReceived),
            local_addr=("::", port),
        )

    async def run(self, onConLost):  # pylint: disable=missing-function-docstring
        try:
            await onConLost
        finally:
            self._sock.close()

    def send(self, msg) -> bool:
        """Send bytes to socket"""
        if not self._sock:
            _LOGGER.error("Could not send, not yet connected!")
            return False
        self._sock.sendto(msg)
        return True

    def sendTo(self, msg, address) -> bool:
        """Send bytes to address"""
        self._sock.sendto(msg, address)

    def onMessage(self, cbfn):
        """Set the callback function to use when data has arrived"""
        self._onMessage = cbfn

    def stop(self):
        """Stop the thread"""
        self._running = False
        self._sock.close()

    def _msgReceived(self, msg, sender):
        if not self._onMessage:
            return
        if self._server:
            self._onMessage(msg, sender)
        else:
            self._onMessage(msg)
