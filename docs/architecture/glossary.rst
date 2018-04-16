Glossary
========================

.. glossary::

  BEL
  BLE
  Basic element (BEL) or basic logic element (BLE)
    BELs or BLEs are the basic logic elements in an FPGA, including
    carry or fast adders (CFAs), flip flops (FFs), lookup tables (LUTs),
    multiplexers (MUXes), and other element types.
    Note: Programmable interconnects (PIPs) are not counted as BELs.

    BELs come in two forms:

    * Basic BEL - A logic unit which does things.
    * Routing BEL - A unit which is statically configured at routing time.
     

  Bitstream
    Binary data that is directly loaded into an FPGA to perform configuration.
    Contains configuration :term:`frames <frame>` as well as programming
    sequences and other commands required to load and activate same.

  Clock domain
    Portion of a :term:`horizontal clock row` to one side of the global clock
    spine. Often refers to :term:`tiles <tile>` that are associated with these
    clocks.

  Column
    A term used in :term:`bitstream` configuration to denote
    a collection of :term:`tiles <tile>`, physically organized as
    a vertical line, and configured by the same set of configuration frames.
    Logic columns span 50 tiles vertically and 2 tiles horizontally
    (pairs of logic tiles and interconnect tiles).

  CLB
  Configurable logic block (CLB)
    The configurable logic unit of an FPGA. Also called a **logic cell**.
    A CLB is a combination of basic logic elements (:term:`BELs <BEL>`).

  Database
    Text files containing meaningful labels for bit positions within
    :term:`segments <segment>`.

  Frame
    The fundamental unit of :term:`bitstream` configuration data consisting of
    101 :term:`words <word>`.
    Each frame has a 32-bit frame address and 101 payload words, 32 bits each.
    The 50th payload word is an EEC.
    The 7 LSB bits of the frame address are the frame index within the
    configuration :term:`column` (called *minor frame address* in the Xilinx
    documentation). The rest of the frame address identifies the configuration
    column (called *base frame address* in Project X-Ray nomenclature).

    The bits in an individual frame are spread out over the entire column.
    For example, in a logic column with 50 tiles, the first tile is configured
    with the first two words in each frame, the next tile with the next two
    words, and so on.
    
  Frame base address
    The first configuration frame address for a :term:`column`. A frame base
    address has always the 7 LSB bits cleared.

  Fuzzer
    Scripts and a makefile to generate one or more :term:`specimens <specimen>`
    and then convert the data from those specimens into a :term:`database`.

  Half
    Portion of a device defined by a virtual line dividing the two sets of global
    clock buffers present in a device. The two halves are referred to as
    the top and bottom halves.

  Node
    A routing node on the device. A node is a collection of :term:`wires <wire>`
    spanning one or more :term:`tiles <tile>`.
    Nodes that are local to a tile map 1:1 to a wire. A node that spans multiple
    tiles maps to multiple wires, one in each tile it spans.

  PIP
  Programmable interconnect point (PIP)
    Connection point between two wires in a tile that may be enabled or
    disabled by the configuration.

  Horizontal clock row
    Portion of a device including 12 horizontal clocks and the 50 interconnect
    and function tiles associated with them. A :term:`half` contains one or
    more horizontal clock rows and each half may have a different number of
    rows.
    
  ROI
  Region of interest (ROI)
    A term used in *Project X-Ray* to denote a
    rectangular region on the FPGA that is the current focus of our study.
    The current region of interest is `SLICE_X12Y100:SLICE_X27Y149`
    on a `xc7a50tfgg484-1` chip.

  Segment
    All configuration bits for a horizontal slice of a :term:`column`.
    This corresponds to two ranges: a range of :term:`frames <frame>`
    and a range of :term:`words <word>` within frames. A segment of a logic
    column is 36 frames wide and 2 words high.

  Site
    Portion of a tile where :term:`BELs <BEL>` can be placed. The
    :term:`slices <slice>` in a :term:`CLB` tile are sites.

  Slice
    Portion of a :term:`tile` that contains :term:`BELs <BEL>`.
    A `CLBLL_L/CLBLL_R` tile contains two `SLICEL` slices.
    A `CLBLM_L/CLBLM_R` tile contains one `SLICEL` slice and one `SLICEM` slice.

  Specimen
    A :term:`bitstream` of a (usually auto-generated) design with additional
    files containing information about the placed and routed design.
    These additional files are usually generated using Vivado TCL scripts
    querying the Vivado design database.

  Tile
    Fundamental unit of physical structure containing a single type of
    resource or function. A container for :term:`sites <site>` and
    :term:`slices <slice>`. The whole chip is a grid of tiles.

    The most important tile types are left and right interconnect tiles
    (`INT_L` and `INT_R`) and left and right :term:`CLB` logic/memory tiles
    (`CLBLL_L`, `CLBLL_R`, `CLBLM_L`, `CLBLM_R`).

  Wire
    Physical wire within a :term:`tile`.

  Word
    32 bits stored in big-endian order. Fundamental unit of :term:`bitstream`
    format. 
