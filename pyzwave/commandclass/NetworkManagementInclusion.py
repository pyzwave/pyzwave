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
    dsk_t,
    flag_t,
    reserved_t,
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
        ("mode", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, FAILED_NODE_REMOVE_STATUS)
class FailedNodeRemoveStatus(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION FAILED_NODE_REMOVE_STATUS"""

    NAME = "FAILED_NODE_REMOVE_STATUS"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
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

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(8)),
        ("mode", uint8_t),
        ("txOptions", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_DSK_REPORT)
class NodeAddDSKReport(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_DSK_REPORT"""

    NAME = "NODE_ADD_DSK_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("dsk", dsk_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_DSK_SET)
class NodeAddDSKSet(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_DSK_SET"""

    NAME = "NODE_ADD_DSK_SET"

    attributes = (
        ("seqNo", uint8_t),
        ("dsk", dsk_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_KEYS_REPORT)
class NodeAddKeysReport(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_KEYS_REPORT"""

    NAME = "NODE_ADD_KEYS_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(7)),
        ("requestCSA", flag_t),
        ("requestedKeys", uint8_t),
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
        ("grantedKeys", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_ADD_STATUS)
class NodeAddStatus(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_ADD_STATUS"""

    NAME = "NODE_ADD_STATUS"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
        ("-", reserved_t(8)),
        ("newNodeID", uint8_t),
        ("nodeInfoLength", uint8_t),
        # TODO, the rest of the params
    )


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

    attributes = (
        ("seqNo", uint8_t),
        ("-", reserved_t(8)),
        ("mode", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION, NODE_REMOVE_STATUS)
class NodeRemoveStatus(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_INCLUSION NODE_REMOVE_STATUS"""

    NAME = "NODE_REMOVE_STATUS"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
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
