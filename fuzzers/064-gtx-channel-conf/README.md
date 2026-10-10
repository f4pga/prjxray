# GTX channel fabric-reference input

In addition to channel attributes and inversion bits, this fuzzer records
whether `GTGREFCLK` has a nonconstant fabric driver (`GTGREFCLK_USED`). The
CPLL reference selector is held at 7 in both states so the input connection
is randomized independently of the selector. Unused channels and legacy
parameter files tag this input as unused. REQP-52 is disabled only because
this is a configuration-mapping experiment: GTGREFCLK is a test-only input,
not a recommended low-jitter transceiver reference.

A controlled XC7Z030 model comparison using Vivado 2025.2 first identified
three candidate bits when switching from dedicated to fabric reference:
minor/channel-relative bits `31_09`, `31_10`, and `31_54`. A second model
comparison held CPLLREFCLKSEL=7 and GTREFCLK1 fixed and changed only
GTGREFCLK from the PS fabric clock to constant zero; it produced the same
three-bit diff. This input-use tag records the vendor connection pattern;
the minimal physically necessary subset is established separately. Physical bit
isolation on ZC706 rev. 1.2 / XC7Z045 showed that `31_54` alone restores the
fabric reference. Both no-extra-bit and `31_10`-only controls lose the CPLL
reference. The `31_54`-only image passed 1000/1000 complete PCS/MAC PMA
loopback frames, zero errors, approximately 100 MHz selected reference and
125 MHz user clocks. An integrated Yosys/nextpnr/openXC7 build independently
passed 1000 frames without manual frame edits.

The randomized fuzzer has not been rerun with its supported Vivado 2017.2.
The Python generator/tag regression tests pass. The measured Zynq channel
mapping is evidence for review; no `_MID_LEFT`/`_MID_RIGHT` or additional
family mapping is inferred. No generated database files are changed in this
PR. Dedicated Si5324 cross-quad routing remains a separate open problem.
External switch traffic was NOT_RUN because the module EEPROM returned NACK.

- [Controlled model evidence](https://github.com/codex-hil/kasli-soc-linux/blob/main/evidence/zc706/sfp-20261010/vivado-fabric-refclk-model.json)
- [Port-only model comparison](https://github.com/codex-hil/kasli-soc-linux/blob/main/evidence/zc706/sfp-20261010/vivado-fabric-refclk-port-only.json)
- [Physical bit-isolation controls](https://github.com/codex-hil/kasli-soc-linux/tree/main/evidence/zc706/sfp-20261010/fclk-bit-isolation)
- [Integrated build/hardware qualification](https://github.com/codex-hil/kasli-soc-linux/tree/main/evidence/zc706/sfp-20261010/fclk-integrated)
- [Reproducer and limitations](https://github.com/codex-hil/kasli-soc-linux/blob/main/docs/zc706-sfp.md)
