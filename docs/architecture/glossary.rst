Glossary
========================

.. glossary::

  ASIC
    An application-specific integrated circuit (ASIC) is a chip that is
    designed and used for a specific purpose, such as video acceleration,
    machine learning acceleration, and many more purposes. In contrast to
    :term:`FPGAs <FPGA>`, the programming of an ASIC is fixed at the time of
    manufacture.

  basic element
  BEL
  basic logic element
  BLE
    Basic elements (BELs) or basic logic element (BLEs)
    are the basic logic units in an :term:`FPGA`, including
    carry or fast adders (:term:`CFAs <cfa>`), flip flops (:term:`FFs <ff>`),
    lookup tables (:term:`LUTs <lut>`), multiplexers (:term:`MUXes <mux>`), and
    other element types. Note: Programmable interconnects (:term:`PIPs <pip>`)
    are not counted as BELs.

    BELs come in two forms:

    * Basic BEL - A logic unit which does things.
    * Routing BEL - A unit which is statically configured at routing time.
     

  Bitstream
    Binary data that is directly loaded into an :term:`FPGA` to perform
    configuration. Contains configuration :term:`frames <frame>` as well as
    programming sequences and other commands required to load and activate same.

  CFA
    A carry or fast adder (CFA) is a logic element on the :term:`FPGA` that
    performs fast arithmetic operations.

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
  Configurable logic block
    A configurable logic block (CLB) is the configurable logic unit of an
    :term:`FPGA`. Also called a **logic cell**. A CLB is a combination of basic
    logic elements (:term:`BELs <bel>`).

  Database
    Text files containing meaningful labels for bit positions within
    :term:`segments <segment>`.

  FF
  Flip flop
    A flip flop (FF) is a logic element on the :term:`FPGA` that stores state.

  FPGA
    A field-programmable gate array (FPGA) is a reprogrammable integrated
    circuit, or chip. Reprogrammable means you can reconfigure the integrated
    circuit for different types of computing. You define the configuration via a
    hardware definition language (:term:`HDL`). The word "field" in
    *field-programmable gate array* means the circuit is programmable
    *in the field*, as opposed to during chip manufacture.

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

  HDL
    You use a hardware definition language (HDL) to describe the behavior of an
    electronic circuit. Popular HDLs include Verilog (inspired by C) and VHDL
    (inspired by Ada).

  Horizontal clock row
    Portion of a device including 12 horizontal clocks and the 50 interconnect
    and function tiles associated with them. A :term:`half` contains one or
    more horizontal clock rows and each half may have a different number of
    rows.

  I/O block
    One of the configurable input/output blocks that connect the :term:`FPGA`
    to external devices.

  LUT
    A lookup table (LUT) is a logic element on the :term:`FPGA`. LUTs function
    as a ROM, apply combinatorial logic, and generate the output value for a
    given set of inputs.

  MUX
    A multiplexer (MUX) is a multi-input, single-output switch controled by
    logic.

  Node
    A routing node on the device. A node is a collection of :term:`wires <wire>`
    spanning one or more :term:`tiles <tile>`.
    Nodes that are local to a tile map 1:1 to a wire. A node that spans multiple
    tiles maps to multiple wires, one in each tile it spans.

  PIP
  Programmable interconnect point
    A programmable interconnect point (PIP) is a connection point between two
    wires in a tile that may be enabled or disabled by the configuration.

  PnR
  Place and route
    Place and route (PnR) is the process of taking logic and placing it into
    hardware logic elements on the :term:`FPGA`, and then routing the signals
    between the placed elements. 

  ROI
  Region of interest
    Region of interest (ROI) is used in *Project X-Ray* to denote a
    rectangular region on the :term:`FPGA` that is the focus of our study.
    The current region of interest is `SLICE_X12Y100:SLICE_X27Y149`
    on a `xc7a50tfgg484-1` chip.

  Routing fabric
    The :term:`wires <wire>` and programmable interconnects (:term:`PIPs <pip>`)
    connecting the logic blocks in an :term:`FPGA`.

  Segment
    All configuration bits for a horizontal slice of a :term:`column`.
    This corresponds to two ranges: a range of :term:`frames <frame>`
    and a range of :term:`words <word>` within frames. A segment of a logic
    column is 36 frames wide and 2 words high.

  Site
    Portion of a tile where :term:`BELs <bel>` can be placed. The
    :term:`slices <slice>` in a :term:`CLB` tile are sites.

  Slice
    Portion of a :term:`tile` that contains :term:`BELs <bel>`.
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
