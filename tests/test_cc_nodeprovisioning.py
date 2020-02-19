# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from pyzwave.message import Message


def test_ListIterationReport():
    # pylint: disable=line-too-long
    pkt = b"x\x04\x02\x01\x10~Mp\x22\xf1\xd9\xb4\xa9\xa8\x13\xd6\nlr\xa4\xe0m\x01\x01i\x01\x00n\x02\x00\x00"
    msg = Message.decode(pkt)
    assert msg.seqNo == 2
    assert msg.remainingCount == 1
    assert msg.dsk == "32333-28706-61913-46249-43027-54794-27762-42208"
