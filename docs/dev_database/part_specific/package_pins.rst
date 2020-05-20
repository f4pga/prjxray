=================
package_pins file
=================

The ``package_pins.csv`` is a simple file that describes the pins of
the particular FPGA chip package.

File format
-----------

Every row in the file represents a single pin. Each of the pins
is characterized by:

- ``pin`` - The package pin name
- ``bank`` - The ID of *IO BANK* to which the pin is connected. It should match
  with the data from the :doc:`part file<./part>`
- ``site`` - The :term:`site <Site>` to which the pin belongs
- ``tile`` - The :term:`tile <Tile>` to which the pin belongs
- ``pin_function`` - The function of the pin

Example
-------

.. code-block::

    A1,35,IOB_X1Y97,RIOB33_X43Y97,IO_L1N_T0_AD4N_35

This line means that the pin ``A1`` which belongs to *IO BANK* ``35``,
of ``IOB_X1Y97`` :term:`site <Site>` in ``RIOB33_X43Y97`` :term:`tile <Tile>`
has ``IO_L1N_T0_AD4N_35`` function.
