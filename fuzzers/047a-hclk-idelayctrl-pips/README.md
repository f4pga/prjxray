# HCLK_IOI interconnect fuzzer

This Fuzzer is a copy of the 047-hclk-ioi-pips fuzzer, but only solves IDELAYCTRL pips.
It is separated from the original hclk-ioi-pips as these pips need different segmatch arguments
to avoid mergedb conflicts. Indeed segmatch `-c` parameter is set to 3.

The IDEALYCTRL pips are in the following form:

`HCLK_IOI3.HCLK_IOI_IDELAYCTRL_REFCLK.HCLK_IOI_LEAF_GCLK_((TOP)|(BOT))[0-9]`
