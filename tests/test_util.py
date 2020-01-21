# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import logging
from unittest.mock import MagicMock

import pytest

from pyzwave.util import Listenable


class Speaker(Listenable):
    pass


class Listener:
    def hello(self, speaker):
        logging.warning("Hello was called")

    def enrage(self, speaker):
        raise Exception("This is outragous!")


@pytest.fixture
def speaker():
    return Speaker()


@pytest.fixture
def listener():
    return Listener()


def test_listen(speaker: Speaker, listener: Listener):
    listener.hello = MagicMock()
    speaker.addListener(listener)
    speaker.speak("hello")
    listener.hello.assert_called_once()


def test_speaker_no_listener(speaker: Speaker, listener: Listener):
    # Check that no exception is raised if there is no listener
    speaker.addListener(listener)
    speaker.speak("world")


def test_speaker_listener_exception(speaker: Speaker, listener: Listener):
    # The exception should not propagate
    speaker.addListener(listener)
    speaker.speak("enrage")
