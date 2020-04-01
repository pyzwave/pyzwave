from enum import IntEnum, IntFlag

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION,
    FAILED_NODE_REMOVE,
    FAILED_NODE_REMOVE_STATUS,
    FAILED_NODE_REPLACE,
    FAILED_NODE_REPLACE_STATUS,
    INCLUDED_NIF_REPORT,
    NODE_ADD,
    NODE_ADD_DSK_REPORT,
    NODE_ADD_DSK_SET,
    NODE_ADD_KEYS_REPORT,
    NODE_ADD_KEYS_SET,
    NODE_ADD_STATUS,
    NODE_NEIGHBOR_UPDATE_REQUEST,
    NODE_NEIGHBOR_UPDATE_STATUS,
    NODE_REMOVE,
    NODE_REMOVE_STATUS,
    RETURN_ROUTE_ASSIGN,
    RETURN_ROUTE_ASSIGN_COMPLETE,
    RETURN_ROUTE_DELETE,
    RETURN_ROUTE_DELETE_COMPLETE,
    SMART_START_JOIN_STARTED_REPORT,
)
from pyzwave.message import Message
from pyzwave.types import (
    BitStreamReader,
    dsk_t,
    enum_t,
    flag_t,
    reserved_t,
    uint4_t,
    uint8_t,
)
from . import ZWaveMessage, registerCmdClass


