# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import asyncio
from unittest.mock import MagicMock

import pytest

from pyzwave.connection import Connection


class DummySock:
    pass


@pytest.fixture
def connection() -> Connection:
    connection = Connection()
    return connection


@pytest.mark.asyncio
async def test_run(connection: Connection):
    async def setEvent(event: asyncio.Future):
        event.set_result(True)

    sockClose = asyncio.Future()
    connection._sock = DummySock()
    connection._sock.close = MagicMock()
    await asyncio.gather(connection.run(sockClose), setEvent(sockClose))
    connection._sock.close.assert_called_once()
