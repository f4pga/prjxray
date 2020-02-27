# LiteX UART DDR minitest

This test aims at providing a minimal DDR design.
The design is tested with a python script that provides memory control signals to the DDR controller
using an UART bridge.

The script performs the calbiration process, therfore it looks for the bitslip as well as the delay values.

### Litex environment

The litex module used is LiteDRAM, which should be checked-out at the correct commit:

    | Repo URL | SHA |
    |    ---   | --- |
    | <https://github.com/antmicro/litex>         | 3350d33  |
    | <https://github.com/enjoy-digital/litedram> | d8f3feb  |
    | <https://github.com/m-labs/migen>           | d11565a  |


### Implementation

There are two different ways to test this design:

1. Vivado: the flow is entirely managed by Vivado, including Synthesis. To make use of this flow do the following:

```
cd src.vivado
make
```

2. Yosys + Vivado: the flow is divided in two steps. Yosys handles synthesys, while Vivado handles P&R and bitstream generation. To make use of this flow do the following:

```
cd src.yosys
make
```

### Testing

To test the implemented design, load the bitstream produced in the previous step, and do the following:

1. Open the litex server:

```
lxserver --uart --uart-port=/dev/ttyUSBX
```

2. On a different terminal, connect to the server through the client script
```
cd scripts
make test_sdram
```

#### Output

Depending on the clock frequency selected during the gateware generation, different outputs are generated:

- 50 MHz sysytem clock:

    ```
    Minimal Arty DDR3 Design for tests with Project X-Ray 2020-02-03 11:30:24
    Release reset
    Bring CKE high
    Load Mode Register 2, CWL=5
    Load Mode Register 3
    Load Mode Register 1
    Load Mode Register 0, CL=6, BL=8
    ZQ Calibration
    bitslip 0: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|31|
    bitslip 1: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 2: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 3: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 4: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 5: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 6: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 7: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    ```

- 100 MHz system clock:


    ```
    Minimal Arty DDR3 Design for tests with Project X-Ray 2020-01-31 15:41:14
    Release reset
    Bring CKE high
    Load Mode Register 2, CWL=5
    Load Mode Register 3
    Load Mode Register 1
    Load Mode Register 0, CL=6, BL=8
    ZQ Calibration
    bitslip 0: |00|01|02|03|04|05|06|07|08|09|10|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 1: |..|..|..|..|..|..|..|..|..|..|..|..|..|13|14|15|16|17|18|19|20|21|22|23|24|25|..|..|..|..|..|..|
    bitslip 2: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|29|30|31|
    bitslip 3: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 4: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 5: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 6: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    bitslip 7: |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
    ```
