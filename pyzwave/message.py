import struct


class Message:
    NAME = None

    def __init__(self, cmdClass, cmd):
        self._cmdClass = cmdClass
        self._cmd = cmd
        self._data = None

    @property
    def cmdClass(self):
        return self._cmdClass

    @property
    def cmd(self):
        return self._cmd

    def compose(self):
        return self.encode()

    @property
    def data(self):
        return self._data

    @classmethod
    def encode(cls, *args):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (None, None))
        retval = bytearray(struct.pack("2B", cmdClass, cmd))
        for arg in args:
            if isinstance(arg, bytes):
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
        self._data = pkt

    def __repr__(self):
        cmdClassName = cmdClasses.get(
            self._cmdClass, "cmdClass 0x{:02X}".format(self._cmdClass)
        )
        name = self.NAME or "0x{:02X}".format(self._cmd)
        return "<Z-Wave {} cmd {}>".format(cmdClassName, name)

    @classmethod
    def create(cls, **kwargs):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (None, None))
        return cls(cmdClass, cmd, **kwargs)

    @staticmethod
    def decode(pkt):
        (cmdClass, cmd) = struct.unpack("2b", pkt[0:2])
        hid = cmdClass << 8 | (cmd & 0xFF)
        MsgCls = ZWaveMessage.get(hid, Message)
        msg = MsgCls(cmdClass, cmd)
        msg.parse(pkt[2:])
        return msg

    @classmethod
    def hid(cls):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (0, 0))
        return (cmdClass << 8) | (cmd & 0xFF)


from pyzwave.commandclass import ZWaveMessage, cmdClasses
