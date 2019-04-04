.db Files
=========

Introduction
------------

This section documents how prjxray represents the bitstream database

These ".db" files come in two common flavors:
 * `segbits_*.db`_: encodes bitstream bits
 * `mask_*.db`_: which bits are used by a segment? Probably needs to be converted to tile

Also note: .rdb (raw db) is a convention for a non-expanded .db file (see below)


segbits_*.db
------------

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
   * segmatch -m (min tag value occurances) was given, but occurances are below this threshold
   * ie INT.FAN_ALT4.SS2END0 occcured twice, but this is below the acceptable level (say 5)
 * INT.FAN_ALT4.SS2END0 <M 6 8> 18_09 25_08
   * Internal only
   * segmatch -M (min tag occurances) was given, but total occurances are below this threshold
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


mask_*.db
---------

These are just simple bit lists

Example line: bit 01_256

See previous section for number meaning

