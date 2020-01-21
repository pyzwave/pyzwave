from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY,
    NODE_LIST_GET,
    NODE_LIST_REPORT,
)
from pyzwave.message import Message
from pyzwave.types import BitStreamReader, uint8_t
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY, "NETWORK_MANAGEMENT_PROXY")


class NodeList(set):
    """Deserializer for nodelist returned in NODE_LIST_REPORT"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize nodes from stream"""
        nodeList = cls()
        for i in range(28):
            nodeByte = uint8_t.deserialize(stream)
            for j in range(8):
                if nodeByte & (1 << j):
                    nodeList.add(i * 8 + j + 1)
        return nodeList


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY, NODE_LIST_GET)
class NodeListGet(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY NODE_LIST_GET"""

    NAME = "NODE_LIST_GET"

    attributes = (("seqNo", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY, NODE_LIST_REPORT)
class NodeListReport(Message):
    """Command Class message COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY NODE_LIST_REPORT"""

    NAME = "NODE_LIST_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("status", uint8_t),
        ("nodeListControllerId", uint8_t),
        ("nodes", NodeList),
    )
