# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
from unittest.mock import MagicMock
import pytest

from pyzwave.commandclass import SensorMultilevel, Version
from pyzwave.message import Message
from pyzwave.types import float_t

from test_commandclass import MockNode


@pytest.fixture
def multilevelSensor() -> SensorMultilevel.SensorMultilevel:
    node = MockNode([SensorMultilevel.COMMAND_CLASS_SENSOR_MULTILEVEL])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=SensorMultilevel.COMMAND_CLASS_SENSOR_MULTILEVEL,
            commandClassVersion=5,
        )
    )
    node.queue(SensorMultilevel.SupportedSensorReport(bitMask=[1]))
    node.queue(SensorMultilevel.SupportedScaleReport(sensorType=1, scaleBitMask=3))
    return node.supported[SensorMultilevel.COMMAND_CLASS_SENSOR_MULTILEVEL]


@pytest.mark.asyncio
async def test_interview(multilevelSensor: SensorMultilevel.SensorMultilevel):
    await multilevelSensor.interview()
    multilevelSensor.node.assert_message_sent(SensorMultilevel.SupportedGetSensor())
    multilevelSensor.node.assert_message_sent(SensorMultilevel.SupportedGetScale)
    assert multilevelSensor.supportedTypes == {1: 3}


@pytest.mark.asyncio
async def test_interview_v4(multilevelSensor: SensorMultilevel.SensorMultilevel):
    multilevelSensor._version = 4
    await multilevelSensor.interview()
    multilevelSensor.node.assert_message_not_sent(SensorMultilevel.SupportedGetSensor())


@pytest.mark.asyncio
async def test_report_v4(multilevelSensor: SensorMultilevel.SensorMultilevel):
    multilevelSensor._version = 4
    listener = MagicMock()
    listener.onReport.return_value = False
    multilevelSensor.addListener(listener)
    assert (
        await multilevelSensor.handleMessage(
            SensorMultilevel.Report(sensorType=1, sensorValue=float_t(10, 1, 0)), 0
        )
        is False
    )
    listener.onReport.assert_called_once()


@pytest.mark.parametrize(
    "valueFilter,value,result",
    [
        ({1: 3}, (1, 23.2, 1, 0), True),
        ({2: 3}, (1, 23.2, 1, 0), False),
        ({1: 4}, (1, 23.2, 1, 0), False),
    ],
)
@pytest.mark.asyncio
async def test_report(
    valueFilter, value, result, multilevelSensor: SensorMultilevel.SensorMultilevel
):
    multilevelSensor._version = 5
    multilevelSensor.supportedTypes = valueFilter
    listener = MagicMock()
    listener.onReport.return_value = False
    multilevelSensor.addListener(listener)
    assert (
        await multilevelSensor.handleMessage(
            SensorMultilevel.Report(
                sensorType=value[0], sensorValue=float_t(*value[1:])
            ),
            0,
        )
        is not result  # The output from handleMessage is inverted from __report__
    )
    if result:
        # Make sure message IS propagated
        listener.onReport.assert_called_once()
    else:
        # Make sure message is NOT propagated
        listener.onReport.assert_not_called()


def test_SupportedSensorReport():
    msg = Message.decode(b"\x31\x02\x01")
    assert msg.bitMask == set([1])
    msg = Message.decode(b"\x31\x02\x05")
    assert msg.bitMask == set([1, 3])
