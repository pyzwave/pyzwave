# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=singleton-comparison
# pylint: disable=attribute-defined-outside-init

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
from pyzwave.commandclass import (
    Basic,
    SwitchBinary,
    NetworkManagementProxy,
    Zip,
    ZipGateway,
    ZipND,
)
from pyzwave.types import IPv6
import pyzwave.zipconnection

from test_zipconnection import DummyConnection, runDelayed, ZIPConnectionImpl


class DummyDTLSConnection:
    async def connect(self, address, psk):
        pass

    def onMessage(self, func):
        pass


pyzwave.zipconnection.DTLSConnection = DummyDTLSConnection
pyzwave.zipconnection.Connection = DummyDTLSConnection


class ZIPGatewayTester(ZIPGateway):
    async def waitForAck(self, ackId: int, timeout: int = 3):
        # Auto ack all messages during testing
        return


class Listener:
    pass


@pytest.fixture
def gateway():
    gateway = ZIPGatewayTester(None, None)
    gateway.listener = Listener
    gateway.listener.messageReceived = MagicMock()
    gateway.addListener(gateway.listener)
    gateway._unsolicitedConnection = DummyConnection()
    gateway._conn = DummyConnection()
    gateway._connections[6] = ZIPConnectionImpl(None, None)
    gateway._connections[6]._conn.send = MagicMock()
    return gateway


async def ipOfNode(_nodeId):
    return ipaddress.IPv6Address("::ffff:c0a8:ee")


async def sendNop(_msg):
    pass


async def sendAndReceiveTimeout(msg, waitFor):
    raise asyncio.TimeoutError()


@pytest.mark.asyncio
async def test_connect(gateway: ZIPGateway):
    gateway._nodes = {1: {}, 2: {}}
    gateway.ipOfNode = ipOfNode

    async def runScript():
        await asyncio.sleep(0)
        gateway.commandReceived(ZipGateway.GatewayModeReport(mode=2))

    await asyncio.gather(gateway.connect(), runScript())


@pytest.mark.asyncio
async def test_connectToNode(gateway: ZIPGateway):
    gateway.ipOfNode = ipOfNode
    assert 2 not in gateway._connections
    assert await gateway.connectToNode(2)
    assert 2 in gateway._connections


