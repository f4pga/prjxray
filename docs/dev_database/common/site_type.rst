===============
site_type files
===============

The *site_type files* are generated for every FPGA
:term:`site <Site>` type. They store the information about the pins and
:term:`PIPs <PIP>` of the :term:`site <Site>`.

Naming convention
-----------------

The naming scheme for the :term:`site <Site>` type files is the following::

   site_type_<site>.json

Example files:

   - ``site_type_IDELAYE2.json``
   - ``site_type_PLLE2_ADV.json``
   - ``site_type_SLICEL.json``

File format
-----------

The :term:`site <Site>` type files are JSON files with the following scheme::

    {
        "site_pins": {
            "<PIN_NAME>": {
                "direction": "<DIR>"
            },
            <...>
        },
        "site_pips": {
            "<PIP_NAME>": {
                "from_pin": "<PIN_NAME>",
                "to_pin": "<PIN_NAME>"
            }
        },
        "type": "<TYPE>"
    }

where:

   - *<PIN_NAME>* - specifies the :term:`site <Site>` pin name
   - *<PIP_NAME>* - specifies the :term:`site <Site>` :term:`pip <PIP>` name
   - *<DIR>* - is a direction of a pin (either **IN** or **OUT**)
   - *<TYPE>* - specifies the :term:`site <Site>` type


The ``"site_pins"`` section describes the input pins of a :term:`site <Site>`
and its directions. The ``"site_pips"`` describes the :term:`PIPs <PIP>`
inside the :term:`site <Site>` and which wires they can connect.

Example
-------

Below there is a part of ``site_type_SLICEL.json`` file for the *artix7*
architecture::

   {
      "site_pins": {
         "A": {
            "direction": "OUT"
         },
         "A1": {
            "direction": "IN"
         },
         "A2": {
            "direction": "IN"
         },
         "A3": {
            "direction": "IN"
         },
         "A4": {
            "direction": "IN"
         },
         "A5": {
            "direction": "IN"
         },
         "A6": {
            "direction": "IN"
         },
         <...>
      },
      "site_pips": {
         "A5FFMUX:IN_A": {
            "from_pin": "IN_A",
            "to_pin": "OUT"
         },
         "A5FFMUX:IN_B": {
            "from_pin": "IN_B",
            "to_pin": "OUT"
         },
         "A5LUT:A1": {
            "from_pin": "A1",
            "to_pin": "O5"
         },
         "A5LUT:A2": {
            "from_pin": "A2",
            "to_pin": "O5"
         },
         "A5LUT:A3": {
            "from_pin": "A3",
            "to_pin": "O5"
         },
         "A5LUT:A4": {
            "from_pin": "A4",
            "to_pin": "O5"
         },
         "A5LUT:A5": {
            "from_pin": "A5",
            "to_pin": "O5"
         },
         <...>
      },
      "type": "SLICEL"
   }

Compare the description with the `Xilinx documentation`_ of that :term:`site <Site>`.

.. _Xilinx documentation: https://www.xilinx.com/support/documentation/user_guides/ug474_7Series_CLB.pdf#page=20
