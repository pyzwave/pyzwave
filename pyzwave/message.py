import logging

from pyzwave.types import BitStreamReader, BitStreamWriter
from pyzwave.util import AttributesMixin

_LOGGER = logging.getLogger(__name__)


class Message(AttributesMixin):
    """Base class for all Z-Wave messages. This class should not be initiated manually"""

    NAME = None

    def cmdClass(self) -> int:
        """Return the command class id for this message"""
        return (self.hid() >> 8) & 0xFF

    def compose(self) -> bytes:
        """Convert the message to a bytearray ready to be sent over the wire"""
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(self.__class__, (None, None))
        if cmdClass is None or cmd is None:
            # Pure Message object, encode to empty bytes
            return b""
        stream = BitStreamWriter()
        stream.addBytes(cmdClass, 1, False)
        stream.addBytes(cmd, 1, False)
        for name, attrType in self.attributes:
            if name not in self._attributes:
                default = getattr(attrType, "default", None)
                if default is not None:
                    attrType(default).serialize(stream)
                    continue
                raise AttributeError(
                    "Value for attribute '{}' in {} has not been set".format(name, self)
                )
            serializer = getattr(self, "compose_{}".format(name), None)
            if serializer:
                serializer(stream)
                continue
            if not hasattr(self._attributes[name], "serialize"):
                raise ValueError("Cannot encode", name, self._attributes[name])
            self._attributes[name].serialize(stream)
        return bytes(stream)

    def serialize(self, stream: BitStreamWriter):
        """Write the message as binary into the bitstream. See compose()"""
        stream.extend(self.compose())

    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return self.compose() == other.compose()

    def __getattr__(self, name):
        # Default implentation in AttributesMixin returns (and sets) a default value.
        # We do not want it here. We only return default if it is explicit set.
        if name not in self._attributes:
            for attrName, attrType in getattr(self, "attributes"):
                if attrName != name:
                    continue
                return getattr(attrType, "default", None)
        return self._attributes.get(name)

    def __repr__(self):
        hid = self.hid()
        cmdClass = (hid >> 8) & 0xFF
        cmd = hid & 0xFF
        cmdClassName = cmdClasses.get(cmdClass, "0x{:02X}".format(cmdClass))
        name = self.NAME or "0x{:02X}".format(cmd)
        return "<Z-Wave {}.{}>".format(cmdClassName, name)

    @classmethod
    def decode(cls, pkt: bytearray):
        """Decode a raw bytearray into a Message object"""
        return cls.deserialize(BitStreamReader(pkt))

    @staticmethod
    def deserialize(stream: BitStreamReader):
        """Deserialize a bitstream into a Message object"""
        if stream.bytesLeft() < 2:
            return UnknownMessage(0x0000)
        cmdClass = stream.byte()
        cmd = stream.byte()
        hid = cmdClass << 8 | (cmd & 0xFF)
        MsgCls = ZWaveMessage.get(hid, None)  # pylint: disable=invalid-name
        if MsgCls:
            msg = MsgCls()
            msg.parseAttributes(stream)
        else:
            msg = UnknownMessage(hid)
        return msg

    @classmethod
    def hid(cls):
        """
        Return the command class id and command id as a single word for easier lookup
        """
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (0, 0))
        return (cmdClass << 8) | (cmd & 0xFF)


class UnknownMessage(Message):
    """
    Wrapper class for wrapping unknown messages. Using this class we still know which
    command class and command this message is (but we don't know how to decode it)
    """

    def __init__(self, hid):
        super().__init__()
        self._hid = hid

    def hid(self):
        return self._hid


# pylint: disable=wrong-import-position
from pyzwave.commandclass import ZWaveMessage, cmdClasses
