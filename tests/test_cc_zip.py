import pytest
from pyzwave.commandclass import NetworkManagementProxy, Zip
from pyzwave.message import Message


def test_zip_packet_networkmanagementproxt_nodelistget():
    pkt = b"#\x02\x80P\x02\x00\x00R\x01\x02"
    msg = Message.decode(pkt)
    assert isinstance(msg, Zip.ZipPacket)
    assert msg.ackRequest == True
    assert msg.ackResponse == False
    assert msg.nackResponse == False
    assert msg.nackWaiting == False
    assert msg.nackQueueFull == False
    assert msg.nackOptionError == False
    assert msg.headerExtIncluded == False
    assert msg.zwCmdIncluded == True
    assert msg.moreInformation == False
    assert msg.secureOrigin == True
    assert msg.seqNo == 2
    assert msg.sourceEP == 0
    assert msg.destEP == 0
    assert type(msg.command) is NetworkManagementProxy.NodeListGet
    assert msg.compose() == pkt


def test_zip_packet_networkmanagementproxt_nodelistreport():
    pkt = b"#\x02\x00\xd0`\x00\x00\x05\x84\x02\x04\x00R\x02\x01\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    msg = Message.decode(pkt)
    assert isinstance(msg, Zip.ZipPacket)
    assert msg.ackRequest == False
    assert msg.ackResponse == False
    assert msg.nackResponse == False
    assert msg.nackWaiting == False
    assert msg.nackQueueFull == False
    assert msg.nackOptionError == False
    assert msg.headerExtIncluded == True
    assert msg.zwCmdIncluded == True
    assert msg.moreInformation == False
    assert msg.secureOrigin == True
    assert msg.seqNo == 96
    assert msg.sourceEP == 0
    assert msg.destEP == 0
    assert type(msg.command) is NetworkManagementProxy.NodeListReport


def test_zip_tlv():
    for header, value in Zip.HeaderExtension.tlvIterator(b"\x84\x02\x04\x00"):
        assert header == 132
        assert value == b"\x04\x00"


def test_zip_tlv_bad_value():
    with pytest.raises(ValueError):
        for _ in Zip.HeaderExtension.tlvIterator(b"\x84\x04\x04\x00"):
            pass
