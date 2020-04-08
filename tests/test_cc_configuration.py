# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import pytest

from pyzwave.commandclass import Configuration
from pyzwave.message import Message

from test_commandclass import MockNode


@pytest.fixture
def configuration() -> Configuration.Configuration:
    node = MockNode([Configuration.COMMAND_CLASS_CONFIGURATION])
    node.queue(Configuration.Report(value=42))
    return node.supported[Configuration.COMMAND_CLASS_CONFIGURATION]


@pytest.mark.asyncio
async def test_Configuration_get_cached(configuration: Configuration.Configuration):
    configuration.parameters[1] = Configuration.ConfigurationValue(value=42)
    assert await configuration.get(1) == 42
    configuration.node.assert_message_not_sent(Configuration.Get)


@pytest.mark.asyncio
async def test_Configuration_get_force_non_cached(
    configuration: Configuration.Configuration,
):
    configuration.parameters[1] = Configuration.ConfigurationValue(value=42)
    assert await configuration.get(1, cached=False) == 42
    configuration.node.assert_message_sent(Configuration.Get)


@pytest.mark.asyncio
async def test_Configuration_get_non_cached(configuration: Configuration.Configuration):
    assert await configuration.get(1) == 42
    configuration.node.assert_message_sent(Configuration.Get)


@pytest.mark.asyncio
async def test_Configuration_report(configuration: Configuration.Configuration):
    await configuration.node.handleMessage(
        Configuration.Report(parameterNumber=2, size=2, value=1234)
    )
    assert configuration.parameters[2].size == 2
    assert configuration.parameters[2].value == 1234


@pytest.mark.asyncio
async def test_Configuration_set(configuration: Configuration.Configuration):
    await configuration.set(1, 1, 42)
    configuration.node.assert_message_sent(Configuration.Set)


def test_Report():
    pkt = b"\x70\x06\x01\x01\x09"
    msg = Message.decode(pkt)
    assert isinstance(msg, Configuration.Report)
    assert msg.parameterNumber == 1
    assert msg.size == 1
    assert msg.value == 9


def test_Set():
    msg = Configuration.Set(parameterNumber=1, default=False, size=1, value=0x42)
    assert msg.compose() == b"\x70\x04\x01\x01\x42"
    msg = Configuration.Set(parameterNumber=1, default=False, size=2, value=0x1234)
    assert msg.compose() == b"\x70\x04\x01\x02\x12\x34"
    msg = Configuration.Set(parameterNumber=1, default=False, size=4, value=0x12345678)
    assert msg.compose() == b"\x70\x04\x01\x04\x12\x34\x56\x78"
