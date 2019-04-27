.db Files
=========

Introduction
------------

This section documents how prjxray represents the bitstream database. The databases are plain text files, using either simple line-based syntax or JSON. The databases are located in `database/<device_class>/`. The `settings.sh` file contains some configurations used by the tools that generate the database, including the region of interest (ROI, see [[Glossary]]).

These ".db" files come in two common flavors:
 * `segbits_*.db`_: encodes bitstream bits
 * `mask_*.db`_: which bits are used by a segment? Probably needs to be converted to tile

Also note: .rdb (raw db) is a convention for a non-expanded .db file (see below)

Segment bit positions
---------------------

Bit positions within a segment are written using the following notation: A two digit decimal number followed by an underscore followed by a two digit decimal number. For example `26_47`.

The first number indicates the frame address relative to the base frame address for the segment and ranges from `00` to `35` for Atrix-7 CLB segments.

The second number indicates the bit position width.

FIXME: Expand this section. We've had a couple questions around this, probably good to get a complete description of this that we can point people too. This is probably a good place to talk about tile grid and how it applies to segbit.


segbits_*.db
------------

Tag files document the meaning of individual configuration bits or bit pattern. They contain one line for each pattern. The first word (sequence of non-whitespace characters) in that line is the *configuration tag*, the remaining words in the line is the list of bits for that pattern. A bit prefixed with a `!` marks a bit that must be cleared, a bit not prefixed with a `!` marks a bit that must be set.

No configuration tag may include the bit pattern for another tag as subset. If it does then this is an indicator that there is an incorrect entry in the database. Usually this either means that a tag has additional bits in their pattern that should not be there, or that `!<bit>` entries are missing for one or more tags.

These are created by segmatch to describe bitstream IP encoding.

Example lines:
 * CLB.SLICE_X0.DFF.ZINI 31_58
   * For feature CLB.SLICE_X0.DFF.ZINI
   * Frame: 31
   * Word: 58 // 32 = 1
   * Mask: 1 << (58 % 32) = 0x04000000
   * To set an actual bitstream location, you will need to adjust frame and word by their tile base addresses
 * CLBLL_L.SLICEL_X0.AOUTMUX.A5Q !30_06 !30_08 !30_11 30_07
   * A multi bit entry. Bit 30_06 should be cleared to use this feature
 * INT_L.BYP_BOUNCE5.BYP_ALT5 always
   * A pseudo pip: feaure always active => no bits required
 * CLBLL_L.OH_NO.BAD.SOLVE <const0>
   * Internal only
   * Candidate bits exist, but they've only ever been set to 0
 * CLBLL_L.OH_NO.BAD.SOLVE <const1>
   * Internal only
   * Candidate bits exist, but they've only ever been set to 1
 * INT.FAN_ALT4.SS2END0 <m1 2> 18_09 25_08
   * Internal only
   * segmatch -m (min tag value occurrences) was given, but occurrences are below this threshold
   * ie INT.FAN_ALT4.SS2END0 occcured twice, but this is below the acceptable level (say 5)
 * INT.FAN_ALT4.SS2END0 <M 6 8> 18_09 25_08
   * Internal only
   * segmatch -M (min tag occurrences) was given, but total occurrences are below this threshold
   * First value (6) is present=1, second value (8) is present=0
   * Say -M 15, but there are 6 + 8 = 14 samples, below the acceptable threshold

Related tools:
 * segmatch: solves symbolic constraints on a bitstream to produce symbol bitmasks
 * dbfixup.py: internal tool that expands multi-bit encodings (ex: one hot) into groups. For example:
   * .rdb file with one hot: BRAM.RAMB18_Y1.WRITE_WIDTH_A_18 27_267
   * .db: file expanded: BRAM.RAMB18_Y1.WRITE_WIDTH_A_18 !27_268 !27_269 27_267
 * parsedb.py: valides that a database is fully and consistently solved
   * Optionally outputs to canonical form
   * Ex: complains if const0 entries exist
   * Ex: complains if symbols are duplicated (such as after a mergedb after rename)
 * mergedb.sh: adds new bit entries to an existing db
   * Ex: CLB is solved by first solving LUT bits, and then solving FF bits


Interconnect :term:`PIP <pip>` Tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tags for interconnect :term:`PIPs <pip>` are stored in the `segbits_int_l.db` and `segbits_int_r.db` database files.

