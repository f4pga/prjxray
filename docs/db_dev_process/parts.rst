Tools
=====

`SymbiFlow/prjxray/tools/`

Here, you can find various programs to work with bitstreams, mainly to assist building fuzzers.

bitread:
    Used to read a bitstream file to output a readable bitfile that can be than used
    to get the various FASM features.
segmatch:
    Used in the fuzzing process to correlate the different bits and find which one belong to which feature.
gen_part_base_yaml:
    Used to get a high level information on the device structure (number of
    configuration rows/columns and maximum frame addresses)
xc7frames2bit:
    Used to write a bitstream file starting from a frames one. Where, in turn,
    the frames file can be generated starting from a FASM file.
xc7patch:
    Used to patch a pre-existing bitstream with additional bits.
bittool:
    ???
bits2rbt:
    ???
frame_address_decoder:
    ???

segmatch
--------
This tools takes input files of the format:

code::
    seg 00000000_050
    bit 38_15
    bit 39_14
    <....>
    tag HCLK_IOI3.LVDS_25_IN_USE 0
    tag HCLK_IOI3.ONLY_DIFF_IN_USE 0
    <...>
    seg 00001C80_050
    bit 38_15
    bit 38_26

where `seg <base_frame_address>_<tile_offset>` indicates how to address the tile,
and `bit <frame_address_offset>_<bit_position>` indicates the position of the bit
within the tile.

base_frame_address:
  The frame address of the first frame that configures the tile.

tile_offset:
  The word index of the first word that configures the tile within a frame.

frame_address_offset:
  frame_address - base_frame_address

bit_position:
  The index of the bit within the words of this frame that configure this tile.

The `prjxray.segmaker.Segmaker` is a helper class that can be used to write these
files inside the fuzzer's `generate.py`.
