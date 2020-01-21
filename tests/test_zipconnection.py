import asyncio
import pytest
from unittest.mock import MagicMock

import sys

# We need to mock away dtls since this may segfault if not patched
sys.modules["dtls"] = __import__("mock_dtls")

from pyzwave.zipconnection import ZIPConnection
from pyzwave.message import Message
from pyzwave.commandclass import Zip, Basic


async def runDelayed(func, *args):
    await asyncio.sleep(0)  # Make sure we wait before sending
    return func(*args)


class DummyConnection:
    async def connect(self, address, psk):
        pass

    def send(self, msg):
        pass


@pytest.fixture
def connection() -> ZIPConnection:
    connection = ZIPConnection()
    connection._conn = DummyConnection()
    return connection


@pytest.mark.asyncio
async def test_connect(connection: ZIPConnection):
    await connection.connect("127.0.0.1", "123456789")


def test_onMessage(connection: ZIPConnection):
    connection.ackReceived = MagicMock()
    connection.commandReceived = MagicMock()

    assert connection.onMessage(b"malformed") == False

    ackResponse = Zip.ZipPacket(
        ackRequest=False,
        ackResponse=True,
        nackResponse=False,
        nackWaiting=False,
        nackQueueFull=False,
        nackOptionError=False,
        headerExtIncluded=False,
        zwCmdIncluded=False,
        moreInformation=False,
        secureOrigin=True,
        seqNo=0,
        sourceEP=0,
        destEP=0,
        command=None,
    )
    assert connection.onMessage(ackResponse.compose()) == True
    connection.ackReceived.assert_called_once()

    nackResponse = Zip.ZipPacket(
        ackRequest=False,
        ackResponse=False,
        nackResponse=True,
        nackWaiting=False,
        nackQueueFull=False,
        nackOptionError=False,
        headerExtIncluded=False,
        zwCmdIncluded=False,
        moreInformation=False,
        secureOrigin=True,
        seqNo=0,
        sourceEP=0,
        destEP=0,
        command=None,
    )
    msg = Message.decode(nackResponse.compose())
    assert msg.ackRequest == False
    assert msg.ackResponse == False
    assert msg.nackResponse == True

    assert connection.onMessage(nackResponse.compose()) == False

    ackRequest = Zip.ZipPacket(
        ackRequest=True,
        ackResponse=False,
        nackResponse=False,
        nackWaiting=False,
        nackQueueFull=False,
        nackOptionError=False,
        headerExtIncluded=False,
        zwCmdIncluded=False,
        moreInformation=False,
        secureOrigin=True,
        seqNo=0,
        sourceEP=0,
        destEP=0,
        command=None,
    )
    assert connection.onMessage(ackRequest.compose()) == False

    pkt = Zip.ZipPacket(
        ackRequest=False,
        ackResponse=False,
        nackResponse=False,
        nackWaiting=False,
        nackQueueFull=False,
        nackOptionError=False,
        headerExtIncluded=False,
        zwCmdIncluded=True,
        moreInformation=False,
        secureOrigin=True,
        seqNo=0,
        sourceEP=0,
        destEP=0,
        command=Basic.Get(),
    )
    assert connection.onMessage(pkt.compose()) == True
    connection.commandReceived.assert_called_once()


@pytest.mark.asyncio
async def test_send(connection: ZIPConnection):
    connection._conn.send = MagicMock()
    basicGet = Basic.Get()
    [res, _] = await asyncio.gather(
        connection.send(basicGet), runDelayed(connection.ackReceived, 1)
    )
    assert res == True
    connection._conn.send.assert_called_once_with(b"#\x02\x80\x50\x01\x00\x00 \x02")


@pytest.mark.asyncio
async def test_send_timeout(connection: ZIPConnection):
    basicGet = Basic.Get()
    assert await connection.send(basicGet, timeout=0) == False
