# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import asyncio
import pytest

from pyzwave.commandclass import Association, Version, ZwavePlusInfo

from test_commandclass import MockNode


@pytest.fixture
def association() -> Association.Association:
    node = MockNode([Association.COMMAND_CLASS_ASSOCIATION])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=1,
        )
    )
    node.queue(Association.GroupingsReport(supportedGroupings=1,))
    node.queue(
        Association.Report(
            groupingIdentifier=1, maxNodesSupported=1, reportsToFollow=0, nodes=b"\x01"
        )
    )
    return node.supported[Association.COMMAND_CLASS_ASSOCIATION]


def test_groupings():
    groupings = Association.Groupings()
    assert groupings.__getstate__() == {}
    groupings.setNumGroups(1)
    assert groupings.__getstate__() == {1: {"maxNodes": 0}}
    groupings.__setstate__({2: {"maxNodes": 2, "foo": "bar"}})
    assert groupings.__getstate__() == {1: {"maxNodes": 0}, 2: {"maxNodes": 2}}


@pytest.mark.asyncio
async def test_interview(association: Association.Association):
    await association.interview()
    assert association.__getstate__() == {
        "groupings": {1: {"maxNodes": 1, "nodes": [1]}},
        "version": 1,
    }


@pytest.mark.asyncio
async def test_interview_timeout(association: Association.Association):
    async def interviewGrouping(*args):
        raise asyncio.TimeoutError()

    association.interviewGrouping = interviewGrouping
    await association.interview()
    assert association.__getstate__() == {
        "groupings": {1: {"maxNodes": 0}},
        "version": 1,
    }


@pytest.mark.asyncio
async def test_interview_wrong_response(association: Association.Association):
    association.node.queue(
        Association.Report(
            groupingIdentifier=2, maxNodesSupported=1, reportsToFollow=0, nodes=b""
        )
    )
    await association.interview()
    assert association.__getstate__() == {
        "groupings": {1: {"maxNodes": 0}},
        "version": 1,
    }


@pytest.mark.asyncio
async def test_setupLifeLine(association: Association.Association):
    association.node.addCommandClass(ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO)
    setMsg = Association.Set(groupingIdentifier=1, nodes=bytes([1]))

    # Do not send message until groups has been setup
    await association.setupLifeLine()
    association.node.assert_message_not_sent(setMsg)

    association.groupings.setNumGroups(1)
    await association.setupLifeLine()
    association.node.assert_message_sent(setMsg)

    # Make sure it is not sent if already setup
    association.node.clear(sent=True)
    await association.setupLifeLine()
    association.node.assert_message_not_sent(setMsg)


@pytest.mark.asyncio
async def test_setupLifeLine_nonZWavePlus(association: Association.Association):
    await association.setupLifeLine()
