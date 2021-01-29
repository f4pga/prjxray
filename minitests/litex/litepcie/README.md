LitePCIe minitest
=================

This minitest is intended to provide a counter-prove on the possible remaining features to document for
the Gigabit Transcievers (GTP tiles) and the PCIE\_2\_1 primitive.

It uses the following litex modules:

| Repo URL                                                  | SHA     |
| --------------------------------------------------------- | ------- |
| <https://github.com/enjoy-digital/litex>                  | 7abfbd9 |
| <https://github.com/enjoy-digital/litedram>               | ab2423e |
| <https://github.com/enjoy-digital/liteeth>                | 7448170 |
| <https://github.com/enjoy-digital/liteiclink>             | 0980a7c |
| <https://github.com/enjoy-digital/litepcie>               | 1d7b584 |
| <https://github.com/enjoy-digital/litex-boards>           | 1d8f0a9 |
| <https://github.com/m-labs/migen>                         | 40b1092 |
| <https://github.com/nmigen/nmigen>                        | 490fca5 |
| <https://github.com/litex-hub/pythondata-cpu-vexriscv>    | 16c5dde |

The final FASM file with the `unknown bits` can be obtained by running the following:

```bash
make all
```

All the pre-requisites (LiteX, RISC-V toolchain, etc.) are automatically installed/built. It is required though to have Vivado installed in the system.
