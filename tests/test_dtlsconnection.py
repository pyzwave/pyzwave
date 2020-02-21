# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=attribute-defined-outside-init

import pytest

from pyzwave.dtlsconnection import DTLSConnection


@pytest.fixture
def dtlsconnection() -> DTLSConnection:
    connection = DTLSConnection()
    return connection


@pytest.mark.asyncio
async def test_connect(dtlsconnection: DTLSConnection):
    def start():
        dtlsconnection._connectionEvent.set()

    dtlsconnection.start = start
    await dtlsconnection.connect(None, None)


def test_stop(dtlsconnection: DTLSConnection):
    dtlsconnection._running = True
    dtlsconnection.stop()
    assert dtlsconnection._running is False
