# HR LVDS_25 differential termination

SPDX-License-Identifier: ISC

Controlled comparator for all 60 bonded HR differential pairs on
XC7Z020CLG400-1 (banks 13, 34 and 35, both LIOB33 and RIOB33).
This design is **not** a board image: its arbitrary output and bank voltages
are not intended for hardware programming.

`reference.tcl` routes once and changes only each P port's DIFF_TERM property.
It writes OFF, each single pair ON, ALL ON and repeated OFF bitstreams.
The measured local tile bits are `38_100 39_97`, independent of pin/bank and
left/right orientation. No other non-ECC configuration bits change.
`mapping.json` records all 60 results and bitstream SHA-256 values.

Reproduction (the comparator was run with Vivado 2019.1):

```sh
vivado -mode batch -source reference.tcl
for name in off off-repeat all pair{0..59}; do
    bitread --part_file "$XRAY_DATABASE_ROOT/xc7z020clg400-1/part.yaml" \
        -y -z -o "$name.bits" "$name.bit"
done
python3 verify_bits.py --db "$XRAY_DATABASE_ROOT"
```

The verifier rejects changes outside the selected tile, inconsistent same-type
mappings, a changed repeated baseline, or an ALL ON result differing from the
union of individual changes. Only derived frame ECC word 50 is excluded.
This comparator does not replace a full rerun of the randomized 030-iob fuzzer
with its supported Vivado version.

The generated database also needs a separate `IOB_Y0.LVDS_25.IN_ONLY` feature:
legacy grouped IN_ONLY features constrain these shared differential-drive bits
to zero. The postprocessor retains the legacy feature and emits an alias that
relaxes only the independently measured DIFF_TERM bits.

Physical A/B was tested with a Yosys/nextpnr/X-Ray build on a ZC706 rev. 1.2,
XC7Z045FFG900, CERN FMC ADC100M14b4cha v6.1 in LPC, VADJ 2.5 V. All 11 design
receivers use HR banks. ADC source termination was disabled (LTC2174 A2=0).
Removing exactly 22 non-ECC bits from the same routed design prevents stable
lane calibration; restoring them passes 139264 channel test-pattern values
and a 1024-sample/channel snapshot on two cold boots. Analog inputs were
unconnected, so this is not analog qualification. No SD or QSPI writes.

Complete physical evidence and the separate nextpnr patch are maintained at:
https://github.com/codex-hil/kasli-soc-linux/tree/main/evidence/zc706/hr-diff-term-20261008
and https://github.com/codex-hil/kasli-soc-linux/blob/main/docs/hr-diff-term.md .

Scope is HR LVDS_25 input termination only. No HP or other-standard mapping
is inferred from these results. Vivado was only the optional mapping comparator;
the tested board bitstreams were built without it.
