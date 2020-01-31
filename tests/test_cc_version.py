# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest

from pyzwave.commandclass import Version

from test_commandclass import MockNode


@pytest.fixture
def version() -> Version.Version:
    node = MockNode([Version.COMMAND_CLASS_VERSION])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=4,
        )
    )
    node.queue(
        Version.VersionReport(
            zwaveLibraryType=6,
            zwaveProtocolVersion=1,
            zwaveProtocolSubVersion=2,
            applicationVersion=1,
            applicationSubVersion=0,
        )
    )
    return node.supported[Version.COMMAND_CLASS_VERSION]


@pytest.mark.asyncio
async def test_interview(version: Version.Version):
    await version.interview()
    assert version.zwaveLibraryType == 6
    assert version.zwaveProtocolVersion == 1
    assert version.zwaveProtocolSubVersion == 2
    assert version.applicationVersion == 1
    assert version.applicationSubVersion == 0