@pytest.mark.asyncio
async def test_getFailedNodeList(gateway: ZIPGateway):
    # pylint: disable=line-too-long
    failedNodeListReport = Message.decode(
        b"R\x0C\x02!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )

    gateway.send = sendNop
    [nodeList, _] = await asyncio.gather(
        gateway.getFailedNodeList(),
        runDelayed(gateway.commandReceived, failedNodeListReport),
    )
    assert nodeList == {1, 6}


@pytest.mark.asyncio
async def test_getFailedNodeList_timeout(gateway: ZIPGateway):
    gateway.sendAndReceive = sendAndReceiveTimeout
    nodeList = await gateway.getFailedNodeList()
    assert nodeList == set()


@pytest.mark.asyncio
async def test_getMultiChannelCapability(gateway: ZIPGateway):
    gateway.send = sendNop
    [report, _] = await asyncio.gather(
        gateway.getMultiChannelCapability(1, 1),
        runDelayed(
            gateway.commandReceived,
            NetworkManagementProxy.MultiChannelCapabilityReport(),
        ),
    )
    assert isinstance(report, NetworkManagementProxy.MultiChannelCapabilityReport)


@pytest.mark.asyncio
async def test_getMultiChannelCapability_timeout(gateway: ZIPGateway):
    gateway.sendAndReceive = sendAndReceiveTimeout
    report = await gateway.getMultiChannelCapability(1, 1)
    assert isinstance(report, NetworkManagementProxy.MultiChannelCapabilityReport)


@pytest.mark.asyncio
async def test_getMultiChannelEndPoints(gateway: ZIPGateway):
    gateway.send = sendNop
    [endpoints, _] = await asyncio.gather(
        gateway.getMultiChannelEndPoints(1),
        runDelayed(
            gateway.commandReceived,
            NetworkManagementProxy.MultiChannelEndPointReport(
                individualEndPoints=2, aggregatedEndPoints=0
            ),
        ),
    )
    assert endpoints == 2


@pytest.mark.asyncio
async def test_getMultiChannelEndPoints_timeout(gateway: ZIPGateway):
    gateway.sendAndReceive = sendAndReceiveTimeout
    assert await gateway.getMultiChannelEndPoints(1) == 0


@pytest.mark.asyncio
async def test_getNodeInfo(gateway: ZIPGateway):
    # pylint: disable=line-too-long
    cachedNodeInfoReport = Message.decode(
        b"R\x04\x03\x1b\x9c\x9c\x00\x04\x10\x01^%'\x85\\pru\x86ZYszh#"
    )

    gateway.send = sendNop
    [nodeInfo, _] = await asyncio.gather(
        gateway.getNodeInfo(1),
        runDelayed(gateway.commandReceived, cachedNodeInfoReport),
    )
    assert isinstance(nodeInfo, NetworkManagementProxy.NodeInfoCachedReport)
    assert nodeInfo == cachedNodeInfoReport


@pytest.mark.asyncio
async def test_getNodeInfo_timeout(gateway: ZIPGateway):
    gateway.sendAndReceive = sendAndReceiveTimeout
    nodeInfo = await gateway.getNodeInfo(1)
    assert isinstance(nodeInfo, NetworkManagementProxy.NodeInfoCachedReport)


@pytest.mark.asyncio
async def test_getNodeList(gateway: ZIPGateway):
    # pylint: disable=line-too-long
    nodeListReport = Message.decode(
        b"R\x02\x02\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )

    async def dummySend(_msg):
        pass

    gateway.send = dummySend
    assert gateway.nodeId == 0
    [nodeList, _] = await asyncio.gather(
        gateway.getNodeList(), runDelayed(gateway.commandReceived, nodeListReport)
    )
    assert nodeList == {1, 6}
    assert gateway._nodes == {1: {}, 6: {}}
    assert gateway.nodeId == 1


@pytest.mark.asyncio
async def test_getNodeList_cached(gateway: ZIPGateway):
    gateway._nodes = {1: {}, 2: {}}
    assert await gateway.getNodeList() == {1, 2}


@pytest.mark.asyncio
async def test_getNodeList_timeout(gateway: ZIPGateway):
    gateway.sendAndReceive = sendAndReceiveTimeout
    nodeList = await gateway.getNodeList()
    assert nodeList == set()


@pytest.mark.asyncio
async def test_handleNodeListReport(gateway: ZIPGateway):
    async def ipOfNode(_):
        return ipaddress.IPv6Address("::1")

    listener = MagicMock()
    gateway.ipOfNode = ipOfNode
    gateway.addListener(listener)
    gateway._nodes = {
        1: {"ip": ipaddress.IPv6Address("::1")},
        2: {"ip": ipaddress.IPv6Address("::1")},
    }
    # pylint: disable=line-too-long
    zipPkt = b"#\x02@\x10\x00\x00\x00R\x02\x02\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    future = gateway.onUnsolicitedMessage(zipPkt, ("::1",))
    await asyncio.gather(future)
    assert gateway._nodes == {
        1: {"ip": ipaddress.IPv6Address("::1")},
        6: {"ip": ipaddress.IPv6Address("::1")},
    }
    listener.nodeListUpdated.assert_called_once()


@pytest.mark.asyncio
async def test_ipOfNode(gateway: ZIPGateway):
    # pylint: disable=line-too-long
    pkt = b"X\x01\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xc0\xa8\x00\xee\xea\xec\xfa\xf9"
    zipNodeAdvertisement = Message.decode(pkt)
    [reply, _] = await asyncio.gather(
        gateway.ipOfNode(6), runDelayed(gateway.commandReceived, zipNodeAdvertisement)
    )
    assert reply == ipaddress.IPv6Address("::ffff:c0a8:ee")


def test_onMessageReceived(gateway: ZIPGateway):
    connection = DummyConnection()
    msg = Basic.Get()
    gateway._connections = {2: connection}
    gateway.onMessageReceived(connection, Zip.ZipPacket(sourceEP=0, command=msg))
    gateway.listener.messageReceived.assert_called_once_with(gateway, 2, 0, msg, 0)


def test_onMessageReceived_noNode(gateway: ZIPGateway):
    gateway._connections = {2: DummyConnection()}
    gateway.onMessageReceived(DummyConnection(), Basic.Get())
    gateway.listener.messageReceived.assert_not_called()


def test_onUnsolicitedMessage(gateway: ZIPGateway):
    ip = ipaddress.IPv6Address("::ffff:c0a8:ee")
    gateway._nodes = {7: {"ip": ip}}
    pkt = b"#\x02\x00\xc0\xf9\x00\x00\x05\x84\x02\x00\x00%\x03\x00"
    assert gateway.onUnsolicitedMessage(pkt, (ip,)) is True
    gateway.listener.messageReceived.assert_called_once_with(
        gateway, 7, 0, SwitchBinary.Report(value=0), 0
    )


def test_onUnsolicitedMessage_unknownNode(gateway: ZIPGateway):
    ip = ipaddress.IPv6Address("::ffff:c0a8:ee")
    pkt = b"#\x02\x00\xc0\xf9\x00\x00\x05\x84\x02\x00\x00%\x03\x00"
    assert gateway.onUnsolicitedMessage(pkt, (ip,)) is False
    gateway.listener.messageReceived.assert_not_called()


@pytest.mark.asyncio
async def test_sendToNode(gateway: ZIPGateway):
    connection = await gateway.connectToNode(6)
    [res, _] = await asyncio.gather(
        gateway.sendToNode(6, Basic.Get()), runDelayed(connection.ackReceived, 1)
    )
    assert res == True


@pytest.mark.asyncio
async def test_setGatewayMode(gateway: ZIPGateway):
    async def runScript():
        await asyncio.sleep(0)
        gateway.commandReceived(ZipGateway.GatewayModeReport(mode=2))

    (retval, _) = await asyncio.gather(gateway.setGatewayMode(1), runScript())
    assert retval is True


@pytest.mark.asyncio
async def test_setGatewayMode_timeout(gateway: ZIPGateway):
    assert await gateway.setGatewayMode(1, timeout=0) == False


@pytest.mark.asyncio
async def test_setNodeInfo(gateway: ZIPGateway):
    with pytest.raises(NotImplementedError):
        await gateway.setNodeInfo(0, 0, [])


@pytest.mark.asyncio
async def test_setupUnsolicitedConnection(gateway: ZIPGateway):
    gateway._nodes = {1: {}}
    await asyncio.gather(
        gateway.setupUnsolicitedConnection(),
        runDelayed(
            gateway.commandReceived,
            ZipND.ZipNodeAdvertisement(
                local=False,
                validity=0,
                nodeId=1,
                ipv6=ipaddress.IPv6Address("2001:db8::1"),
                homeId=0x12345678,
            ),
        ),
    )
    assert gateway._nodes == {1: {"ip": IPv6("2001:db8::1")}}
