# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from pyzwave.commandclass import Basic
from pyzwave.message import Message


def test_report():
    pkt = b"\x20\x03\x02"
    msg = Message.decode(pkt)
    assert isinstance(msg, Basic.Report)
    assert msg.value == 2
    assert msg.compose() == pkt
