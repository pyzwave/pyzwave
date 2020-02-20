# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import pytest

from pyzwave.commandclass import Meter
from pyzwave.message import Message


@pytest.mark.parametrize(
    "pkt,params",
    [
        (
            "3202A16C00000025000043",
            {
                "rateType": Meter.RateType.IMPORT,
                "deltaTime": 0,
                "meterType": Meter.MeterType.ELECTRIC_METER,
                "meterValue": 0.037,
                "scale": Meter.ElectricMeterScale.A,
            },
        ),
        (
            "3202A26C00000025000043",
            {
                "rateType": Meter.RateType.IMPORT,
                "deltaTime": 0,
                "meterType": Meter.MeterType.GAS_METER,
                "meterValue": 0.037,
                "scale": 5,
            },
        ),
        (
            "3202A16400039299000064",
            {
                "rateType": Meter.RateType.IMPORT,
                "deltaTime": 0,
                "meterType": Meter.MeterType.ELECTRIC_METER,
                "meterValue": 234.137,
                "scale": Meter.ElectricMeterScale.V,
            },
        ),
        (
            "32022134000000600000",
            {
                "rateType": Meter.RateType.IMPORT,
                "meterType": Meter.MeterType.ELECTRIC_METER,
                "deltaTime": 0,
                "meterValue": 9.6,
                "scale": Meter.ElectricMeterScale.W,
            },
        ),
        (
            "3202213400000060",
            {
                "rateType": Meter.RateType.IMPORT,
                "meterType": Meter.MeterType.ELECTRIC_METER,
                "deltaTime": None,  # Not included
                "meterValue": 9.6,
                "scale": Meter.ElectricMeterScale.W,
            },
        ),
    ],
)
def test_decode(pkt, params):
    msg = Message.decode(bytes.fromhex(pkt))
    for key, value in params.items():
        msgValue = getattr(msg, key)
        assert msgValue == value
