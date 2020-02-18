# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=unidiomatic-typecheck
# pylint: disable=singleton-comparison

import pytest
from pyzwave.commandclass import NetworkManagementProxy, Zip
from pyzwave.message import Message
from pyzwave.types import BitStreamReader


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
    # pylint: disable=line-too-long
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


def test_zip_packet_response():
    # pylint: disable=line-too-long
    pkt = b"#\x02\x00\xd0`\x00\x00\x05\x84\x02\x04\x00R\x02\x01\x00\x01!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    msg = Message.decode(pkt)
    assert isinstance(msg, Zip.ZipPacket)
    reply = msg.response(success=True)
    assert reply.ackRequest == False
    assert reply.ackResponse == True
    assert reply.nackResponse == False
    assert reply.nackWaiting == False
    assert reply.nackQueueFull == False
    assert reply.nackOptionError == False
    assert reply.seqNo == msg.seqNo
    reply = msg.response(success=False, nackQueueFull=True)
    assert reply.ackRequest == False
    assert reply.ackResponse == False
    assert reply.nackResponse == True
    assert reply.nackWaiting == False
    assert reply.nackQueueFull == True
    assert reply.nackOptionError == False
    assert reply.seqNo == msg.seqNo


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    "header,includedReport",
    [
        (
            b"\x1e\x03\x1b\x00\x01\x00\x01\x02\x00m\x02\x054\x00\x00\x00\x02\x03\x05~\x7f\x7f\x7f\x7f\x04\x01\x01\x05\x01\x01",
            Zip.ZIPPacketOptionType.MAINTENANCE_REPORT,
        ),
        (
            b"\x05\x84\x02\x04\x00_\x03\x01",
            Zip.ZIPPacketOptionType.ENCAPSULATION_FORMAT_INFORMATION,
        ),
    ],
)
def test_zip_packet_ima(header, includedReport):
    data = Zip.HeaderExtension.deserialize(BitStreamReader(header))
    hdr = Zip.HeaderExtension()
    hdr.__setstate__(data)
    assert hdr.get(includedReport)