Tags that enable interconnect :term:`PIPs <pip>` have the following syntax: `<tile_type>.<destination_wire>.<source_wire>`.

The `<tile_type>` may be `INT_L` or `INT_R`. The destination and source wires are wire names in that tile type. For example, consider the following entry in `segbits_int_l.db`: `INT_L.NL1BEG1.NN6END2 07_32 12_33`

FIXME: This is probably a good place to reference tileconn as the documentation that explains how wires are connected outside of switchboxes (which is what pips document).

This means that the bits `07_32` and `12_33` must be set in the segment to drive the value from the wire `NN6END2` to the wire `NL1BEG1`.

CLB Configurations Tags
^^^^^^^^^^^^^^^^^^^^^^^

Tags for CLB tiles use a dot-separated hierarchy for their tag names. For example the tag `CLBLL_L.SLICEL_X0.ALUT.INIT[00]` documents the bit position of the LSB LUT init bit for the ALUT for the slice with even X coordinate within a `CLBLL_L` tile. (There are 4 LUTs in a slice: ALUT, BLUT, CLUT, and DLUT. And there are two slices in a CLB tile: One with an even X coordinate using the `SLICEL_X0` namespace for tags, and one with an odd X coordinate using the `SLICEL_X1` namespace for tags.)



ppips_*.db
----------

Pseudo :term:`PIPs <pip>` are :term:`PIPs <pip>` in the Vivado tool, but do not have actual bit pattern. The `ppips_*.db` files contain information on pseudo-:term:`PIPs <pip>`. Those files contain one entry per pseudo-PIP, each with one of the following three tags: `always`, `default` or `hint`. The tag `always` is used for pseudo-:term:`PIPs <pip>` that are actually always-on, i.e. that are permanent connections between two wires. The tag `default` is used for pseudo-:term:`PIPs <pip>` that represent the default behavior if no other driver has been configured for the destination net (all `default` pseudo-:term:`PIPs <pip>` connect to the `VCC_WIRE` net). And the tag `hint` is used for :term:`PIPs <pip>` that are used by Vivado to tell the router that two logic slice outputs drive the same value, i.e. behave like they are connected as far as the routing process is concerned.

mask_*.db
---------

These are just simple bit lists

Example line: bit 01_256

See previous section for number meaning

For each segment type there is a mask file `mask_<seg_type>.db` that contains one line for each bit that has been observed being set in any of the example designs generated during generation of the database. The lines simply contain the keyword `bit` followed by the bit position. This database is used to identify unused bits in the configuration segments.


.bits example
-------------

Say entry is: bit_0002050b_002_05

2 step process:
* Decode which segment
* Decode which bit within that segment

We have:
* Frame address 0x0002050b (hex)
* Word #: 2 (decimal, 0-99)
* Bit #: 5 (decimal, 0-31)

The CLB tile and the associated interconnect switchbox tile are configured together as a segment. However, configuration data is grouped by segment column rather than tile column. First, note this segment consists of 36 frames. Second, note there are 100 32 bit words per frame (+ 1 for checksum => 101 actual). Each segment takes 2 of those words meaning 50 segments (ie 50 CLB tiles + 50 interconnect tiles) are effected per frame. This means that the smallest unit that can be fully configured is a group of 50 CLB tile + switchbox tile segments taking 4 * 36 * 101 = 14544 bytes. Finally, note segment columns are aligned to 0x80 addresses (which easily fits the 36 required frames).

tilegrid.json defines addresses more precisely. Taking 0x0002050b, the frame base address is 0x0002050b & 0xFFFFFF80 => 0x00020500. The frame offset is 0x0002050b & 0x7F => 0x0B => 11.

So in summary:
* Frame base address: 0x00020500
* Frame offset: 0x0B (11)
* Frame word #: 2
* Frame word bit #: 5

So, with this in mind, we have frame base address 0x00020500 and word # 2. This maps to tilegrid.json entry SEG_CLBLL_L_X12Y101 (has "baseaddr": ["0x00020600", 2]). This also yields "type": "clbll_l" meaning we are configuring a CLBLL_L.

FIXME: This example is out of date with the new tilegrid format, should update it.


Looking at segbits_clbll_l.db, we need to look up the bit at segment column 11, offset at bit 5. However, this is not present, so we fall back to segbits_int_l.db. This yields a few entries related to EL1BEG (ex: INT_L.EL1BEG_N3.EL1END0 11_05 13_05).


