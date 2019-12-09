#!/usr/bin/env python3
import argparse
import csv
import re

from collections import defaultdict

# =============================================================================


def main():

    BUS_REGEX = re.compile("(.*[A-Z_])([0-9]+)$")

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=str, help="PS7 pin dump file")
    args = parser.parse_args()

    # Load pin dump
    with open(args.csv, "r") as fp:
        pin_dump = list(csv.DictReader(fp))

    # Group pins into buses
    buses = defaultdict(lambda :{
        "direction": None,
        "min": None,
        "max": None,
        "width": 0
        })

    for pin in list(pin_dump):

        # Get bus name and signal index
        match = BUS_REGEX.match(pin["name"])
        if match:
            name = match.group(1)
            idx = int(match.group(2))
        else:
            name = pin["name"]
            idx = 0

        # Get direction
        if int(pin["is_input"]):
            direction = "input"
        if int(pin["is_output"]):
            direction = "output"

        # Add to bus
        bus = buses[name]

        if bus["direction"] is None:
            bus["direction"] = direction
        else:
            assert bus["direction"] == direction

        if bus["min"] is None:
            bus["min"] = idx
        else:
            bus["min"] = min(bus["min"], idx)

        if bus["max"] is None:
            bus["max"] = idx
        else:
            bus["max"] = max(bus["max"], idx)

        bus["width"] = bus["max"] - bus["min"] + 1

    # Sort buses by their purpose
    for name, bus in buses.items():

        # A test pin (unconnected)
        if name.startswith("TEST"):
            cls = "test"

        # A debug pin (unconnected)
        elif name.startswith("DEBUG"):
            cls = "debug"

        # A MIO/DDR pin.
        elif name.startswith("MIO") or name.startswith("DDR") and \
            name != "DDRARB":
            cls = "mio"

        # "Normal" pin
        else:
            cls = "normal"

        bus["class"] = cls

    # .....................................................
    # Generate XML model
    model_xml = """<models>
  <model name="PS7">
"""

    # Inputs
    model_xml += """    <input_ports>
"""
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal", "mio"]:
            continue

        if bus["direction"] != "input":
            continue

        model_xml += "      <port name=\"{}\"/>\n".format(name)

    # Outputs
    model_xml += """    </input_ports>
    <output_ports>
"""
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal", "mio"]:
            continue

        if bus["direction"] != "output":
            continue

        model_xml += "      <port name=\"{}\"/>\n".format(name)

    model_xml += """    </output_ports>
"""

    model_xml += """  </model>
</models>"""

    with open("ps7.model.xml", "w") as fp:
        fp.write(model_xml)

    # .....................................................
    # Generate XML pb_type
    pb_name = "PS7"
    blif_model = "PS7"

    pb_xml = """<pb_type name="{}" blif_model=".subckt {}" num_pb="1">
""".format(pb_name, blif_model)

    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal", "mio"]:
            continue

        pb_xml += "  <{} name=\"{}\" num_pins=\"{}\"/>\n".format(
            bus["direction"].ljust(6), name, bus["width"])

    pb_xml += """</pb_type>
"""

    with open("ps7.pb_type.xml", "w") as fp:
        fp.write(pb_xml)

    # .....................................................
    # Prepare Verilog module definition for the PS7
    pin_strs = []
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal", "mio"]:
            continue

        if bus["width"] > 1:
            pin_str = "  {} [{:>2d}:{:>2d}] {}".format(
                bus["direction"].ljust(6), bus["max"], bus["min"], name)
        else:
            pin_str = "  {}         {}".format(bus["direction"].ljust(6), name)

        pin_strs.append(pin_str)

    verilog = """(* blackbox *)
module PS7 (
{}
);

endmodule
""".format(",\n".join(pin_strs))

    with open("ps7.v", "w") as fp:
        fp.write(verilog)


if __name__ == "__main__":
    main()
