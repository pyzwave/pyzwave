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


def test_stop(connection: Connection):
    connection._running = True
    connection.stop()
    assert connection._running is False
    connection._sock.close.assert_called_once()


def test_ZipClientProtocol_onConLost():
    onConLost = asyncio.get_event_loop().create_future()
    protocol = ZipClientProtocol(onConLost, None)
    assert onConLost.done() is False
    protocol.connection_lost(None)
    assert onConLost.done() is True
