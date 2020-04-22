# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import asyncio
from unittest.mock import MagicMock
import pytest

from pyzwave.adapter import Adapter, TxOptions
from pyzwave.commandclass import (
    Basic,
    NetworkManagementInclusion,
    NetworkManagementProxy,
    Zip,
)
from pyzwave.message import Message
from pyzwave.types import dsk_t


class AdapterImpl(Adapter):
    def __init__(self):
        super().__init__()
        self.nodeId = 1

    async def addNode(self, txOptions: TxOptions) -> bool:
        return await super().addNode(txOptions)

    async def addNodeDSKSet(
        self, accept: bool, inputDSKLength: int, dsk: dsk_t
    ) -> bool:
        return await super().addNodeDSKSet(accept, inputDSKLength, dsk)

    async def addNodeKeysSet(
        self, grantCSA: bool, accept: bool, grantedKeys: NetworkManagementInclusion.Keys
    ) -> bool:
        return await super().addNodeKeysSet(grantCSA, accept, grantedKeys)

    async def addNodeStop(self) -> bool:
        return await super().addNodeStop()

    async def connect(self):
        await super().connect()

    async def getFailedNodeList(self) -> list:
        return await super().getFailedNodeList()

    async def getMultiChannelCapability(
        self, nodeId: int, endpoint: int
    ) -> NetworkManagementProxy.MultiChannelCapabilityReport:
        return await super().getMultiChannelCapability(nodeId, endpoint)

    async def getMultiChannelEndPoints(self, nodeId: int) -> int:
        return await super().getMultiChannelEndPoints(nodeId)

    async def getNodeInfo(
        self, nodeId: int
    ) -> NetworkManagementProxy.NodeInfoCachedReport:
        return await super().getNodeInfo(nodeId)

    async def getNodeList(self) -> set:
        await super().getNodeList()

    async def removeFailedNode(self, nodeId: int) -> bool:
        return await super().removeFailedNode(nodeId)

    async def removeNode(self) -> bool:
        return await super().removeNode()

    async def removeNodeStop(self) -> bool:
        return await super().removeNodeStop()

    async def send(
        self, cmd: Message, sourceEP: int = 0, destEP: int = 0, timeout: int = 3
    ) -> bool:
        return await super().send(cmd, sourceEP, destEP, timeout)

    async def setNodeInfo(self, generic, specific, cmdClasses):
        await super().setNodeInfo(generic, specific, cmdClasses)


@pytest.fixture
def adapter() -> Adapter:
    return AdapterImpl()


async def runDelayed(func, *args):
    await asyncio.sleep(0)  # Make sure we wait before sending
    return func(*args)


@pytest.mark.asyncio
async def test_ack(adapter: Adapter):
    await asyncio.gather(
        adapter.waitForAck(1), runDelayed(adapter.ackReceived, Zip.ZipPacket(seqNo=1))
    )


@pytest.mark.asyncio
async def test_ack_duplicate(adapter: Adapter):
    with pytest.raises(Exception):
        await asyncio.gather(adapter.waitForAck(1), adapter.waitForAck(1))


@pytest.mark.asyncio
async def test_ack_timeout(adapter: Adapter):
    with pytest.raises(asyncio.TimeoutError):
        await adapter.waitForAck(1, timeout=0)


def test_ack_not_existing(adapter: Adapter):
    assert adapter.ackReceived(Zip.ZipPacket(seqNo=43)) is False


