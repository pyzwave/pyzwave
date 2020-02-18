# pyzwave

[![Coverage Status](https://coveralls.io/repos/github/pyzwave/pyzwave/badge.svg?branch=master)](https://coveralls.io/github/pyzwave/pyzwave?branch=master)

**[pyzwave](https://github.com/pyzwave/pyzwave)** is **[Z-Wave](https://en.wikipedia.org/wiki/Z-Wave)** library to implement the **[Z-Wave](https://www.z-wave.com/)** standard as a Python 3 library.

**[pyzwave](https://github.com/pyzwave/pyzwave)** is inspired by **[zigpy](https://github.com/zigpy/zigpy)**.

## Compatible hardware

pyzwave uses **[Z/IP Gateway](https://www.silabs.com/products/development-tools/software/z-wave/controller-sdk/z-ip-gateway-sdk)** to talk with the hardware. Any hardware working with Z/IP Gateway should work with pyzwave. Z/IP Gateway requires the Z-Wave chip to be running the bridge firmware which unfortunately not all adapters do.

pyzwave could be adapted to talk directly with a non bridge controller but due to a signed NDA the source for this cannot be open sourced by **[Telldus Technologies AB](https://telldus.com)** (the author behind this library).

## Status

**[Z/IP Gateway](https://www.silabs.com/products/development-tools/software/z-wave/controller-sdk/z-ip-gateway-sdk)** requires the connection between this library to be encrypted using DTLS. This library includes a connection using DTLS but unfortunately unsolicited reports does not yet work using this.

A workaround until this issue is resolved is to recompile Z/IP gateway to not use DTLS for the connection. Any help getting the DTLS fully supported is welcome.

## How to contribute

If you are looking to make a contribution to this project we suggest that you follow the steps in these guides:

- [First Contributions](https://github.com/firstcontributions/first-contributions/blob/master/README.md)
- [First Contributions (GitHub Desktop Edition)](https://github.com/firstcontributions/first-contributions/blob/master/github-desktop-tutorial.md)

Some developers might also be interested in receiving donations in the form of hardware such as Z-Wave modules or devices, and even if such donations are most often donated with no strings attached it could in many cases help the developers motivation and indirect improve the development of this project.
