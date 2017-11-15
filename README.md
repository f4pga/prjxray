Project X-Ray
=============

Documenting the Xilinx 7-series bit-stream format.

Quickstart Guide:
-----------------

Pull submodules:
    git submodule update --init --recursive

Install CMake and build the C++ tools:
    sudo apt-get install cmake # version 3.5.0 or later required,
                               # for Ubuntu Trusty pkg is called cmake3
    mkdir build
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
