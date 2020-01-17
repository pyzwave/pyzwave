import struct
import logging

from pyzwave.types import BitStreamReader, BitStreamWriter

_LOGGER = logging.getLogger(__name__)


class Message:
    NAME = None
    attributes = ()

    def __init__(self, **kwargs):
        self._attributes = {}

    def compose(self) -> bytearray:
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(self.__class__, (None, None))
        stream = BitStreamWriter()
        stream.addBytes(cmdClass, 1, False)
        stream.addBytes(cmd, 1, False)
        for name, _ in self.attributes:
            if name not in self._attributes:
                raise AttributeError(
                    "Value for attribute {} has not been set".format(name)
                )
            self._attributes[name].serialize(stream)
        return stream

    @classmethod
    def encode(cls, *args):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (None, None))
        retval = bytearray(struct.pack("2B", cmdClass, cmd))
        for arg in args:
            if isinstance(arg, bytes):
                retval.extend(arg)
            elif isinstance(arg, bytearray):
                retval.extend(arg)
            elif isinstance(arg, int):
                retval.append(arg)
            else:
                raise ValueError(
                    "Cannot encode data of type {} as a Z-Wave message".format(
                        type(arg)
                    )
                )
        return bytes(retval)

    def parse(self, pkt):
        stream = BitStreamReader(pkt)
        for name, attrType in self.attributes:
            value = attrType.deserialize(stream)
            # This can be optimized to reduze the second loop inb __setattr__
            setattr(self, name, value)

    def __getattr__(self, name):
        return self._attributes.get(name)

    def __setattr__(self, name, value):
        attributes = getattr(self, "attributes")
        for msgAttrName, attrType in attributes:
            if msgAttrName == name:
                self._attributes[name] = attrType(value)
                return
        return super().__setattr__(name, value)

    def __repr__(self):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(self.__class__, (None, None))
        cmdClassName = cmdClasses.get(cmdClass, "cmdClass 0x{:02X}".format(cmdClass))
        name = self.NAME or "0x{:02X}".format(cmd)
        return "<Z-Wave {} cmd {}>".format(cmdClassName, name)

    @staticmethod
    def decode(pkt):
        (cmdClass, cmd) = struct.unpack("2b", pkt[0:2])
        hid = cmdClass << 8 | (cmd & 0xFF)
        MsgCls = ZWaveMessage.get(hid, Message)
        msg = MsgCls()
        msg.parse(pkt[2:])
        return msg

    @classmethod
    def hid(cls):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (0, 0))
        return (cmdClass << 8) | (cmd & 0xFF)


from pyzwave.commandclass import ZWaveMessage, cmdClasses
