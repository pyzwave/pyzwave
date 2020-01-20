import asyncio
import pytest
from unittest.mock import MagicMock

from pyzwave.zipgateway import ZIPGateway
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
def gateway():
    gateway = ZIPGateway()
    gateway._conn = DummyConnection()
    return gateway


@pytest.mark.asyncio
async def test_connect(gateway: ZIPGateway):
    await gateway.connect("127.0.0.1", "123456789")


@pytest.mark.asyncio
async def test_getNodeList(gateway: ZIPGateway):
    nodeListReport = Message.decode(
        b"R\x02\x02\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )

    async def dummySend(msg):
        pass

    gateway.send = dummySend
    [nodeList, _] = await asyncio.gather(
        gateway.getNodeList(), runDelayed(gateway.commandReceived, nodeListReport)
    )
    assert nodeList == {1, 6}


@pytest.mark.asyncio
async def test_getNodeList_timeout(gateway: ZIPGateway):
    async def dummySendAndReceive(msg, waitFor):
        raise asyncio.TimeoutError()

    gateway.sendAndReceive = dummySendAndReceive
    nodeList = await gateway.getNodeList()
    assert nodeList == {}


def test_onMessage(gateway: ZIPGateway):
    gateway.ackReceived = MagicMock()
    gateway.commandReceived = MagicMock()

    assert gateway.onMessage(b"malformed") == False

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
    assert gateway.onMessage(ackResponse.compose()) == True
    gateway.ackReceived.assert_called_once()

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

    assert gateway.onMessage(nackResponse.compose()) == False

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
    assert gateway.onMessage(ackRequest.compose()) == False

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
    assert gateway.onMessage(pkt.compose()) == True
    gateway.commandReceived.assert_called_once()


@pytest.mark.asyncio
async def test_send(gateway: ZIPGateway):
    basicGet = Basic.Get()
    [res, _] = await asyncio.gather(
        gateway.send(basicGet), runDelayed(gateway.ackReceived, 1)
    )
    assert res == True


@pytest.mark.asyncio
async def test_send_timeout(gateway: ZIPGateway):
    basicGet = Basic.Get()
    assert await gateway.send(basicGet, timeout=0) == False
