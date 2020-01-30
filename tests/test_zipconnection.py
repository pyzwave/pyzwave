# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=singleton-comparison

import asyncio
import sys
from unittest.mock import MagicMock, patch

import pytest

from pyzwave.message import Message
from pyzwave.commandclass import Basic, Zip, ZipND

# We need to mock away dtls since this may segfault if not patched
sys.modules["dtls"] = __import__("mock_dtls")
from pyzwave.zipconnection import ZIPConnection  # pylint: disable=wrong-import-position


class ZIPConnectionImpl(ZIPConnection):
    async def getNodeList(self) -> set:
        await super().getNodeList()


async def runDelayed(func, *args):
    await asyncio.sleep(0)  # Make sure we wait before sending
    return func(*args)


class DummyConnection:
    async def connect(self, address, psk):
        pass

    async def listen(self, psk, port):
        pass

    def send(self, msg):
        pass


@pytest.fixture
def connection() -> ZIPConnection:
    connection = ZIPConnectionImpl(None, None)
    connection._conn = DummyConnection()
    connection._conn.send = MagicMock()
    return connection


@pytest.mark.asyncio
async def test_connect(connection: ZIPConnection):
    await connection.connect()


@pytest.mark.asyncio
async def test_getFailedNodeList(connection: ZIPConnection):
    with pytest.raises(NotImplementedError):
        await connection.getFailedNodeList()


@pytest.mark.asyncio
async def test_getNodeInfo(connection: ZIPConnection):
    with pytest.raises(NotImplementedError):
        await connection.getNodeInfo(1)


@pytest.mark.asyncio
async def test_getNodeList(connection: ZIPConnection):
    with pytest.raises(NotImplementedError):
        await connection.getNodeList()


def test_onPacket(connection: ZIPConnection):
    assert connection.onPacket(b"malformed") is False


def test_onPacket_Zip(connection: ZIPConnection):
    connection.ackReceived = MagicMock()
    connection.commandReceived = MagicMock()

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
    assert connection.onPacket(ackResponse.compose()) is True
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

    assert connection.onPacket(nackResponse.compose()) is False

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
    assert connection.onPacket(ackRequest.compose()) is False

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
    assert connection.onPacket(pkt.compose()) is True
    connection.commandReceived.assert_called_once()


def test_onPacket_ZipND(connection: ZIPConnection):
    pkt = ZipND.ZipNodeAdvertisement(
        local=False, validity=0, nodeId=6, ipv6=0, homeId=0,
    )
    assert connection.onPacket(pkt.compose()) is True

    pkt = Zip.ZipKeepAlive(ackRequest=True, ackResponse=False)
    assert connection.onPacket(pkt.compose()) is False

    pkt = Zip.ZipKeepAlive(ackRequest=False, ackResponse=True)
    assert connection.onPacket(pkt.compose()) is True


def test_keepAlive(connection: ZIPConnection):
    connection.keepAlive()
    connection._conn.send.assert_called_with(b"#\x03\x80")


def test_psk():
    psk = b"Foobar"
    connection = ZIPConnectionImpl(None, psk)
    assert connection.psk == psk


def test_resetKeepAlive(connection: ZIPConnection):
    with patch.object(asyncio.TimerHandle, "cancel"):
        assert connection._keepAlive is None
        connection.resetKeepAlive()
        assert connection._keepAlive is not None
        timer = connection._keepAlive
        connection.resetKeepAlive()
        timer.cancel.assert_called_once()
        assert connection._keepAlive != timer


@pytest.mark.asyncio
async def test_send(connection: ZIPConnection):
    connection._conn.send = MagicMock()
    basicGet = Basic.Get()
    [res, _] = await asyncio.gather(
        connection.send(basicGet), runDelayed(connection.ackReceived, 1)
    )
    assert res is True
    connection._conn.send.assert_called_once_with(b"#\x02\x80\x50\x01\x00\x00 \x02")


@pytest.mark.asyncio
async def test_send_timeout(connection: ZIPConnection):
    basicGet = Basic.Get()
    assert await connection.send(basicGet, timeout=0) is False


@pytest.mark.asyncio
async def test_setNodeInfo(connection: ZIPConnection):
    with pytest.raises(NotImplementedError):
        await connection.setNodeInfo(0, 0, [])
