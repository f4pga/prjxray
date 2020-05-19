==========
part files
==========

Both the ``part.json`` and ``part.yaml`` files contain information about
the configuration resources of the FPGA chip. The files include information
about bus types and the number of :term:`frames <Frame>` that
are available for the given configurational :term:`column <Column>`.

Additionally, the file stores information about the device ID and
available *IO BANKS*.

File format
-----------

Both files contain the same information, but since the ``part.yaml`` is
less accessible, the description will be based on the ``part.json`` file.

The ``part.json`` file is of the following form::

    {
        "global_clock_regions": {
            "bottom": {
                "rows": {
                    "<ROW_NUMBER>" : {
                        "configuration_buses": {
                            "<CONFIGURATION_BUS>": {
                                "configurational_columns": {
                                    "<COLUMN_NUMBER>": {
                                        "frame_count": <FRAME_COUNT>
                                    }
                                    <...>
                                }
                            }
                            <...>
                        }
                    }
                    <...>
                }
            },
            "top": {
                "rows": {
                    "<ROW_NUMBER>" : {
                        "configuration_buses": {
                            "<CONFIGURATION_BUS>": {
                                "configurational_columns": {
                                    "<COLUMN_NUMBER>": {
                                        "frame_count": <FRAME_COUNT>
                                    }
                                    <...>
                                }
                            }
                            <...>
                        }
                    }
                    <...>
                }
            },
            }
        },
        "idcode" : <IDCODE>,
        "iobanks" : {
            "<BANK_ID>": <BANK_POSITION>",
            <...>
        }
    }

The file contains three main entries:

- ``"global_clock_regions"`` - Contains the information about the configurational
  resources of the FPGA chip. The 7-Series FPGAs are divided into two
  :term:`halves <Half>` - ``top`` and ``bottom``. This explains the origin of
  those entries in the file.

  Every half contains a few ``rows`` associated with
  the global :term:`clock regions <Clock region>`. The particular row of the
  global :term:`clock regions <Clock region>` is indicated by the ``<ROW_NUMBER>``.
  Since every row can be configured by one of three configurational buses:
  ``CLK_IO_CLKB``, ``BLOCK_RAM`` or ``CFG_CLB``, the appropriate bus is indicated by
  the ``<CONFIGURATION_BUS>``.

  There are many :term:`columns <Column>` connected to a single bus. Each column
  is described by appropriate ``<COLUMN_NUMBER>`` entry which contains the
  information about the number of frames (``<FRAME_COUNT>``) which can be
  used to configure the particular column.

- ``"idcode"`` - ID of the given chip package

- ``"iobanks"`` - a dictionary that contains the *IO Bank* ID (``<BANK_ID>``) and
  their position in the FPGA grid (``<BANK_POSITION>``).

Examples
--------

.. code-block:: javascript

    {
        global_clock_regions": {
            "bottom": {
                "rows": {
                    "0": {
                        "configuration_buses": {
                            "BLOCK_RAM": {
                                "configuration_columns": {
                                    "0": {
                                        "frame_count": 128
                                    },
                                    "1": {
                                        "frame_count": 128
                                    },
                                    "2": {
                                        "frame_count": 128
                                    }
                                }
                            },
                            "CLB_IO_CLK": {
                                "configuration_columns": {
                                    "0": {
                                        "frame_count": 42
                                    },
                                    "1": {
                                        "frame_count": 30
                                    },
                                    "2": {
                                        "frame_count": 36
                                    },
                                    <...>
                                }
                            }
                        <...>
                    },
                },
            "top" : {
                <...>
            }
        },
        "idcode": 56803475,
        "iobanks": {
            "0": "X1Y78",
            "14": "X1Y26",
            "15": "X1Y78",
            "16": "X1Y130",
            "34": "X113Y26",
            "35": "X113Y78"
        }
    }
