# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import asyncio
import sys

import pytest


# We need to mock away dtls since this may segfault if not patched
sys.modules["dtls"] = __import__("mock_dtls")

# pylint: disable=wrong-import-position
from pyzwave.zipgateway import ZIPGateway
from pyzwave.message import Message

from test_zipconnection import DummyConnection, runDelayed


@pytest.fixture
def gateway():
    gateway = ZIPGateway(None, None)
    gateway._conn = DummyConnection()
    return gateway


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
