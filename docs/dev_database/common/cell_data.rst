===============
cell data files
===============

The *cell data* files are meant for specific primitives which have a common attribute format. The data contained in these files is generated/copied from the corresponding primitives' fuzzers.

Naming convention
-----------------

The naming scheme for the cell data files is the following::

    <primitive_name>_<data_file_type>.json

Example files:

    - ``gtpe2_common_attrs.json``
    - ``gtpe2_channel_ports.json``

File format
-----------

There are two main data file types:

    - *Ports*
    - *Attributes*

Attributes files
~~~~~~~~~~~~~~~~

This is a JSON file containing a dictionary of parameters, each one with, at most, four attributes:

    - Type: one of BIN, INT, STR, BOOL.
    - Values: all possible values that this parameter can assume. In case of `BIN` types, the values list contains only the maximum value reachable.
    - Digits: number of digits (or bits) required to enable a parameter.
    - Encoding: This is present only for `INT` types of parameters. These reflect the actual encoding of the parameter value in the bit array.

As an example of parameter please, refer to the following::

    {
        "PLL0_REFCLK_DIV": {
            "type": "INT",
            "values": [1, 2],
            "encoding": [16, 0],
            "digits": 5
        },
        "RXLPMRESET_TIME": {
            "type": "BIN",
            "values": [127],
            "digits": 7
        },
        "RX_XCLK_SEL": {
            "type": "STR",
            "values": ["RXREC", "RXUSR"],
            "digits": 1
        },
        "TX_LOOPBACK_DRIVE_HIZ": {
            "type": "BOOL",
            "values": ["FALSE", "TRUE"],
            "digits": 1
        },
    }

Ports files
~~~~~~~~~~~

This is a JSON file containing a dictionary of ports, each one with two attributes:

    - Direction: Corresponds to the port directiona and can have the ``input``, ``output``, ``clock`` values.
                 Note that the ``clock`` value is implicitly considered also as an ``input``.
    - Width: Indicates the width of the port bus.

As an example of parameter please, refer to the following::

    {
        "CFGRESET": {
            "direction": "input",
            "width": 1
        },
        "CLKRSVD0": {
            "direction": "input",
            "width": 1
        }
    }
