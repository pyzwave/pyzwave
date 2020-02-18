# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=attribute-defined-outside-init

import asyncio
from unittest.mock import MagicMock

import pytest

from pyzwave.connection import Connection, ZipClientProtocol


@pytest.fixture
def connection() -> Connection:
    connection = Connection()
    connection._sock = MagicMock()
    return connection


@pytest.fixture
def protocol() -> ZipClientProtocol:
    return ZipClientProtocol(MagicMock(), MagicMock())


@pytest.mark.asyncio
async def test_connect(connection: Connection):
    async def run(_):
        pass

    connection.run = run
    await connection.connect(None, None)
    assert isinstance(connection._sock, asyncio.Transport)


@pytest.mark.asyncio
async def test_run(connection: Connection):
    async def setEvent(event: asyncio.Future):
        event.set_result(True)

    sockClose = asyncio.Future()
    await asyncio.gather(connection.run(sockClose), setEvent(sockClose))
    connection._sock.close.assert_called_once()


def test_send(connection: Connection):
    pkt = b"\xde\xad\xbe\xef"
    assert connection.send(pkt) is True
    connection._sock.sendto.assert_called_once_with(pkt)
    connection._sock = None
    assert connection.send(pkt) is False


def test_sendTo(connection: Connection):
    pkt = b"\xde\xad\xbe\xef"
    connection.sendTo(pkt, "::1")
    connection._sock.sendto.assert_called_once_with(pkt, "::1")


def test_stop(connection: Connection):
    connection._running = True
    connection.stop()
    assert connection._running is False
    connection._sock.close.assert_called_once()


def test_ZipClientProtocol_connection_made(protocol: ZipClientProtocol):
    assert protocol.transport is None
    protocol.connection_made(42)
    assert protocol.transport == 42


def test_ZipClientProtocol_datagram_received(protocol: ZipClientProtocol):
    protocol.datagram_received("Foo", "::1")
    protocol.onMessage.assert_called_once_with("Foo", "::1")


def test_ZipClientProtocol_error_received(protocol: ZipClientProtocol):
    # Change this test once the function is implemented
    assert protocol.error_received("Too bad for you") is None


def test_ZipClientProtocol_onConLost():
    onConLost = asyncio.get_event_loop().create_future()
    protocol = ZipClientProtocol(onConLost, None)
    assert onConLost.done() is False
    protocol.connection_lost(None)
    assert onConLost.done() is True
