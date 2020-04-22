Sleeping nodes (battery operated)
==========================================

To talk with battery operated nodes the messages must be queued until the node is awake.

The node will use the WAKE_UP command class to notify when the node is awake. Zipgateway
contains a mailbox proxy to help with queuing the messages. Using this is optional and
the queueing can be implemented by the end application instead.

Mailbox service
---------------

To use the mailbox proxy in Zipgateway the application must have a
:class:`MailboxService <pyzwave.mailbox.MailboxService>` configured.
The ip address and port should be the same as the :class:`ZipGateway <pyzwave.zipgateway.ZIPGateway>`
is configured to listen on.

.. code::

  import ipaddress
  from pyzwave.mailbox import MailboxService

  mailbox = MailboxService(adapter)
  await mailbox.initialize(ipaddress.IPv6Address("::ffff:c0a8:31"), 4123)

Sending messages
----------------

When a :class:`MailboxService <pyzwave.mailbox.MailboxService>` has been configured the
:func:`Adapter.send() <pyzwave.adapter.Adapter.send>` method will block until the node
either wakes up or is considered dead.

This can be a long time (week or even months). Please make sure the code can handle this.
