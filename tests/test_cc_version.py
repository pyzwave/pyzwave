# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest

from pyzwave.commandclass import Version

from test_commandclass import MockNode, version


@pytest.mark.asyncio
async def test_interview(version: Version.Version):
    await version.interview()
    assert version.zwaveLibraryType == 6
    assert version.zwaveProtocolVersion == 1
    assert version.zwaveProtocolSubVersion == 2
    assert version.applicationVersion == 1
    assert version.applicationSubVersion == 0
