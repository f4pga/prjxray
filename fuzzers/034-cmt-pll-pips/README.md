# Fuzzer for the PIPs of CMT_TOP_[LR]_UPPER_T tiles.

The fuzzer instantiates a PLL in each available site with 2/3 probability of using it. Once used it is connected randomly to various clock and logic resources.

For some nets a randomized "manual" route is chosen to cover as many routing scenarios as possible.

The information whether a PLL is used or not is stored in a file (`"design.txt"`) along with the randomized route (`route.txt`)

After the design synthesis the `generate.py` sets fixed routes on some nets which is read from the `route.txt` file. The rest of the design is routed in the regular way. The script also dumps all used PIPs (as reported by Vivado) to the `design_pips.txt`.

The tag generation is done in the following way:

- If a PLL site is occupied then tags for all active PIPs are emitted as 1s. No tags are emitted for inactive PIPs.
- When a PLL site is not occupied (IN_USE=0) then tags for all PIPs for the CMT tile are emitted as 0s.
- The IN_USE tag is emitted directly.

The raw solution of tag bits is postprocessed via the custom script `fixup_and_group.py`. The script does two things:

- Clears all bits found for the IN_USE tag in all other tags. Those bits are common to all of them.
- Groups tags according to the group definitions read from the `tag_groups.txt` file. Bits that are common to the group are set as 0 in each tag that belongs to it (tags within a group are exclusive).