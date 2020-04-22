# from typing import Dict, List
from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ASSOCIATION_GRP_INFO,
    ASSOCIATION_GROUP_COMMAND_LIST_GET,
    ASSOCIATION_GROUP_COMMAND_LIST_REPORT,
    ASSOCIATION_GROUP_INFO_GET,
    ASSOCIATION_GROUP_INFO_REPORT,
    ASSOCIATION_GROUP_NAME_GET,
    ASSOCIATION_GROUP_NAME_REPORT,
)

from pyzwave.message import Message
from pyzwave.types import (
    BitStreamReader,
    bits_t,
    flag_t,
    reserved_t,
    str_t,
    uint8_t,
    uint16_t,
)
from . import ZWaveMessage, ZWaveMessageHandler, ZWaveCommandClass
from .CommandClass import DictAttribute, CommandClass


class Group(DictAttribute):
    """Attribute for an association group"""

    attributes = (
        ("name", str),
        # ("mode", uint8_t),  # Not used according to docs, always zero. No need to save it
        ("profile", uint16_t),
        # ("eventCode", uint16_t),  # Not used according to docs, always zero. No need to save it
        ("commands", list),
    )


class Groupings(dict):
    """Helper class for storing association groups"""

    def __getstate__(self):
        return {int(group): value.__getstate__() for group, value in self.items()}

    def __setstate__(self, state):
        for key, value in state.items():
            group = Group()
            group.__setstate__(value)
            self[int(key)] = group


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION_GRP_INFO, ASSOCIATION_GROUP_COMMAND_LIST_GET)
class GroupCommandListGet(Message):
    """
    Command Class message
    COMMAND_CLASS_ASSOCIATION_GRP_INFO ASSOCIATION_GROUP_COMMAND_LIST_GET
    """

    NAME = "GROUP_COMMAND_LIST_GET"
    attributes = (
        ("allowCache", flag_t),
        ("-", reserved_t(7)),
        ("groupingIdentifier", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION_GRP_INFO, ASSOCIATION_GROUP_COMMAND_LIST_REPORT)
class GroupCommandListReport(Message):
    """
    Command Class message
    COMMAND_CLASS_ASSOCIATION_GRP_INFO ASSOCIATION_GROUP_COMMAND_LIST_REPORT
    """

    NAME = "GROUP_COMMAND_LIST_REPORT"

    attributes = (
        ("groupingIdentifier", uint8_t),
        ("commandClass", list),
    )

    @staticmethod
    def parse_commandClass(stream: BitStreamReader):  # pylint: disable=invalid-name
        """Parse attribute commandClass"""
        retval = []
        length = stream.byte()
        i = 0
        while i < length:
            commandClass = stream.byte()
            # TODO: Handle command classes with 2 bytes
            command = stream.byte()
            retval.append([commandClass, command])
            i += 2
        return retval


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION_GRP_INFO, ASSOCIATION_GROUP_INFO_GET)
class GroupInfoGet(Message):
    """Command Class message COMMAND_CLASS_VERSION ASSOCIATION_GROUP_INFO_GET"""

    NAME = "GROUP_INFO_GET"
    attributes = (
        ("refreshCache", flag_t),
        ("listMode", flag_t),
        ("-", reserved_t(6)),
        ("groupingIdentifier", uint8_t),
    )


class GroupInfoGroupType(DictAttribute):
    """The type for the group property in the GroupInfoReport"""

    attributes = (
        ("groupingIdentifier", uint8_t),
        ("mode", uint8_t),
        ("profile", uint16_t),
        ("-", reserved_t(8)),
        ("eventCode", uint16_t),
    )


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION_GRP_INFO, ASSOCIATION_GROUP_INFO_REPORT)
class GroupInfoReport(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION_GRP_INFO ASSOCIATION_GROUP_INFO_REPORT"""

    NAME = "GROUP_INFO_REPORT"

    attributes = (
        ("listMode", flag_t),
        ("dynamicInfo", flag_t),
        ("groupCount", bits_t(6)),
        ("groups", list),
    )

    def parse_groups(self, stream: BitStreamReader):  # pylint: disable=invalid-name
        """Parse groups"""
        retval = []
        for _ in range(int(self.groupCount)):
            grp = GroupInfoGroupType()
            grp.parseAttributes(stream)
            retval.append(grp)
        return retval


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION_GRP_INFO, ASSOCIATION_GROUP_NAME_GET)
class GroupNameGet(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION_GRP_INFO ASSOCIATION_GROUP_NAME_GET"""

    NAME = "GROUP_NAME_GET"
    attributes = (("groupingIdentifier", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_ASSOCIATION_GRP_INFO, ASSOCIATION_GROUP_NAME_REPORT)
class GroupNameReport(Message):
    """Command Class message COMMAND_CLASS_ASSOCIATION_GRP_INFO ASSOCIATION_GROUP_NAME_REPORT"""

    NAME = "GROUP_NAME_REPORT"

    attributes = (
        ("groupingIdentifier", uint8_t),
        ("name", str_t),
    )


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_ASSOCIATION_GRP_INFO)
class AssociationGrpInfo(CommandClass):
    """Command Class COMMAND_CLASS_ASSOCIATION_GRP_INFO"""

    NAME = "ASSOCIATION_GRP_INFO"
    attributes = (("groupings", Groupings),)

    @ZWaveMessageHandler(GroupCommandListReport)
    async def __groupCommandListReport__(self, report: GroupCommandListReport, _flags):
        self.groupings[report.groupingIdentifier].commands = list(report.commandClass)
        return True

    @ZWaveMessageHandler(GroupInfoReport)
    async def __groupInfoReport__(self, report: GroupInfoReport, _flags):
        for group in report.groups:
            self.groupings[group.groupingIdentifier] = Group(profile=group.profile)
            await self.send(GroupNameGet(groupingIdentifier=group.groupingIdentifier),)
            await self.send(
                GroupCommandListGet(
                    allowCache=True, groupingIdentifier=group.groupingIdentifier
                ),
            )
        return True

    @ZWaveMessageHandler(GroupNameReport)
    async def __groupNameReport__(self, report: GroupNameReport, _flags):
        if report.groupingIdentifier not in self.groupings:
            return True
        self.groupings[report.groupingIdentifier].name = report.name
        return True

    async def interview(self):
        # We may get several reports from this command. At this point we do not know how many so
        # it is easier to handle them all in groupInfoReport than waiting here
        await self.send(
            GroupInfoGet(refreshCache=False, listMode=True, groupingIdentifier=0)
        )
        # We do not know when we have received everything so we mark the command class
        # as interviewed...
        return True
