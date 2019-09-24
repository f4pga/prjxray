Configuration
=============

Within an FPGA, various memories (latches, block RAMs, distributed RAMs)
contain the state of signal routing, :term:`BEL` configuration, and runtime
storage. Configuration is the process of loading an initial state into all of
these memories both to define the intended logic operations as well as set
initial data for runtime memories. Note that the same mechanisms used for
configuration are also capable of reading out the active state of these
memories as well. This can be used to examine the contents of a block RAM or
other memory at any point in the device's operation.

Addressing
----------------
As described in :ref:`architecture_overview-label`, 7-Series FPGAs are constructed
out of :term:`tiles <tile>` organized into :term:`clock domains <clock
domain>`. Each tile contains a set of :term:`BELs <BEL>` and the memories used
to configure them. Uniquely addressing each of these memories
involves first identifying the :term:`horizontal clock row`, then the tile within
that row, and finally the specific bit within the tile.

:term:`Horizontal clock row` addressing follows the hierarchical structure described
in :ref:`architecture_overview-label` with a single bit used to indicate top or bottom half
and a 5-bit integer to encode the row number. Within the row, tiles are connected to
one or more configuration busses depending on the type of tile and what configuration
memories it contains. These busses are identified by a 3-bit integer:

+---------+-------------------+---------------------+
| Address | Name              | Connected tile type |
+=========+===================+=====================+
| 000     | CLB, I/O, CLB     | Interconnect (INT)  |
+---------+-------------------+---------------------+
| 001     | Block RAM content | Block RAM (BRAM)    |
+---------+-------------------+---------------------+
| 010     | CFG_CLB           | ???                 |
+---------+-------------------+---------------------+

Within each bus, the connected tiles are organized into
:term:`columns <column>`. A column roughly
corresponds to a physical vertical line of tiles perpendicular to and centered over
the horizontal clock row. Each column contains varying amounts of configuration data
depending on the types of tiles attached to that column. Regardless of the amount,
a column's configuration data is organized into a multiple of :term:`frames <frame>`.
Each frame consists of 101 words with 100 words for the connected tiles and 1 word for
the horizontal clock row. The 7-bit address used to identify a specific frame within
the column is called the minor address.

Putting all these pieces together, a 32-bit frame address is constructed:

+-----------------+-------+
| Field           | Bits  |
+=================+=======+
| Reserved        | 31:26 |
+-----------------+-------+
| Bus             | 25:23 |
+-----------------+-------+
| Top/Bottom Half | 22    |
+-----------------+-------+
| Row             | 21:17 |
+-----------------+-------+
| Column          | 16:7  |
+-----------------+-------+
| Minor           | 6:0   |
+-----------------+-------+

CLB, I/O, CLB
^^^^^^^^^^^^^

Columns on this bus are comprised of 50 directly-attached interconnect tiles with various
kinds of tiles connected behind them. Frames are striped across the interconnect tiles
with each tile receiving 2 words out of the frame. The number of frames in a column
depends on the type of tiles connected behind the interconnect. For example, interconnect
tiles always have 26 frames and a CLBL tile has an additional 12 frames so a column of CLBs
will have 36 frames.

Block RAM content
^^^^^^^^^^^^^^^^^

As the name says, this bus provides access to the :term:`block RAM` contents.
Block RAM configuration data is accessed via the CLB, I/O, CLB bus. The mapping
of frame words to memory locations is not currently understood.

CFG_CLB
^^^^^^^

While mentioned in a few places, this bus type has not been seen in any bitstreams for Artix7
so far.

Loading sequence
----------------------

.. todo::

  Expand on these rough notes.

* Device is configured via a state machine controlled via a set of registers
* CRC of register writes is checked against expected values to verify data
  integrity during transmission.
* Before writing frame data:

  * IDCODE for configuration's target device is checked against actual device
  * Watchdog timer is disabled
  * Start-up sequence clock is selected and configured
  * Start-up signal assertion timing is configured
  * Interconnect is placed into Hi-Z state

* Data is then written by:

  * Loading a starting address
  * Selecting the write configuration command
  * Writing configuration data to data input register

    * Writes must be in multiples of the frame size
    * Multi-frame writes trigger autoincrementing of the frame address
    * Autoincrement can be disabled via bit in COR1 register.
    * At the end of a row, 2 frames of zeros must be inserted before data for the next row.

* After the write has finished, the device is restarted by:

  * Strobing a signal to activate IOB/CLB configuration flip-flops
  * Reactivate interconnect
  * Arms start-up sequence to run after desync
  * Desynchronizes the device from the configuration port

* Status register provides detail of start-up phases and which signals are asserted

Other
-----
* ECC of frame data is contained in word 50 alongside horizontal clock row configuration
* Loading will succeed even with incorrect ECC data
* ECC is primarily used for runtime bit-flip detection
