# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=attribute-defined-outside-init

import asyncio
from unittest.mock import MagicMock

import pytest

from pyzwave.connection import Connection


class DummySock:
    pass


@pytest.fixture
def connection() -> Connection:
    connection = Connection()
    sock = DummySock()
    sock.close = MagicMock()
    sock.sendto = MagicMock()
    connection._sock = sock
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
