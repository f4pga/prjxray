Project X-Ray
=============

Documenting the Xilinx 7-series bit-stream format.

See [wiki](https://github.com/cliffordwolf/prjxray/wiki) for more information.


Quickstart Guide:
-----------------

Install CMake and build the C++ tools:
    sudo apt-get install cmake3
    pushd build
    cmake ..
    make
    popd

Always make sure to set the environment for the device you are working on before
running any other commands:

    source database/artix7/settings.sh

Creating HTML documentation:

    cd htmlgen
    python3 htmlgen

(Re-)creating parts of the database, for example LUT init bits:

    cd fuzzers/010-lutinit
    make
    make pushdb
