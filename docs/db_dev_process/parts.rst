Tools
=====

`SymbiFlow/prjxray/tools/`

Here, you can find various programs to work with bitstreams, mainly to assist building fuzzers.

bitread:
    Used to read a bitstream file to output a readable bitfile that can be than used
    to get the various FASM features.
segmatch:
    Used in the fuzzing process to correlate the different bits and find which one belong to which feature.
gen_part_base_yaml.
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
