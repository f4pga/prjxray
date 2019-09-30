# LiteX minitest

This folder contains a minitest for a Linux capable LiteX SoC for Arty board.

## Synthesis+implementation

There are two variants: for Vivado only flow and for Yosys+Vivado flow. In order to run one of them enter the specific directory and run `make`.

## HDL code generation

The following instructions are for generation of the HDL code

## 1. Install Litex

* Create an empty directory and clone there the following repos. Be sure to checkout the specific SHA given.

    | Repo URL | SHA |
    |    ---   | --- |
    | <https://github.com/antmicro/litex>         | 60f2853e |
    | <https://github.com/enjoy-digital/litedram> | 7fbe0b7  |
    | <https://github.com/enjoy-digital/liteeth>  | 2424e62  |
    | <https://github.com/m-labs/migen>           | 562c046  |

* If you do not want to install LiteX and Migen in your system, setup the Python virtualenv and activate it in the following way:

```
virtualenv litex-env
source litex-env/bin/activate
```

* Install LiteX and Migen packages from the previously cloned repos.

    Run the following command in each repo subdirectory:

```
./setup.py develop
```

* (optional) Hack LiteX HDL generation script to make it think that you have RISC-V toolchain installed (if you don't want to build and install it).

    * Open the file `litex/litex/soc/integration/cpu_interface.py` in your favorite editor.
    * Navigate to the line `53`.
    * Replace it with `("TRIPLE", "riscv32-unknown-elf")`

    This will allow you to generate the HDL code without bothering for compilation of the software.

## 2. Install RISC-V toolchain

If you don't want to compile the software for the generated LiteX design then you may skip toolchain installation and just hack the LiteX to think that you have it. To do so follow instuctions in the previous point.

* Clone the repo

```
git clone https://github.com/crosstool-ng/crosstool-ng
cd crosstool-ng
git checkout afaf7b9a
```

* Create a file named `ct.config` and put the following content into it:

```
CT_CONFIG_VERSION="3"
CT_EXPERIMENTAL=y
CT_LOCAL_TARBALLS_DIR="${CT_TOP_DIR}/../dl"
CT_PREFIX_DIR="${CT_TOP_DIR}/${CT_TARGET}"
# CT_PREFIX_DIR_RO is not set
CT_ARCH_RISCV=y
CT_ARCH_ARCH="rv32im"
CT_ARCH_ABI="ilp32"
CT_TARGET_VENDOR=""
CT_LIBC_NONE=y
# CT_CC_GCC_LDBL_128 is not set
CT_DEBUG_GDB=y
# CT_GDB_CROSS_PYTHON is not set
CT_ALLOW_BUILD_AS_ROOT=y
CT_ALLOW_BUILD_AS_ROOT_SURE=y
```

* Build the toolchain. Issue the following commands:

```
export DEFCONFIG=`realpath ct.config`
./bootstrap
./configure --enable-local
make -j`nproc`
./ct-ng defconfig
./ct-ng build.`nproc`
```

## 3. Generate the HDL code

If you have built the RISC-V toolchain then make the PATH point to its binaries:

```
export PATH="crosstool-ng/riscv32-unknown-elf/bin:$(PATH)"
```

The following command will generate HDL code for the LiteX SoC with DRAM and Ethernet support for the Arty board target:

```
cd litex/litex/boards/targets
./arty.py --cpu-type vexriscv --cpu-variant linux --with-ethernet --no-compile-software --no-compile-gateware
```

You can choose which synthesis tool generate the design for. This can be done via the additional `--synth-mode` option of the `arty.py` script. The default is `vivado` but you can change it and specify `yosys`.

Generated code will be placed in the `litex/litex/boards/targets/soc_ethernetsoc_arty` folder.