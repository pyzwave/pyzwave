import asyncio
import logging

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ASSOCIATION,
    ASSOCIATION_GET,
    ASSOCIATION_REPORT,
    ASSOCIATION_SET,
    ASSOCIATION_GROUPINGS_GET,
    ASSOCIATION_GROUPINGS_REPORT,
)
from pyzwave.message import Message
from pyzwave.types import bytes_t, uint8_t
from . import ZWaveCommandClass, ZWaveMessage
from .CommandClass import CommandClass, DictAttribute

_LOGGER = logging.getLogger(__name__)

# pylint: disable=attribute-defined-outside-init
class Group(DictAttribute):
    """Attribute for information regarding one association group"""

    attributes = (
        ("maxNodes", uint8_t),
        ("nodes", list),
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
        self.speak("commandClassUpdated")

    async def interviewGrouping(self, groupingIdentifier):
        """Interview an association group"""
        group = self.groupings[groupingIdentifier]
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
        if controllerId in grouping.nodes:
            # Lifeline already setup
            return
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
        ("nodes", bytes_t),
    )


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION, ASSOCIATION_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION ASSOCIATION_SET"""

    NAME = "SET"

    attributes = (
        ("groupingIdentifier", uint8_t),
        ("nodes", bytes_t),
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
