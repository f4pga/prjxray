GTXE2\_COMMON Primitive Configuration fuzzer
============================================

This fuzzer is used to document the parameters corresponding to the GTXE2\_COMMON primitive.

It uses pre-built JSON containing a dictionary of parameters, each one with four attributes:

- Type: one of Binary, Integer, String, Boolean.
- Values: all possible values that this parameter can assume. In case of `BIN` types, the values list contains only the maximum value reachable.
- Digits: number of digits (or bits) required to use a parameter.
- Encoding: This is present only for `INT` types of parameters. These reflect the actual encoding of the parameter value in the bit array.

E.g.:

```json
{
    "PLL0_REFCLK_DIV": {
        "type": "INT",
        "values": [1, 2],
        "encoding": [16, 0],
        "digits": 5
    }
}
```

In addition, there exist wires and PIPs that allow the connections of the `GTREFCLK` ports to clocks coming from the device fabric instead of the `IBUFDS_GTE2` primitive.

In fact, if the clock comes from the device fabric, the physical `GTGREFCLK[01]` port is used instead of the `GTREFCLK[01]` one (even though the design's primitive port is always `GTREFCLK`).

In the [User Guide (pg 27)](https://docs.amd.com/v/u/en-US/ug476_7Series_Transceivers), it is stated that the `GTGREFCLK[01]` port is used for "internal testing purposes".
Using this port is highly discouraged to get the reference clock from the fabric, as the recommended way is to get the clock from an external source using the `IBUFDS_GTE2` primitive.

Therefore, in addition to the parameters, `IN_USE` and `ZINV\INV` features, this fuzzer documents also the `GTREFCLK[01]_USED` and `BOTH_GTREFCLK[01]_USED` features.
