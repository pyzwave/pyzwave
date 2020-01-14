import struct

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY,
    NODE_LIST_GET,
    NODE_LIST_REPORT,
)
from pyzwave.message import Message
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY, "NETWORK_MANAGEMENT_PROXY")


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY, NODE_LIST_GET)
class NodeListGet(Message):
    NAME = "NODE_LIST_GET"

    def __init__(self, cmdClass, cmd, seqNo=0):
        super().__init__(cmdClass, cmd)
        self._seqNo = seqNo

    def compose(self):
        return self.encode(self._seqNo)

    def parse(self, pkt):
        (self._seqNo,) = struct.unpack("B", pkt[0:1])

    @property
    def seqNo(self):
        return self._seqNo

    @seqNo.setter
    def seqNo(self, seqNo):
        self._seqNo = seqNo


@ZWaveMessage(COMMAND_CLASS_NETWORK_MANAGEMENT_PROXY, NODE_LIST_REPORT)
class NodeListReport(Message):
    NAME = "NODE_LIST_REPORT"

    def __init__(self, cmdClass, cmd):
        super().__init__(cmdClass, cmd)
        self._seqNo = 0
        self._status = 0
        self._nodeListControllerID = 0
        self._nodes = set()

    @property
    def nodes(self):
        return self._nodes

    def parse(self, pkt):
        (self._seqNo, self._status, self._nodeListControllerID,) = struct.unpack(
            "3B", pkt[0:3]
        )
        nodes = pkt[3:]
        self._nodes = set()
        for i in range(len(nodes)):
            nodeByte = nodes[i]
            for j in range(8):
                if nodeByte & (1 << j):
                    self._nodes.add(i * 8 + j + 1)

    @property
    def seqNo(self):
        return self._seqNo

    @seqNo.setter
    def seqNo(self, seqNo):
        self._seqNo = seqNo

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def nodeListControllerID(self):
        return self._nodeListControllerID

    @nodeListControllerID.setter
    def nodeListControllerID(self, nodeListControllerID):
        self._nodeListControllerID = nodeListControllerID
