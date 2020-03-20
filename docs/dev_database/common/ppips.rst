===========
ppips files
===========

The *ppips files* are generated for every FPGA :term:`tile <Tile>` type.
They store the information about the pseudo-PIPs, inside the tile.

Programable Interconnect Point (:term:`PIP <PIP>`) is a connection inside the
:term:`tile <Tile>` that can be enabled or disabled. Pseudo PIPs appear as standard
:term:`PIPs <PIP>` in the Vivado tool, but they do not have actual configuration
bit pattern in segbits files (they are not configurable).

The *ppips files* contains the information which `PIPs <PIP>` do not have
configuration bits, which allows the tools to not generat error in that situation.
On the other hand this information is used to indicate that the connection
between wires is always on.

Naming convention
-----------------

The naming scheme for the PPIPs files is the following::

   ppips_<tile>.db

For example:

   - ``ppips_dsp_l.db``
   - ``ppips_clbll_l.db``
   - ``ppips_bram_int_interface_l.db``

File format
-----------

The file contains one entry per pseudo-PIP, each with one of the following
three tags: ``always``, ``default`` or ``hint``. The entries are of the form:::

   <ppip_location> <tag>

The tag ``always`` is used for pseudo-PIPs that are actually always-on, i.e.,
that are permanent connections between two wires.

The tag ``default`` is used for pseudo-PIPs that represent the default behavior
if no other driver has been configured for the destination net
(all default pseudo-PIPs connect to the VCC_WIRE net).

The tag ``hint`` is used for PIPs that are used by Vivado to tell the router
that two logic slice outputs drive the same value, i.e., behave like they
are connected as far as the routing process is concerned.

Example
-------

Below there is a part of artix7 ``ppips_clbll_l.db`` file::

   <...>
   CLBLL_L.CLBLL_L_A.CLBLL_L_A6 hint
   CLBLL_L.CLBLL_L_AMUX.CLBLL_L_A hint
   CLBLL_L.CLBLL_L_AX.CLBLL_BYP0 always
   CLBLL_L.CLBLL_L_B.CLBLL_L_B1 hint
   CLBLL_L.CLBLL_L_B.CLBLL_L_B2 hint
   CLBLL_L.CLBLL_L_B.CLBLL_L_B3 hint
   CLBLL_L.CLBLL_L_B.CLBLL_L_B4 hint
   <...>

The ``<ppip_location>`` name is arbitrary. However, the naming convention is
similar to the one in the Vivado tool, which allows for quick identification of their role in the FPGA chip.
