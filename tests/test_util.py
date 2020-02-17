# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-self-use
# pylint: disable=unidiomatic-typecheck
# pylint: disable=blacklisted-name
import asyncio
import logging
from unittest.mock import MagicMock

import pytest

from pyzwave.util import AttributesMixin, Listenable
from pyzwave.types import BitStreamReader, float_t, uint8_t


class Speaker(Listenable):
    pass


class Listener:
    def __init__(self):
        self.fooCalled = False

    def hello(self, speaker):
        logging.warning("Hello was called")

    async def foo(self, speaker):
        self.fooCalled = True
        return 42

    def enrage(self, speaker):
        raise Exception("This is outragous!")


class CustomAttribute(str):
    def __init__(self):
        super().__init__()
        self.content = ""

    def __setstate__(self, state):
        self.content = str(state)

    def __getstate__(self):
        return self.content

    def __str__(self):
        return str(self.content)


class AnotherAttributable(AttributesMixin):
    attributes = (
        ("foo", uint8_t),
        ("bar", uint8_t),
        ("custom", CustomAttribute),
    )

    def parse_custom(self, reader):
        return ""


class Attributable(AttributesMixin):
    attributes = (
        ("foo", uint8_t),
        ("bar", uint8_t),
        ("floating", float_t),
        ("custom", CustomAttribute),
        ("native", int),
        ("recursive", AnotherAttributable),
    )


@pytest.fixture
def attributable() -> Attributable:
    return Attributable()


@pytest.fixture
def speaker():
    return Speaker()


@pytest.fixture
def listener():
    return Listener()


def test_attributes(attributable: Attributable):
    assert attributable.foo == 0
    assert attributable.bar == 0
    assert attributable.floating == 0.0
    assert attributable.custom == ""
    assert attributable.native == 0
    attributable.foo = 1
    attributable.bar = 2
    attributable.floating = (22.3, 2, 1)
    attributable.custom = "3"
    attributable.native = 4
    assert attributable.foo == 1
    assert attributable.bar == 2
    assert attributable.floating == 22.3
    assert attributable.floating.scale == 1
    assert str(attributable.custom) == "3"
    assert attributable.native == 4
    assert isinstance(attributable.foo, uint8_t)
    assert type(attributable.native) == int


def test_attributes__init__():
    another = AnotherAttributable()
    attributable = Attributable(foo=0, custom="hello", recursive=another)
    assert attributable.foo == 0
    assert str(attributable.custom) == "hello"
    assert attributable.recursive == another


def test_attributes_parseAttributes():
    pkt = b"\x01\x02"
    attributable = AnotherAttributable()
    attributable.parseAttributes(BitStreamReader(pkt))
    assert attributable.foo == 1
    assert attributable.bar == 2


def test_attributes_state(attributable: Attributable):
    assert attributable.__getstate__() == {}
    attributable.__setstate__({"foo": 1, "bar": 2, "custom": 3, "native": 4})
    state = attributable.__getstate__()
    assert attributable.foo == 1
    assert attributable.bar == 2
    assert str(attributable.custom) == "3"
    assert state == {"foo": 1, "bar": 2, "custom": "3", "native": 4}
    assert isinstance(attributable.foo, uint8_t)


def test_listen(speaker: Speaker, listener: Listener):
    listener.hello = MagicMock()
    speaker.addListener(listener)
    speaker.speak("hello")
    listener.hello.assert_called_once()


@pytest.mark.asyncio
async def test_speaker_ask(speaker: Speaker, listener: Listener):
    speaker.addListener(listener)
    assert listener.fooCalled is False
    retval = await speaker.ask("foo")
    assert listener.fooCalled is True
    assert retval == [42]


@pytest.mark.asyncio
async def test_speaker_async_listener(speaker: Speaker, listener: Listener):
    speaker.addListener(listener)
    assert listener.fooCalled is False
    await asyncio.gather(*speaker.speak("foo"))
    assert listener.fooCalled is True


def test_speaker_no_listener(speaker: Speaker, listener: Listener):
    # Check that no exception is raised if there is no listener
    speaker.addListener(listener)
    speaker.speak("world")


def test_speaker_listener_exception(speaker: Speaker, listener: Listener):
    # The exception should not propagate
    speaker.addListener(listener)
    speaker.speak("enrage")
