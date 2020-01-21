# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import asyncio
import pytest

from pyzwave.adapter import Adapter
from pyzwave.commandclass import Basic


class AdapterImpl(Adapter):
    async def connect(self):
        await super().connect()


@pytest.fixture
def adapter() -> Adapter:
    return AdapterImpl()


async def runDelayed(func, *args):
    await asyncio.sleep(0)  # Make sure we wait before sending
    return func(*args)


@pytest.mark.asyncio
async def test_ack(adapter: Adapter):
    await asyncio.gather(adapter.waitForAck(1), runDelayed(adapter.ackReceived, 1))


@pytest.mark.asyncio
async def test_ack_duplicate(adapter: Adapter):
    with pytest.raises(Exception):
        await asyncio.gather(adapter.waitForAck(1), adapter.waitForAck(1))


@pytest.mark.asyncio
async def test_ack_timeout(adapter: Adapter):
    with pytest.raises(asyncio.TimeoutError):
        await adapter.waitForAck(1, timeout=0)


def test_ack_not_existing(adapter: Adapter):
    assert adapter.ackReceived(43) is False


@pytest.mark.asyncio
async def test_connect(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.connect()


@pytest.mark.asyncio
async def test_getNodeList(adapter: Adapter):
    with pytest.raises(NotImplementedError):
        await adapter.getNodeList()


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
async def test_waitForMessage(adapter: Adapter):
    await asyncio.gather(
        adapter.waitForMessage(Basic.Get),
        runDelayed(adapter.commandReceived, Basic.Get()),
    )


@pytest.mark.asyncio
async def test_waitForMessage_timeout(adapter: Adapter):
    with pytest.raises(asyncio.TimeoutError):
        await adapter.waitForMessage(Basic.Get, 0)
