.. pyzwave documentation master file, created by
   sphinx-quickstart on Fri Feb 21 14:08:58 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyzwave's documentation!
===================================


Quickstart
----------

To setup pyzwave you need three things. The application, an adapter
and a storage module.

.. code::

    from pyzwave.application import Application
    from pyzwave.zipgateway import ZIPGateway
    from pyzwave.persistantstorage import YamlStorage

    PSK = "123456789012345678901234567890AA"

    adapter = ZIPGateway("192.168.0.169", psk=bytes.fromhex(PSK))
    await adapter.connect()
    storage = YamlStorage("/tmp/")
    app = Application(adapter, storage)
    await app.startup()

Composing and sending messages
------------------------------

To compose messages this is done in object oriented way.
Example for requesting a sensor value from a node supporting sensor multilevel

.. code::

    from pyzwave.commandclass import SensorMultilevel

    node = app.nodes["5:0"]
    message = SensorMultilevel.Get(
        sensorType=SensorMultilevel.SensorType.TEMPERATURE,
        scale=0
    )
    report = await node.sendAndReceive(message, SensorMultilevel.Report)
    print(report.debugString())


.. toctree::
   :hidden:
   :caption: Content
   :maxdepth: 2

   inclusion
   reference/pyzwave
