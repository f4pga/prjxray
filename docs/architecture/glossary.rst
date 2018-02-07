Glossary
========================

.. glossary::

  basic element
  BEL
  basic logic element
  BLE
    For example a LUT5, LUT6, CARRY4, or MUX, but not PIPs.

    BELs come in two types:

    * Basic BEL - A logic unit which does things.
    * Routing BEL - A unit which is statically configured at the routing time.
     

  bitstream
    Binary data that is directly loaded into an FPGA to perform configuration.
    Contains configuration :term:`frames <frame>` as well as programming
    sequences and other commands required to load and activate same.

  clock domain
    Portion of a :term:`horizontal clock row` to one side of the global clock
    spine. Often refers to :term:`tiles <tile>` that are associated with these
    clocks.

  column
    Collection of :term:`tiles <tile>` physically organized as a vertical line.

  configurable logic block
  CLB
    Basic building block of logic. 

  frame
    Fundamental unit of configuration data consisting of 101 :term:`words <word>`.

  half
    Portion of a device defined by a virtual line dividing the two sets of global
    clock buffers present in a device. The two halves are simply referred to as
    the top and bottom halves.

  node
    Collection of :term:`wires <wire>` spanning one or more tiles.

  programmable interconnect point
  PIP
    Connection point between two wires in a tile that may be enabled or
    disabled by the configuration.

  horizontal clock row
    Portion of a device including 12 horizontal clocks and the 50 interconnect
    and function tiles associated with them. A :term:`half` contains one or
    more horizontal clock rows and each half may have a different number of
    rows.

  site
    Portion of a tile where :term:`BELs <BEL>` can be placed.  :term:`Slices
    <slice>` in a :term:`CLB` tile are sites.

  slice
    Portion of a :term:`CLB` tile that contains :term:`BELs <BEL>`.

  tile
    Fundamental unit of physical structure containing a single type of
    resource or function.

  wire
    Physical wire within a :term:`tile`.

  word
    32-bits stored in big-endian order. Fundamental unit of :term:`bitstream` format. 
