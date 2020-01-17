import struct

from pyzwave.const.ZW_classcmd import COMMAND_CLASS_ZIP, COMMAND_ZIP_PACKET
from pyzwave.message import Message
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_ZIP, "ZIP")


@ZWaveMessage(COMMAND_CLASS_ZIP, COMMAND_ZIP_PACKET)
class ZipPacket(Message):
    NAME = "ZIP_PACKET"

    ZIP_PACKET_FLAGS0_ACK_REQ = 0x80
    ZIP_PACKET_FLAGS0_ACK_RES = 0x40
    ZIP_PACKET_FLAGS0_NACK_RES = 0x20
    ZIP_PACKET_FLAGS0_WAIT_RES = 1 << 4
    ZIP_PACKET_FLAGS0_NACK_QF = 1 << 3
    ZIP_PACKET_FLAGS1_HDR_EXT_INCL = 0x80
    ZIP_PACKET_FLAGS1_ZW_CMD_INCL = 0x40
    ZIP_PACKET_FLAGS1_MORE_INFORMATION = 0x20
    ZIP_PACKET_FLAGS1_SECURE_ORIGIN = 0x10
    ZIP_OPTION_EXPECTED_DELAY = 1
    ZIP_OPTION_MAINTENANCE_GET = 2
    ZIP_OPTION_MAINTENANCE_REPORT = 3

    def __init__(self, command=None):
        super().__init__()
        self._flags0 = 0
        self._flags1 = self.ZIP_PACKET_FLAGS1_SECURE_ORIGIN
        self._seqNo = 0
        self._sourceEP = 0
        self._destEP = 0
        self._ima = {}
        self._command = command

    @property
    def ackRequest(self) -> bool:
        return bool(self._flags0 & self.ZIP_PACKET_FLAGS0_ACK_REQ)

    @ackRequest.setter
    def ackRequest(self, ackRequest):
        if ackRequest:
            self._flags0 |= self.ZIP_PACKET_FLAGS0_ACK_REQ
        else:
            self._flags0 &= ~self.ZIP_PACKET_FLAGS0_ACK_REQ

    @property
    def ackResponse(self) -> bool:
        return bool(self._flags0 & self.ZIP_PACKET_FLAGS0_ACK_RES)

    @ackResponse.setter
    def ackResponse(self, ackResponse):
        if ackResponse:
            self._flags0 |= self.ZIP_PACKET_FLAGS0_ACK_RES
        else:
            self._flags0 &= ~self.ZIP_PACKET_FLAGS0_ACK_RES

    @property
    def command(self):
        return self._command

    def compose(self):
        args = [self.flags0, self.flags1, self._seqNo, self._sourceEP, self._destEP]
        if self._command:
            args.append(self._command.compose())
        return self.encode(*args)

    @property
    def destEP(self):
        return self._destEP

    @destEP.setter
    def destEP(self, destEP):
        self._destEP = destEP & 0xFF

    @property
    def flags0(self):
        return self._flags0

    @property
    def flags1(self):
        flags = self._flags1
        if self._command:
            flags |= self.ZIP_PACKET_FLAGS1_ZW_CMD_INCL
        return flags

    @property
    def nackResponse(self) -> bool:
        return bool(self._flags0 & self.ZIP_PACKET_FLAGS0_NACK_RES)

    @nackResponse.setter
    def nackResponse(self, nackResponse):
        if nackResponse:
            self._flags0 |= self.ZIP_PACKET_FLAGS0_NACK_RES
        else:
            self._flags0 &= ~self.ZIP_PACKET_FLAGS0_NACK_RES

    @property
    def seqNo(self):
        return self._seqNo

    @seqNo.setter
    def seqNo(self, seqNo):
        self._seqNo = seqNo

    @property
    def sourceEP(self):
        return self._sourceEP

    @sourceEP.setter
    def sourceEP(self, sourceEP):
        self._sourceEP = sourceEP & 0xFF

    def parse(self, pkt):
        (
            self._flags0,
            self._flags1,
            self._seqNo,
            self._sourceEP,
            self._destEP,
        ) = struct.unpack("5B", pkt[0:5])
        frame = pkt[5:]
        if self.flags1 & self.ZIP_PACKET_FLAGS1_HDR_EXT_INCL:
            extLength = frame[0]
            for optionType, optionValue in self.tlvIterator(frame[1:extLength]):
                if (optionType & 0x7F) == self.ZIP_OPTION_MAINTENANCE_REPORT:
                    for _iType, _iValue in self.tlvIterator(optionValue):
                        # TODO parse and save IMA information
                        pass
            frame = frame[extLength:]
        if not self.flags1 & self.ZIP_PACKET_FLAGS1_ZW_CMD_INCL:
            return
        self._command = Message.decode(frame)

    @property
    def zwCmdIncluded(self) -> bool:
        return self._command is not None

    @staticmethod
    def tlvIterator(pkt):
        i = 0

        while i < len(pkt):
            tlvType = pkt[i]
            length = pkt[i + 1]
            tlvValue = pkt[i + 2 : i + 2 + length]
            i = i + 2 + length
            yield (tlvType, tlvValue)
        if i != len(pkt):
            raise Exception("BAD TLV")
