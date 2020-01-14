# -*- coding: utf-8 -*-

import logging

_LOGGER = logging.getLogger(__name__)


class Listenable:
    def __init__(self):
        self._listeners = []

    def addListener(self, listener):
        self._listeners.append(listener)

    def speak(self, message, *args):
        for listener in self._listeners:
            method = getattr(listener, message, None)
            if not method:
                continue
            try:
                method(self, *args)
            except Exception as error:
                _LOGGER.warning("Error calling listener.%s: %s", message, error)
