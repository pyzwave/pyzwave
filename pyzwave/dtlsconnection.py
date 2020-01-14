# -*- coding: utf-8 -*-

import asyncio
import logging
import ssl
import socket
import threading

from ctypes import (
    c_char,
    c_char_p,
    c_int,
    c_uint,
    c_void_p,
    CFUNCTYPE,
    POINTER,
    memmove,
    memset,
)

import dtls
import _ssl


dtls.do_patch()

_LOGGER = logging.getLogger(__name__)

SSL_CB_ALERT = 0x4000  # /* used in callback */

CLIENTPSKFUNC = CFUNCTYPE(
    c_uint, c_void_p, c_char_p, POINTER(c_char), c_uint, POINTER(c_char), c_uint
)
CLIENTCBFUNC = CFUNCTYPE(None, c_void_p, c_int, c_int)


class DTLSConnection(threading.Thread):
    def __init__(self):
        super().__init__(name="Z-Wave DTLS connection")
        self._address = None
        self._psk = None
        self._running = False
        self._sock = None
        self._connectionEvent = asyncio.Event()
        self._loop = asyncio.get_event_loop()
        self.setDaemon(True)

        self.clientPskCbWrapper = CLIENTPSKFUNC(self.clientPskCb)
        self.clientCbWrapper = CLIENTCBFUNC(self.clientCb)

    async def connect(self, address, psk):
        self._address = address
        self._psk = psk
        self._connectionEvent.clear()
        self.start()
        await self._connectionEvent.wait()

    def run(self):
        self._sock = self.createDtlsPskSock(self._address, self._psk)
        self._loop.call_soon_threadsafe(self._connectionEvent.set)
        self._running = True
        while self._running:
            try:
                pkt = self._sock.recv(1500)
                if self._onMessage:
                    self._loop.call_soon_threadsafe(self._onMessage, pkt)
            except AttributeError:
                _LOGGER.error("Got attribute error!")
            except Exception as error:
                _LOGGER.error("Could not read from zipgateway %s", error)
                break

    def send(self, msg):
        if not self._sock:
            _LOGGER.error("Could not send, not yet connected!")
            return
        self._sock.send(msg)

    def onMessage(self, cbfn):
        self._onMessage = cbfn

    def stop(self):
        self._running = False

    def clientPskCb(self, ssl, hint, identity, max_idenity_len, cpsk, max_psk_len):
        (iden, pypsk) = (
            "Client_identity",
            self._psk,
        )
        l = len(pypsk)
        memmove(cpsk, pypsk, l)
        if iden:
            memmove(identity, iden.encode("utf-8"), len(iden))
        else:
            memset(identity, 0, 1)
        return l

    def clientCb(self, ssl, where, ret):

        if where & SSL_CB_ALERT and self._sock._connected:

            print("Client Alert", where, ret, self._sock._connected)
            # sock.unwrap();
            self._sock._connected = True

            self._sock._sslobj = _ssl.sslwrap(
                self._sock._sock,
                False,
                None,
                None,
                _ssl.CERT_NONE,
                _ssl.PROTOCOL_SSLv23,
                None,
                None,
            )

            self._sock.do_handshake()
            # try:
            # 	dtls.openssl.SSL_shutdown(sock._sslobj._ssl.value);
            # except:
            # 	pass
            # sock.shutdown(socket.SHUT_WR)

    def createDtlsPskSock(self, address, psk):
        sock = ssl.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
            do_handshake_on_connect=False,
            ciphers="PSK",
        )
        # sock.setblocking(True)
        # sock.settimeout(20.0)
        sock.connect((address, 41230))

        # Using ctypes we interface with the function SSL_set_psk_client_callback from OpenSSL
        proto = (
            "SSL_set_psk_client_callback",
            dtls.openssl.libssl,
            ((None, "ret"), (dtls.openssl.SSL, "ctx"), (c_void_p, "psk_client_cb")),
        )
        dtls.openssl._make_function(*proto)

        proto = (
            "SSL_set_info_callback",
            dtls.openssl.libssl,
            ((None, "ret"), (dtls.openssl.SSL, "ctx"), (c_void_p, "callback")),
        )
        dtls.openssl._make_function(*proto)

        # pylint: disable=no-member
        dtls.openssl.SSL_set_psk_client_callback(
            sock._sslobj._ssl.value, self.clientPskCbWrapper
        )

        dtls.openssl.SSL_set_info_callback(
            sock._sslobj._ssl.value, self.clientCbWrapper
        )

        sock.do_handshake()
        return sock
