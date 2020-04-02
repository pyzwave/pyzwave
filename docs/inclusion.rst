Node inclusion
==========================================

To include a node start inclusion mode in the controller with
:func:`Adapter.addNode() <pyzwave.adapter.Adapter.addNode>`.
Status about the inclusion are sent as
:class:`NetworkManagementInclusion.NodeAddStatus <pyzwave.commandclass.NetworkManagementInclusion.NodeAddStatus>` messages

zipgateway send back secure inclusion callback using messages
:class:`NetworkManagementInclusion.NodeAddKeysReport <pyzwave.commandclass.NetworkManagementInclusion.NodeAddKeysReport>` and
:class:`NetworkManagementInclusion.NodeAddDSKReport <pyzwave.commandclass.NetworkManagementInclusion.NodeAddDSKReport>`

Non secure inclusion
--------------------

To force the node to be included non secure respond to
:class:`NodeAddKeysReport <pyzwave.commandclass.NetworkManagementInclusion.NodeAddKeysReport>` with
a :class:`NodeAddKeysSet <pyzwave.commandclass.NetworkManagementInclusion.NodeAddKeysSet>` message with
the attributes set to::

  grantCSA = False
  accept = False
  grantedKeys = 0

.. code::

  await adapter.addNodeKeysSet(False, False, 0)

S0 inclusion
------------

To force S0 inclusion respond to :class:`NodeAddKeysReport <pyzwave.commandclass.NetworkManagementInclusion.NodeAddKeysReport>`
with the key set to
:any:`SECURITY_0_NETWORK_KEY <pyzwave.commandclass.NetworkManagementInclusion.Keys.SECURITY_0_NETWORK_KEY>`:

.. code::

  await adapter.addNodeKeysSet(False, True, NetworkManagementInclusion.Keys.SECURITY_0_NETWORK_KEY)

S2 inclusion
------------

To continue with S2 bootstrapping respond the requested keys from the node to the controller:

.. code::

  async def messageReceived(self, _sender, message: Message):
    if isinstance(message, NodeAddKeysReport):
      await adapter.addNodeKeysSet(False, True, message.requestedKeys)

Depending on the security class requested the user may or may not complete the input
of the DSK (device specific key). The controller uses the
:class:`NetworkManagementInclusion.NodeAddDSKReport <pyzwave.commandclass.NetworkManagementInclusion.NodeAddDSKReport>`
message for this. Example:

.. code::

  async def messageReceived(self, _sender, message: Message):
    if isinstance(message, NodeAddDSKReport):
      if message.inputDSKLength == 0:
         # Unauthenticated S2. No input from the user needed.
         # User may confirm the dsk in message.dsk is the same
         # as the label in the including node
         if await confirmDSK(message.dsk):
           await adapter.addNodeDSKSet(True, 0, b'')
         else:
           await adapter.addNodeDSKSet(False, 0, b'')
      else:
         # Let the user enter the missing section from the dsk
         # to finish S2 bootstrapping
         userInput = await requestUserInput(message)
         await adapter.addNodeDSKSet(True, message.inputDSKLength, userInput)
