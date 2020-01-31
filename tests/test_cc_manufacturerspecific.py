# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest

from pyzwave.commandclass import ManufacturerSpecific, Version

from test_commandclass import MockNode


@pytest.fixture
def manufacturerSpecific() -> ManufacturerSpecific.ManufacturerSpecific:
    node = MockNode([ManufacturerSpecific.COMMAND_CLASS_MANUFACTURER_SPECIFIC])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=1,
        )
    )
    node.queue(
        ManufacturerSpecific.Report(manufacturerID=1, productTypeID=2, productID=3,)
    )
    return node.supported[ManufacturerSpecific.COMMAND_CLASS_MANUFACTURER_SPECIFIC]


@pytest.mark.asyncio
async def test_interview(
    manufacturerSpecific: ManufacturerSpecific.ManufacturerSpecific,
):
    await manufacturerSpecific.interview()
    assert manufacturerSpecific.manufacturerID == 1
    assert manufacturerSpecific.productTypeID == 2
    assert manufacturerSpecific.productID == 3
