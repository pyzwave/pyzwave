# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from pyzwave.commandclass import NetworkManagementProxy
from pyzwave.message import Message


def test_node_list_get():
    pkt = b"R\x01\x02"
    msg = Message.decode(pkt)
    assert isinstance(msg, NetworkManagementProxy.NodeListGet)
    assert msg.seqNo == 2
    assert msg.compose() == pkt


def test_node_list_report():
    # pylint: disable=line-too-long
    pkt = b"R\x02\x02\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    msg = Message.decode(pkt)
    assert isinstance(msg, NetworkManagementProxy.NodeListReport)
    assert msg.seqNo == 2
    assert msg.status == 0
    assert msg.nodeListControllerId == 1
    assert msg.nodes == {1, 6}
    # Encoding not implemented since we do not need to send this message
    # assert msg.compose() == pkt
