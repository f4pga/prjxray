===============
tile_type files
===============

The *tile_type files* are generated for every FPGA :term:`tile <tile>`
type. They store the information about the :term:`tile <tile>` configuration,
it's :term:`PIPs <pip>`, :term:`sites <site>`, wires and their properties.

Naming convention
-----------------

The naming scheme for the segbits files is the following::

   tile_type_<tile>.json

Exemplary files:

   - ``tile_type_INT_L.json``
   - ``tile_type_BRAM_L.json``
   - ``tile_type_HCLK_CLB.json``

File format
-----------

The :term:`tile <tile>` type files are JSON files with the following shape::

   {
      "pips": {
         "<PIP_NAME>": {
            "can_invert":' "<BOOL>",
            "dst_to_src": {
                "delay": [
                    "<DEALY_VALUE>",
                    "<DELAY_VALUE>",
                    "<DELAY_VALUE>",
                    "<DELAY_VALUE>"
                ],
                "in_cap": "<IN_CAPACITANCE>",
                "res": "<RESISTANCE>"
            },
            "dst_wire": "<WIRE_NAME>",
            "is_directional": "<BOOL>",
            "is_pass_transistor": <BOOL>,
            "is_pseudo": "0",
            "src_to_dst": {
                "delay": [
                    "<DELAY_VALUE>",
                    "<DELAY_VALUE>",
                    "<DELAY_VALUE>",
                    "<DELAY_VALUE>"
                ],
                "in_cap": "<IN_CAPACITANCE>",
                "res": "<RESISTANCE>"
            },
            "src_wire": "<WIRE_NAME>"
         },
      },
      "sites": [
         {
            "name": "<SITE_NAME>",
            "prefix": "<SITE_PREFIX>",
            "site_pins": {
                "<SITE_PIN_NAME>": {
                    "cap": "<CAPACITY>",
                    "delay": [
                        "<DELAY_VALUE>",
                        "<DELAY_VALUE>",
                        "<DELAY_VALUE>",
                        "<DELAY_VALUE>"
                    ],
                    "wire": "<WIRE_NAME>"
                },
                <...>
      ],
      "tile_type": "<TILE_TYPE>",
      "wires": {
         "<WIRE_NAME>": {
            "cap": "<WIRE_CAPACITY>",
            "res": "<WIRE_RESISTANCE>"
         },
         <...>
      },
   }

"pips" section
^^^^^^^^^^^^^^

The "pips" section describes all :term:`PIPs <pip>` in the :term:`tile <tile>`.
Every :term:`PIP <pip>` has it's name - ``"<PIN_NAME>"`` and may be
characterized by the following attributes:

- ``"can_invert"`` - takes a value which can be either **1** or **0**.
  It defines whether the :term:`PIP <pip>` has an inverter on it's output or not.

- ``dst_to_src"`` - information about the connection in the direction
  from destination to source. It describes the following properties of the connection:

   - ``"delay"`` - four-element list, which contain information about the delays.
   - ``"in_cap"`` - the input capacitance of the :term:`PIP <pip>`
   - ``"res"`` - the resistance of the :term:`PIP <pip>`.

- ``dst_wire`` - the destination wire name

- ``is_directional`` - contains the information whether :term:`PIP <pip>` is directional.

- ``is_pass_transisstor`` - contains the information whether :term:`PIP <pip>` acts
  as a pass transistor

- ``is_pseudo`` - contains the information whether :term:`PIP <pip>` is a pseudo-PIP

- ``src_to_dst`` - contains the information about the connection in the direction
  from source to destination. It is described by the same set of properties as
  ``dst_to_src`` section.

"sites" section:
^^^^^^^^^^^^^^^^

The "sites" section describes all :term:`sites <site>` in the :term:`tile <tile>`.
Every :term:`site <site>` may be characterized by the following attributes:

- ``"name"`` - location in the :term:`tile <tile>` grid

- ``"prefix"`` - the type of the :term:`site <site>`

- ``"site_pins"`` - describes the pins that belong to the :term:`site <site>`.
  Every pin has it's  name - ``"<PIN_NAME>"`` and may be described
  by the following attributes:

   - ``"cap"`` - pin capacitance
   - ``"delay"`` - pin delay
   - ``"wire"`` - wire associated with the pin

- ``"type"`` - indicates the type of the site

- ``"x_coord"`` - describes *x* coordinate of the site position inside the tile

- ``y_coord"`` - describes the *y* coordinate of the site position inside the tile

"wires" section
^^^^^^^^^^^^^^^

The "wires" section describes the wires located in the :term:`tile <tile>`.
Every wire has it's name - ``"<WIRE_NAME>"`` and may be characterized
by the following attributes:

- ``"cap"`` - wire capacitance
- ``"res"`` - wire resistance

Other
^^^^^
- ``"tile_type"`` - indicates the type of the tile


Example
-------

Below there is a part of ``tile_type_BRAM_L.json`` for the *artix7* architecture::

   {
      "pips": {
         "BRAM_L.BRAM_ADDRARDADDRL0->>BRAM_FIFO18_ADDRATIEHIGH0": {
            "can_invert": "0",
            "dst_to_src": {
                "delay": [
                    "0.038",
                    "0.046",
                    "0.111",
                    "0.134"
                ],
                "in_cap": "0.000",
                "res": "737.319"
            },
            "dst_wire": "BRAM_FIFO18_ADDRATIEHIGH0",
            "is_directional": "1",
            "is_pass_transistor": 0,
            "is_pseudo": "0",
            "src_to_dst": {
                "delay": [
                    "0.038",
                    "0.046",
                    "0.111",
                    "0.134"
                ],
                "in_cap": "0.000",
                "res": "737.319"
            },
            "src_wire": "BRAM_ADDRARDADDRL0"
         },
         <...>
         "BRAM_L.BRAM_IMUX12_1->BRAM_IMUX_ADDRARDADDRU8": {
            "can_invert": "0",
            "dst_to_src": {
                "delay": null,
                "in_cap": null,
                "res": "0.000"
            },
            "dst_wire": "BRAM_IMUX_ADDRARDADDRU8",
            "is_directional": "1",
            "is_pass_transistor": 1,
            "is_pseudo": "0",
            "src_to_dst": {
                "delay": null,
                "in_cap": null,
                "res": "0.000"
            },
            "src_wire": "BRAM_IMUX12_1"
         },
         <...>
      },
      "sites": [
         {
            "name": "X0Y0",
            "prefix": "RAMB18",
            "site_pins": {
                "ADDRARDADDR0": {
                    "cap": "0.000",
                    "delay": [
                        "0.000",
                        "0.000",
                        "0.000",
                        "0.000"
                    ],
                    "wire": "BRAM_FIFO18_ADDRARDADDR0"
                },
                <...>
                "WRERR": {
                    "delay": [
                        "0.000",
                        "0.000",
                        "0.000",
                        "0.000"
                    ],
                    "res": "860.0625",
                    "wire": "BRAM_RAMB18_WRERR"
                },
                <...>
            },
            "type": "RAMB18E1",
            "x_coord": 0,
            "y_coord": 1
         }
      ],
      "tile_type": "BRAM_L",
      "wires": {
         "BRAM_ADDRARDADDRL0": null,
         "BRAM_ADDRARDADDRL1": null,
         "BRAM_ADDRARDADDRL2": null,
         "BRAM_ADDRARDADDRL3": null,
         "BRAM_EE2A0_0": {
            "cap": "60.430",
            "res": "268.920"
         },
         <...>
         "BRAM_EE2A0_1": {
            "cap": "60.430",
            "res": "268.920"
         },
         <...>
       }
