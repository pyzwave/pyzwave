# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from pyzwave.commandclass import NetworkManagementInclusion
from pyzwave.message import Message


def test_node_add_status():
    pkt = b"\x34\x02\x0c\x06\x00N\x15\xd3\x9c\x04\x10\x01^%'\x85\\pru\x86ZYszh#\x00\x00\x00"
    msg = Message.decode(pkt)
    assert isinstance(msg, NetworkManagementInclusion.NodeAddStatus)
    assert msg.seqNo == 12
    assert msg.newNodeID == 78
    assert msg.commandClass == [
        94,
        37,
        39,
        133,
        92,
        112,
        114,
        117,
        134,
        90,
        89,
        115,
        122,
        104,
    ]
