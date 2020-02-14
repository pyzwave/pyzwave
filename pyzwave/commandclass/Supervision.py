from pyzwave.message import Message
from pyzwave.types import BitStreamReader, bits_t, flag_t, reserved_t, uint8_t
from . import ZWaveMessage, registerCmdClass


COMMAND_CLASS_SUPERVISION = 0x6C
SUPERVISION_GET = 0x01
SUPERVISION_REPORT = 0x02

registerCmdClass(COMMAND_CLASS_SUPERVISION, "SUPERVISION")


@ZWaveMessage(COMMAND_CLASS_SUPERVISION, SUPERVISION_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_SUPERVISION SUPERVISION_GET"""

    NAME = "SUPERVISION_GET"

    attributes = (
        ("statusUpdates", flag_t),
        ("-", reserved_t(1)),
        ("sessionID", bits_t(6)),
        ("command", Message),
    )

    @staticmethod
    def parse_command(stream: BitStreamReader):  # pylint: disable=invalid-name
        """Parse the length prefixed command"""
        length = stream.byte()
        return Message.decode(stream.value(length))


@ZWaveMessage(COMMAND_CLASS_SUPERVISION, SUPERVISION_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_SUPERVISION SUPERVISION_REPORT"""

    NAME = "SUPERVISION_REPORT"

    attributes = (
        ("moreStatusUpdates", flag_t),
        ("wakeUpRequest", flag_t),  # Version 2
        ("sessionID", bits_t(6)),
        ("status", uint8_t),
        ("duration", uint8_t),
    )
