#!/usr/bin/env python3
import argparse
import csv
import json
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
        is_input = int(pin["is_input"])
        is_output = int(pin["is_output"])
        is_bidir = int(pin["is_bidir"])

        if is_input and not is_output and not is_bidir:
            direction = "input"
        elif not is_input and is_output and not is_bidir:
            direction = "output"
        elif not is_input and not is_output and is_bidir:
            direction = "inout"
        else:
            assert False, pin

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

        # PS7 clock/reset
        elif name in ["PSCLK", "PSPORB", "PSSRSTB"]:
            cls = "mio"

        # "Normal" pin
        else:
            cls = "normal"

        bus["class"] = cls

    # .....................................................
    # Generate JSON with PS7 pins grouped by direction

    ps7_pins = {"input": [], "output": [], "inout": []}
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal", "mio"]:
            continue

        if bus["width"] > 1:
            for i in range(bus["min"], bus["max"]+1):
                pin_name = "{}{}".format(name, i)
                ps7_pins[bus["direction"]].append(pin_name)
        else:
            ps7_pins[bus["direction"]].append(name)
    
    with open("ps7_pins.json", "w") as fp:
        json.dump(ps7_pins, fp, sort_keys=True, indent=2)

    # .....................................................
    # Generate XML model
    pb_name = "PS7"
    blif_model = "PS7_VPR"

    model_xml = """<models>
  <model name="{}">
""".format(blif_model)

    # Inputs
    model_xml += """    <input_ports>
"""
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal"]:
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
        if bus["class"] not in ["normal"]:
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
    pb_xml = """<pb_type name="{}" blif_model=".subckt {}" num_pb="1">
""".format(pb_name, blif_model)

    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal"]:
            continue

        pb_xml += "  <{} name=\"{}\" num_pins=\"{}\"/>\n".format(
            bus["direction"].ljust(6), name, bus["width"])

    pb_xml += """</pb_type>
"""

    with open("ps7.pb_type.xml", "w") as fp:
        fp.write(pb_xml)

    # .....................................................
    # Prepare Verilog module definition for the PS7_VPR
    port_defs = []
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins (eg. MIO and DDR)
        if bus["class"] not in ["normal"]:
            continue

        # Generate port definition
        if bus["width"] > 1:
            port_str = "  {} [{:>2d}:{:>2d}] {}".format(
                bus["direction"].ljust(6), bus["max"], bus["min"], name)
        else:
            port_str = "  {}         {}".format(
                bus["direction"].ljust(6), name)

        port_defs.append(port_str)

    verilog = """(* blackbox *)
module PS7_VPR (
{}
);

endmodule
""".format(",\n".join(port_defs))

    with open("ps7_sim.v", "w") as fp:
        fp.write(verilog)

    # .....................................................
    # Prepare techmap that maps PS7 to PS7_VPR and handles
    # unconnected inputs (ties them to GND)
    port_defs = []
    port_conns = []
    param_defs = []
    wire_defs = []
    for name in sorted(buses.keys()):
        bus = buses[name]

        # Skip not relevant pins
        if bus["class"] not in ["normal", "mio"]:
            continue

        # Generate port definition
        if bus["width"] > 1:
            port_str = "  {} [{:>2d}:{:>2d}] {}".format(
                bus["direction"].ljust(6), bus["max"], bus["min"], name)
        else:
            port_str = "  {}         {}".format(
                bus["direction"].ljust(6), name)

        port_defs.append(port_str)

        # MIO and DDR pins are not mapped as they are dummy
        if bus["class"] == "mio":
            continue

        # This is an input port, needs to be tied to GND if unconnected
        if bus["direction"] == "input":

            # Techmap parameter definition
            param_defs.append(
                "  parameter _TECHMAP_CONSTMSK_{}_ = 0;".format(name.upper()))
            param_defs.append(
                "  parameter _TECHMAP_CONSTVAL_{}_ = 0;".format(name.upper()))

            # Wire definition using generate statement. Necessary for detection
            # of unconnected ports.
            wire_defs.append(
                """
  generate if((_TECHMAP_CONSTMSK_{name_upr}_ == {N}'d0) && (_TECHMAP_CONSTVAL_{name_upr}_ == {N}'d0))
    wire [{M}:0] {name_lwr} = {N}'d0;
  else
    wire [{M}:0] {name_lwr} = {name};
  endgenerate""".format(
                    name=name,
                    name_upr=name.upper(),
                    name_lwr=name.lower(),
                    N=bus["width"],
                    M=bus["width"] - 1))

            # Connection to the "generated" wire.
            port_conns.append(
                "  .{name:<25}({name_lwr})".format(
                    name=name, name_lwr=name.lower()))

        # An output port
        else:

            # Direct connection
            port_conns.append("  .{name:<25}({name})".format(name=name))

    # Format the final verilog.
    verilog = """module PS7 (
{port_defs}
);

  // Techmap specific parameters.
{param_defs}

  // Detect all unconnected inputs and tie them to 0.
{wire_defs}

  // Replacement cell.
  PS7_VPR _TECHMAP_REPLACE_ (
{port_conns}
  );

endmodule
""".format(
        port_defs=",\n".join(port_defs),
        param_defs="\n".join(param_defs),
        wire_defs="\n".join(wire_defs),
        port_conns=",\n".join(port_conns))

    with open("ps7_map.v", "w") as fp:
        fp.write(verilog)


# =============================================================================

if __name__ == "__main__":
    main()
