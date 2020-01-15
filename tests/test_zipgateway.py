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

    ackResponse = Zip.ZipPacket.create()
    ackResponse.ackResponse = True
    assert gateway.onMessage(ackResponse.compose()) == True
    gateway.ackReceived.assert_called_once()

    nackResponse = Zip.ZipPacket.create()
    nackResponse.nackResponse = True
    assert gateway.onMessage(nackResponse.compose()) == False

    ackRequest = Zip.ZipPacket.create()
    ackRequest.ackRequest = True
    assert gateway.onMessage(ackRequest.compose()) == False

    pkt = Zip.ZipPacket.create(command=Basic.Get.create())
    assert gateway.onMessage(pkt.compose()) == True
    gateway.commandReceived.assert_called_once()


@pytest.mark.asyncio
async def test_send(gateway: ZIPGateway):
    basicGet = Basic.Get.create()
    [res, _] = await asyncio.gather(
        gateway.send(basicGet), runDelayed(gateway.ackReceived, 1)
    )
    assert res == True


@pytest.mark.asyncio
async def test_send_timeout(gateway: ZIPGateway):
    basicGet = Basic.Get.create()
    assert await gateway.send(basicGet, timeout=0) == False