@pytest.mark.asyncio
async def test_addNode(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.addNode(TxOptions.NULL)


@pytest.mark.asyncio
async def test_addNodeDSKSet(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.addNodeDSKSet(True, 0, b"")


@pytest.mark.asyncio
async def test_addNodeKeysSet(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.addNodeKeysSet(False, True, 0)


@pytest.mark.asyncio
async def test_addNodeStop(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.addNodeStop()


def test_commandReceived(adapter: Adapter):
    adapter.messageReceived = MagicMock()
    adapter.commandReceived(Zip.ZipPacket(command=Basic.Report(value=0)))
    adapter.messageReceived.assert_called_once_with(Basic.Report(value=0))


@pytest.mark.asyncio
async def test_connect(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.connect()


@pytest.mark.asyncio
async def test_getFailedNodeList(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.getFailedNodeList()


@pytest.mark.asyncio
async def test_getMultiChannelCapability(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.getMultiChannelCapability(1, 1)


@pytest.mark.asyncio
async def test_getMultiChannelEndPoints(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.getMultiChannelEndPoints(1)


@pytest.mark.asyncio
async def test_getNodeInfo(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.getNodeInfo(1)


@pytest.mark.asyncio
async def test_getNodeList(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.getNodeList()


@pytest.mark.asyncio
async def test_nack_negative_expected_delay(adapter: Adapter):
    async def sendAck():
        await asyncio.sleep(0)
        # pylint: disable=line-too-long
        pkt = b"#\x020\x90\x01\x00\x00\x16\x01\x03\xff\xf9\xc3\x03\x0e\x00\x01\x00\x01\x02\x00\x1a\x02\x05\x00\x00\x00\x00\x02"
        msg = Message.decode(pkt)
        adapter.ackReceived(msg)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        adapter.ackReceived(Zip.ZipPacket(ackResponse=True, seqNo=1))

    await asyncio.gather(adapter.waitForAck(1), sendAck())


def test_nack_not_existing(adapter: Adapter):
    assert (
        adapter.ackReceived(
            Zip.ZipPacket(nackResponse=True, nackWaiting=True, seqNo=43)
        )
        is False
    )


@pytest.mark.asyncio
async def test_nack_waiting(adapter: Adapter):
    async def sendAck():
        await asyncio.sleep(0)
        # pylint: disable=line-too-long
        pkt = b"#\x020\x90\x01\x00\x00\x16\x01\x03\x00\x06=\x03\x0e\x00\x01\x00\x01\x02\x00\x1a\x02\x05\x00\x00\x00\x00\x02"
        msg = Message.decode(pkt)
        adapter.ackReceived(msg)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        adapter.ackReceived(Zip.ZipPacket(ackResponse=True, seqNo=1))

    await asyncio.gather(adapter.waitForAck(1), sendAck())


def test_nodeId(adapter: Adapter):
    assert adapter.nodeId == 1
    adapter.nodeId = 2
    assert adapter.nodeId == 2


@pytest.mark.asyncio
async def test_removeFailedNode(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.removeFailedNode(2)


@pytest.mark.asyncio
async def test_removeNode(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.removeNode()


@pytest.mark.asyncio
async def test_removeNodeStop(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.removeNodeStop()


@pytest.mark.asyncio
async def test_send(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.send(Basic.Get())


@pytest.mark.asyncio
async def test_sendAndReceive(adapter: Adapter):
    async def noop(_):
        pass

    adapter.send = noop  # Throws not implemented as default
    values = await asyncio.gather(
        adapter.sendAndReceive(Basic.Get(), Basic.Report),
        runDelayed(adapter.commandReceived, Basic.Report()),
    )
    assert isinstance(values[0], Basic.Report)


@pytest.mark.asyncio
async def test_sendToNode(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.sendToNode(6, Basic.Get())


@pytest.mark.asyncio
async def test_setNodeInfo(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.setNodeInfo(0, 0, [])


@pytest.mark.asyncio
async def test_waitForMessage(adapter: Adapter):
    await asyncio.gather(
        adapter.waitForMessage(Basic.Get),
        runDelayed(adapter.commandReceived, Basic.Get()),
    )


@pytest.mark.asyncio
async def test_waitForMessage_timeout(adapter: Adapter):
    with pytest.raises(asyncio.TimeoutError):
        await adapter.waitForMessage(Basic.Get, 0)
