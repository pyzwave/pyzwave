# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=singleton-comparison

import asyncio
import ipaddress
import sys
from unittest.mock import MagicMock

import pytest


# We need to mock away dtls since this may segfault if not patched
sys.modules["dtls"] = __import__("mock_dtls")

# pylint: disable=wrong-import-position
from pyzwave.zipgateway import ZIPGateway
from pyzwave.message import Message
from pyzwave.commandclass import Basic
import pyzwave.zipconnection

from test_zipconnection import DummyConnection, runDelayed, ZIPConnectionImpl


class DummyDTLSConnection:
    async def connect(self, address, psk):
        pass

    def onMessage(self, func):
        pass


pyzwave.zipconnection.DTLSConnection = DummyDTLSConnection


@pytest.fixture
def gateway():
    gateway = ZIPGateway(None, None)
    gateway._conn = DummyConnection()
    gateway._connections[6] = ZIPConnectionImpl(None, None)
    gateway._connections[6]._conn.send = MagicMock()
    return gateway


@pytest.mark.asyncio
async def test_connectoToNode(gateway: ZIPGateway):
    async def ipOfNode(_nodeId):
        return ipaddress.IPv6Address("::ffff:c0a8:ee")

    gateway.ipOfNode = ipOfNode
    assert 2 not in gateway._connections
    assert await gateway.connectToNode(2)
    assert 2 in gateway._connections


@pytest.mark.asyncio
async def test_getNodeList(gateway: ZIPGateway):
    # pylint: disable=line-too-long
    nodeListReport = Message.decode(
        b"R\x02\x02\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )

    async def dummySend(_msg):
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


@pytest.mark.asyncio
async def test_ipOfNode(gateway: ZIPGateway):
    # pylint: disable=line-too-long
    pkt = b"X\x01\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xc0\xa8\x00\xee\xea\xec\xfa\xf9"
    zipNodeAdvertisement = Message.decode(pkt)
    [reply, _] = await asyncio.gather(
        gateway.ipOfNode(6), runDelayed(gateway.commandReceived, zipNodeAdvertisement)
    )
    assert reply == ipaddress.IPv6Address("::ffff:c0a8:ee")


@pytest.mark.asyncio
async def test_sendToNode(gateway: ZIPGateway):
    connection = await gateway.connectToNode(6)
    [res, _] = await asyncio.gather(
        gateway.sendToNode(6, Basic.Get()), runDelayed(connection.ackReceived, 1)
    )
    assert res == True


@pytest.mark.asyncio
async def test_setNodeInfo(gateway: ZIPGateway):
    with pytest.raises(NotImplementedError):
        await gateway.setNodeInfo(0, 0, [])
