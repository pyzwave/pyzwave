# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest

from pyzwave.commandclass import Version, ZwavePlusInfo

from test_commandclass import MockNode


@pytest.fixture
def zwavePlusInfo() -> ZwavePlusInfo.ZwavePlusInfo:
    node = MockNode([ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=1,
        )
    )
    node.queue(
        ZwavePlusInfo.Report(
            zwavePlusVersion=1,
            roleType=5,
            nodeType=0,
            installerIconType=1793,
            userIconType=1792,
        )
    )
    return node.supported[ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO]


@pytest.mark.asyncio
async def test_interview(zwavePlusInfo: ZwavePlusInfo.ZwavePlusInfo):
    await zwavePlusInfo.interview()
    assert zwavePlusInfo.zwavePlusVersion == 1
    assert zwavePlusInfo.roleType == 5
    assert zwavePlusInfo.nodeType == 0
    assert zwavePlusInfo.installerIconType == 1793
    assert zwavePlusInfo.userIconType == 1792
