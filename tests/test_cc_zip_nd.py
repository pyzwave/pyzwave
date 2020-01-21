# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=singleton-comparison

import ipaddress


from pyzwave.commandclass import ZipND
from pyzwave.message import Message


def test_zipnd_zipnodeadvertisement():
    # pylint: disable=line-too-long
    pkt = b"X\x01\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xc0\xa8\x00\xee\xea\xec\xfa\xf9"
    msg = Message.decode(pkt)
    assert isinstance(msg, ZipND.ZipNodeAdvertisement)
    assert msg.local == False
    assert msg.nodeId == 6
    assert msg.ipv6 == ipaddress.IPv6Address("::ffff:c0a8:ee")
    assert msg.homeId == 0xEAECFAF9
    assert msg.compose() == pkt
