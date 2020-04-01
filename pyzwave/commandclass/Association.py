import asyncio
import logging

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ASSOCIATION,
    COMMAND_CLASS_MULTI_CHANNEL_ASSOCIATION_V2,
    COMMAND_CLASS_MULTI_CHANNEL_V2,
    ASSOCIATION_GET,
    ASSOCIATION_REPORT,
    ASSOCIATION_SET,
    ASSOCIATION_GROUPINGS_GET,
    ASSOCIATION_GROUPINGS_REPORT,
    MULTI_CHANNEL_ASSOCIATION_SET_MARKER_V2,
)
from pyzwave.message import Message
from pyzwave.types import BitStreamReader, BitStreamWriter, uint8_t
from . import ZWaveCommandClass, ZWaveMessage
from .CommandClass import CommandClass, DictAttribute

_LOGGER = logging.getLogger(__name__)


class Nodes(list):
    """Nodes in association reports. Handle both normal and multi channel"""

    default = []

    def contains(self, nodeId, endpoint=0) -> bool:
        """Returns if node is in this collection"""
        for iNodeId, iEndpoint in self:
            if iEndpoint is None:
                iEndpoint = 0
            if nodeId == iNodeId and endpoint == iEndpoint:
                return True
        return False

    def __getstate__(self):
        retval = []
        for nodeId, endpoint in self:
            if endpoint is None:
                retval.append(str(nodeId))
            else:
                retval.append("{}:{}".format(nodeId, endpoint))
        return retval

    def __setstate__(self, state):
        for node in state:
            if isinstance(node, tuple):
                nodeId, endpoint = node
            elif isinstance(node, int):
                nodeId, endpoint = node, None
            elif ":" in node:
                nodeId, endpoint = node.split(":", 1)
                endpoint = int(endpoint)
            else:
                nodeId, endpoint = node, None
            self.append((int(nodeId), endpoint))

    def serialize(self, stream: BitStreamWriter):
        """Serialise nodes"""
        haveMultichannel = False
        for node, endpoint in self:
            if endpoint is not None:
                haveMultichannel = True
                continue
            stream.append(node)
        if not haveMultichannel:
            return
        stream.append(MULTI_CHANNEL_ASSOCIATION_SET_MARKER_V2)
        for node, endpoint in self:
            if endpoint is None:
                # Already added
                continue
            stream.extend([node, endpoint])

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize nodes from association report."""
        data = stream.remaining()
        nodes = []
        while data:
            node = data[0]
            data = data[1:]
            if node == MULTI_CHANNEL_ASSOCIATION_SET_MARKER_V2:
                break
            nodes.append((node, None))
        while data:
            node = data[0]
            endpoint = data[1]
            nodes.append((node, endpoint))
            data = data[2:]
        return nodes


# pylint: disable=attribute-defined-outside-init
class Group(DictAttribute):
    """Attribute for information regarding one association group"""

    attributes = (
        ("maxNodes", uint8_t),
        ("nodes", Nodes),
    )


class Groupings(dict):
    """Helper class for storing associations"""

    def setNumGroups(self, number: int):
        """Set the number of groups this node has"""
        for i in range(1, number + 1):
            if i not in self:
                group = Group()
                group.maxNodes = 0
                group.multiChannelMaxNodes = 0
                self[i] = group

    def __getstate__(self):
        return {group: value.__getstate__() for group, value in self.items()}

    def __setstate__(self, state):
        for key, value in state.items():
            group = Group()
            group.__setstate__(value)
            self[int(key)] = group


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_ASSOCIATION)
class Association(CommandClass):
    """Command Class COMMAND_CLASS_ASSOCIATION"""

    NAME = "ASSOCIATION"
    attributes = (("groupings", Groupings),)

    async def interview(self):
        report = await self.sendAndReceive(GroupingsGet(), GroupingsReport)
        self.groupings.setNumGroups(report.supportedGroupings)
        for identifier in self.groupings:
            try:
                await self.interviewGrouping(identifier)
            except asyncio.TimeoutError:
                continue
        await self.setupLifeLine()

    async def interviewGrouping(self, groupingIdentifier):
        """Interview an association group"""
        group = self.groupings[groupingIdentifier]
        if self.node.supports(COMMAND_CLASS_MULTI_CHANNEL_ASSOCIATION_V2):
            report = await self.sendAndReceive(
                MultiChannelGet(groupingIdentifier=groupingIdentifier),
                MultiChannelReport,
            )
        else:
            report = await self.sendAndReceive(
                Get(groupingIdentifier=groupingIdentifier), Report
            )
        if report.groupingIdentifier != groupingIdentifier:
            # Got the wrong message. Should hopyfully not happen...
            return
        group.maxNodes = report.maxNodesSupported
        group.nodes = report.nodes

    async def setupLifeLine(self, groupingIdentifier=1):
        """Setup the lifeline association group"""
        if not self.node.isZWavePlus:
            # Non Z-Wave Plus does not have a fixed defined lifeline.
            # Setup the lifeline like association groups in quirks instead.
            return
        controllerId = 1  # TODO: Get this dynamically
        grouping = self.groupings.get(groupingIdentifier)
        if not grouping:
            # No associations set. Bail.
            return
        if grouping.nodes.contains(controllerId):
            # Lifeline already setup
            return
        if self.node.supports(COMMAND_CLASS_MULTI_CHANNEL_V2) and self.node.supports(
            COMMAND_CLASS_MULTI_CHANNEL_ASSOCIATION_V2
        ):
            await self.node.send(
                MultiChannelSet(
                    groupingIdentifier=groupingIdentifier, nodes=[(controllerId, 0)]
                )
            )
        else:
            await self.node.send(
                Set(groupingIdentifier=groupingIdentifier, nodes=[controllerId])
            )
        await self.interviewGrouping(groupingIdentifier)


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION, ASSOCIATION_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION ASSOCIATION_GET"""

    NAME = "GET"

    attributes = (("groupingIdentifier", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION, ASSOCIATION_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION ASSOCIATION_GROUPINGS_REPORT"""

    NAME = "REPORT"

    attributes = (
        ("groupingIdentifier", uint8_t),
        ("maxNodesSupported", uint8_t),
        ("reportsToFollow", uint8_t),
        ("nodes", Nodes),
    )


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION, ASSOCIATION_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION ASSOCIATION_SET"""

    NAME = "SET"

    attributes = (
        ("groupingIdentifier", uint8_t),
        ("nodes", Nodes),
    )


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION, ASSOCIATION_GROUPINGS_GET)
class GroupingsGet(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION ASSOCIATION_GROUPINGS_GET"""

    NAME = "GROUPINGS_GET"


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION, ASSOCIATION_GROUPINGS_REPORT)
class GroupingsReport(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION ASSOCIATION_GROUPINGS_REPORT"""

    NAME = "GROUPINGS_REPORT"

    attributes = (("supportedGroupings", uint8_t),)


# pylint: disable=wrong-import-position
from .MultiChannelAssociation import (
    MultiChannelGet,
    MultiChannelReport,
    MultiChannelSet,
)
