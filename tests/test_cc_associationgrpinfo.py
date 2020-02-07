# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest

from pyzwave.commandclass import (
    AssociationGrpInfo,
    Version,
)
from pyzwave.message import Message

from test_commandclass import MockNode


@pytest.fixture
def associationgrpinfo() -> AssociationGrpInfo.AssociationGrpInfo:
    node = MockNode([AssociationGrpInfo.COMMAND_CLASS_ASSOCIATION_GRP_INFO])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=1,
        )
    )
    node.reply(
        AssociationGrpInfo.GroupNameGet,
        AssociationGrpInfo.GroupNameReport(groupingIdentifier=1, name="Lifeline"),
    )
    node.reply(
        AssociationGrpInfo.GroupCommandListGet,
        AssociationGrpInfo.GroupCommandListReport(
            groupingIdentifier=1, commandClass=[[1, 2], [3, 4]]
        ),
    )
    # node.queue(Association.GroupingsReport(supportedGroupings=1,))
    # node.queue(
    #     MultiChannelAssociation.MultiChannelReport(
    #         groupingIdentifier=1,
    #         maxNodesSupported=1,
    #         reportsToFollow=0,
    #         nodes=[(1, None), (2, 0)],
    #     )
    # )
    # node.queue(
    #     Association.Report(
    #         groupingIdentifier=1, maxNodesSupported=1, reportsToFollow=0, nodes=[1]
    #     )
    # )
    return node.supported[AssociationGrpInfo.COMMAND_CLASS_ASSOCIATION_GRP_INFO]


def test_groupcommandlistreport():
    report = Message.decode(b"Y\x06\t\x021\x05")
    assert report.commandClass == [[49, 5]]


def test_groupinforeport():
    report = Message.decode(b"Y\x04\x81\x01\x00q\x07\x00\x00\x00")
    assert report.groupCount == 1
    assert report.groups[0].groupingIdentifier == 1
    assert report.groups[0].mode == 0
    assert report.groups[0].profile == 0x7107
    assert report.groups[0].eventCode == 0


def test_groupings():
    groupings = AssociationGrpInfo.Groupings()
    assert groupings.__getstate__() == {}
    state = {
        1: {"commands": [[90, 1], [49, 5], [50, 2]], "name": "lifeline", "profile": 1,}
    }
    groupings.__setstate__(state)
    assert groupings.__getstate__() == state


@pytest.mark.asyncio
async def test_interview(associationgrpinfo: AssociationGrpInfo.AssociationGrpInfo):
    await associationgrpinfo.interview()
    AssociationGrpInfo.GroupInfoReport()
    await associationgrpinfo.node.handleMessage(
        AssociationGrpInfo.GroupInfoReport(
            groupCount=1,
            groups=[AssociationGrpInfo.GroupInfoGroupType(groupingIdentifier=1)],
        )
    )
    assert associationgrpinfo.__getstate__() == {
        "groupings": {
            1: {"profile": 0, "name": "Lifeline", "commands": [[1, 2], [3, 4]]}
        },
        "version": 1,
    }


# @pytest.mark.asyncio
# async def test_interview_multichannel(association: Association.Association):
#     association.node.addCommandClass(
#         Association.COMMAND_CLASS_MULTI_CHANNEL_ASSOCIATION_V2
#     )
#     association.node.addCommandClass(Association.COMMAND_CLASS_MULTI_CHANNEL_V2)
#     await association.interview()
#     assert association.__getstate__() == {
#         "groupings": {1: {"maxNodes": 1, "nodes": ["1", "2:0"]}},
#         "version": 1,
#     }


# @pytest.mark.asyncio
# async def test_interview_timeout(association: Association.Association):
#     async def interviewGrouping(*args):
#         raise asyncio.TimeoutError()

#     association.interviewGrouping = interviewGrouping
#     await association.interview()
#     assert association.__getstate__() == {
#         "groupings": {1: {"maxNodes": 0}},
#         "version": 1,
#     }


# @pytest.mark.asyncio
# async def test_interview_wrong_response(association: Association.Association):
#     association.node.queue(
#         Association.Report(
#             groupingIdentifier=2, maxNodesSupported=1, reportsToFollow=0, nodes=b""
#         )
#     )
#     await association.interview()
#     assert association.__getstate__() == {
#         "groupings": {1: {"maxNodes": 0}},
#         "version": 1,
#     }


# def test_nodes__getstate__():
#     nodes = Association.Nodes([(1, None), (2, 0)])
#     assert nodes.__getstate__() == ["1", "2:0"]


# def test_nodes__setstate__():
#     nodes = Association.Nodes()
#     nodes.__setstate__(["1", "2:0"])
#     assert nodes == [(1, None), (2, 0)]


# def test_nodes_deserialize():
#     reader = BitStreamReader(bytes([1, 0, 2, 0]))
#     nodes = Association.Nodes.deserialize(reader)
#     assert nodes == [(1, None), (2, 0)]


# def test_nodes_serialize():
#     writer = BitStreamWriter()
#     nodes = Association.Nodes([(1, None), (2, 0)])
#     nodes.serialize(writer)
#     assert writer == bytes([1, 0, 2, 0])


# @pytest.mark.asyncio
# async def test_setupLifeLine(association: Association.Association):
#     association.node.addCommandClass(ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO)
#     setMsg = Association.Set(groupingIdentifier=1, nodes=[1])

#     # Do not send message until groups has been setup
#     await association.setupLifeLine()
#     association.node.assert_message_not_sent(setMsg)

#     association.groupings.setNumGroups(1)
#     await association.setupLifeLine()
#     association.node.assert_message_sent(setMsg)

#     # Make sure it is not sent if already setup
#     association.node.clear(sent=True)
#     await association.setupLifeLine()
#     association.node.assert_message_not_sent(setMsg)


# @pytest.mark.asyncio
# async def test_setupLifeLine_multichannel(association: Association.Association):
#     association.node.addCommandClass(ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO)
#     association.node.addCommandClass(
#         Association.COMMAND_CLASS_MULTI_CHANNEL_ASSOCIATION_V2
#     )
#     association.node.addCommandClass(Association.COMMAND_CLASS_MULTI_CHANNEL_V2)
#     association.groupings.setNumGroups(1)
#     await association.setupLifeLine()
#     association.node.assert_message_sent(
#         MultiChannelAssociation.MultiChannelSet(groupingIdentifier=1, nodes=[(1, 0)])
#     )


# @pytest.mark.asyncio
# async def test_setupLifeLine_nonZWavePlus(association: Association.Association):
#     await association.setupLifeLine()