registerCmdClass(
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, "NETWORK_MANAGEMENT_INCLUSION"
)


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, FAILED_NODE_REMOVE)
class FailedNodeRemove(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION FAILED_NODE_REMOVE"""

    NAME = "FAILED_NODE_REMOVE"

    attributes = (
        ("seqNo", uint8_t),
        ("nodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, FAILED_NODE_REMOVE_STATUS)
class FailedNodeRemoveStatus(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION FAILED_NODE_REMOVE_STATUS"""

    NAME = "FAILED_NODE_REMOVE_STATUS"

    class Status(IntEnum):
        """Failed node remove status"""

        NOT_FOUND = 0x00
        DONE = 0x01
        REMOVE_FAIL = 0x02

    attributes = (
        ("seqNo", uint8_t),
        ("status", enum_t(Status, uint8_t)),
        ("nodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, FAILED_NODE_REPLACE)
class FailedNodeReplace(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION FAILED_NODE_REPLACE"""

    NAME = "FAILED_NODE_REPLACE"

    attributes = (
        ("seqNo", uint8_t),
        ("nodeID", uint8_t),
        ("txOptions", uint8_t),
        ("mode", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, FAILED_NODE_REPLACE_STATUS)
class FailedNodeReplaceStatus(Message):
    """
    Command Class message
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION
    FAILED_NODE_REPLACE_STATUS
    """

    NAME = "FAILED_NODE_REPLACE_STATUS"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
        ("nodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, INCLUDED_NIF_REPORT)
class IncludedNIFReport(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION INCLUDED_NIF_REPORT"""

    NAME = "INCLUDED_NIF_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("dsk", dsk_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD)
class NodeAdd(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD"""

    NAME = "NODE_ADD"

    class Mode(IntEnum):
        """Node add mode"""

        ANY = 0x01
        STOP = 0x05
        ANY_S2 = 0x07

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(8)),
        ("mode", enum_t(Mode, uint8_t)),
        ("txOptions", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_DSK_REPORT)
class NodeAddDSKReport(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_DSK_REPORT"""

    NAME = "NODE_ADD_DSK_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(4)),
        ("inputDSKLength", uint4_t),
        ("dsk", dsk_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_DSK_SET)
class NodeAddDSKSet(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_DSK_SET"""

    NAME = "NODE_ADD_DSK_SET"

    attributes = (
        ("seqNo", uint8_t),
        ("accept", flag_t),
        ("-", reserved_t(3)),
        ("inputDSKLength", uint4_t),
        ("dsk", dsk_t),
    )


class Keys(IntFlag):
    """Keys flags for S2 bootstrapping"""

    UNAUTHENTICATED_SECURITY_CLASS = 1
    AUTHENTICATED_SECURITY_CLASS = 2
    ACCESS_CONTROL_SECURITY_CLASS = 4
    SECURITY_0_NETWORK_KEY = 128


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_KEYS_REPORT)
class NodeAddKeysReport(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_KEYS_REPORT"""

    NAME = "NODE_ADD_KEYS_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(7)),
        ("requestCSA", flag_t),
        ("requestedKeys", enum_t(Keys, uint8_t)),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_KEYS_SET)
class NodeAddKeysSet(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_KEYS_SET"""

    NAME = "NODE_ADD_KEYS_SET"

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(6)),
        ("grantCSA", flag_t),
        ("accept", flag_t),
        ("grantedKeys", enum_t(Keys, uint8_t)),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_STATUS)
class NodeAddStatus(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_STATUS"""

    class Status(IntEnum):
        """Add node status"""

        NODE_FOUND = 0x02  # Note, not part of NodeAddStatus, only in Serial Api
        ADD_SLAVE = 0x03  # Note, not part of NodeAddStatus, only in Serial Api
        PROTOCOL_DONE = 0x05  # Note, not part of NodeAddStatus, only in Serial Api
        DONE = 0x06
        FAILED = 0x07
        SECURITY_FAILED = 0x09

    NAME = "NODE_ADD_STATUS"

    attributes = (
        ("seqNo", uint8_t),
        ("status", enum_t(Status, uint8_t)),
        ("-", reserved_t(8)),
        ("newNodeID", uint8_t),
        ("nodeInfoLength", uint8_t),
        ("listening", flag_t),
        ("zwaveProtocolSpecific", reserved_t(7)),
        ("optFunc", flag_t),
        ("zwaveProtocolSpecific", reserved_t(7)),
        ("basicDeviceClass", uint8_t),
        ("genericDeviceClass", uint8_t),
        ("specificDeviceClass", uint8_t),
        ("commandClass", list),
    )

    def parse_commandClass(
        self, stream: BitStreamReader
    ):  # pylint: disable=invalid-name
        """Parse the length prefixed command"""
        length = self.nodeInfoLength - 7
        if length > stream.bytesLeft():
            return list(stream.remaining())
        return list(stream.value(length))


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_NEIGHBOR_UPDATE_REQUEST)
class NodeNeightborUpdateRequest(Message):
    """
    Command Class message
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION
    NODE_NEIGHBOR_UPDATE_REQUEST
    """

    NAME = "NODE_NEIGHBOR_UPDATE_REQUEST"

    attributes = (
        ("seqNo", uint8_t),
        ("nodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_NEIGHBOR_UPDATE_STATUS)
class NodeNeightborUpdateStatus(Message):
    """
    Command Class message
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION
    NODE_NEIGHBOR_UPDATE_STATUS
    """

    NAME = "NODE_NEIGHBOR_UPDATE_STATUS"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_REMOVE)
class NodeRemove(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_REMOVE"""

    NAME = "NODE_REMOVE"

    class Mode(IntEnum):
        """Remove node mode"""

        ANY = 0x01
        STOP = 0x05

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(8)),
        ("mode", enum_t(Mode, uint8_t)),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_REMOVE_STATUS)
class NodeRemoveStatus(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_REMOVE_STATUS"""

    NAME = "NODE_REMOVE_STATUS"

    class Status(IntEnum):
        """Remove node status"""

        DONE = 0x06
        FAILED = 0x07

    attributes = (
        ("seqNo", uint8_t),
        ("status", enum_t(Status, uint8_t)),
        ("nodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, RETURN_ROUTE_ASSIGN)
class ReturnRouteAssign(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION RETURN_ROUTE_ASSIGN"""

    NAME = "RETURN_ROUTE_ASSIGN"

    attributes = (
        ("seqNo", uint8_t),
        ("sourceNodeID", uint8_t),
        ("destinationNodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, RETURN_ROUTE_ASSIGN_COMPLETE)
class ReturnRouteAssignComplete(Message):
    """
    Command Class message
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION
    RETURN_ROUTE_ASSIGN_COMPLETE
    """

    NAME = "RETURN_ROUTE_ASSIGN_COMPLETE"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, RETURN_ROUTE_DELETE)
class ReturnRouteDelete(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION RETURN_ROUTE_DELETE"""

    NAME = "RETURN_ROUTE_DELETE"

    attributes = (
        ("seqNo", uint8_t),
        ("nodeID", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, RETURN_ROUTE_DELETE_COMPLETE)
class ReturnRouteDeleteComplete(Message):
    """
    Command Class message
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION
    RETURN_ROUTE_DELETE_COMPLETE
    """

    NAME = "RETURN_ROUTE_DELETE_COMPLETE"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
    )


@ZWaveMessage(
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, SMART_START_JOIN_STARTED_REPORT
)
class SmartStartJoinStartedReport(Message):
    """
    Command Class message
    COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION
    SMART_START_JOIN_STARTED_REPORT
    """

    NAME = "SMART_START_JOIN_STARTED_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("dsk", dsk_t),
    )
