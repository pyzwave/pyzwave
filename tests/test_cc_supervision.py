# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from pyzwave.commandclass import Basic, Supervision
from pyzwave.message import Message


def test_parse_command():
    pkt = b"\x6C\x01\x03\x03\x20\x03\x02"
    msg = Message.decode(pkt)
    assert isinstance(msg, Supervision.Get)
    assert msg.sessionID == 3
    assert isinstance(msg.command, Basic.Report)
