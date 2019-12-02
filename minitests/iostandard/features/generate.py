import os
import random
import json
from collections import defaultdict

try:
    random.seed(int(os.getenv("SEED"), 16))
except TypeError:
    pass

# =============================================================================


def load_iob_sites(file_name):
    """
    Loads IOB site dump from the given CSV file.
    """
    iob_sites = defaultdict(lambda: [])

    with open(file_name, "r") as fp:
        fp.readline()

        for line in fp:

            fields = line.split(",")
            if len(fields) != 10:
                continue

            iob_sites[fields[3]].append(
                {
                    "tile": fields[0],
                    "name": fields[1],
                    "type": fields[2],
                    "bank": fields[4],
                    "pkg_pin": fields[5],
                    "is_bonded": bool(int(fields[6])),
                    "is_clock": bool(int(fields[7])),
                    "is_global_clock": bool(int(fields[8])),
                    "is_vref": bool(int(fields[9])),
                })

    return iob_sites


# =============================================================================

IOBUF_NOT_ALLOWED = [
    'HSTL_I',
    'HSTL_I_18',
    'SSTL18_I',
]

DIFF_MAP = {
    'SSTL135': 'DIFF_SSTL135',
}


def gen_iosettings():
    """
    A generator function which yields all possible IO settings combintions.
    """

    IOSTANDARDS = (
        'LVCMOS12',
        'LVCMOS15',
        'LVCMOS18',
        'LVCMOS25',
        'LVCMOS33',
        'LVTTL',
        'SSTL135',

        # Those are available but not currently fuzzed.
        #        'SSTL135_R',
        #        'SSTL15',
        #        'SSTL15_R',
        #        'SSTL18_I',
        #        'SSTL18_II',
        #        'HSTL_I',
        #        'HSTL_I_18',
        #        'HSTL_II',
        #        'HSTL_II_18',
        #        'HSUL_12',
        #        'MOBILE_DDR',
    )

    DRIVES = defaultdict(lambda: [None])
    DRIVES.update(
        {
            "LVTTL": [4, 8, 12, 16, 24],
            "LVCMOS12": [4, 8, 12],
            "LVCMOS15": [4, 8, 12, 16],
            "LVCMOS18": [4, 8, 12, 16, 24],
            "LVCMOS25": [4, 8, 12, 16],
            "LVCMOS33": [4, 8, 12, 16],
        })

    SLEWS = ("SLOW", "FAST")

    for iostandard in IOSTANDARDS:

        # Single ended
        for drive in DRIVES[iostandard]:
            for slew in SLEWS:
                yield {"iostandard": iostandard, "drive": drive, "slew": slew}

        # Differential
        if iostandard in DIFF_MAP:
            for drive in DRIVES[iostandard]:
                for slew in SLEWS:
                    yield {
                        "iostandard": DIFF_MAP[iostandard],
                        "drive": drive,
                        "slew": slew
                    }


# =============================================================================


def run():
    """
    Main.
    """

    # Load IOB data
    iob_sites = load_iob_sites("iobs-{}.csv".format(os.getenv("VIVADO_PART")))

    # Generate IOB site to package pin map and *M site to *S site map.
    site_to_pkg_pin = {}
    master_to_slave = {}

    for region, sites in iob_sites.items():
        tiles = defaultdict(lambda: {})

        for site in sites:
            site_to_pkg_pin[site["name"]] = site["pkg_pin"]
            if site["type"] == "IOB33M":
                tiles[site["tile"]]["M"] = site
            if site["type"] == "IOB33S":
                tiles[site["tile"]]["S"] = site

        for sites in tiles.values():
            master_to_slave[sites["M"]["name"]] = sites["S"]["name"]

    # Generate designs
    iosettings_gen = gen_iosettings()
    design_index = 0
    while True:

        num_inp = 0
        num_out = 0
        num_ino = 0

        # Generate clock regions
        region_data = []
        for region in sorted(list(iob_sites.keys())):

            # Get IO settings
            try:
                iosettings = next(iosettings_gen)
            except StopIteration:
                break

            # Get sites
            sites = [
                (
                    site["name"],
                    site["type"],
                ) for site in iob_sites[region] if site["is_bonded"]
                and not site["is_vref"] and "SING" not in site["tile"]
            ]
            if not len(sites):
                continue

            # Differential / single ended
            if "DIFF" in iosettings["iostandard"]:

                # Select 5 random sites (IBUFDS, IBUFDS, OBUFDS, OBUFDS, IOBUFDS)
                site_names = [s[0] for s in sites if s[1] == "IOB33M"]
                used_sites = random.sample(site_names, 5)
                unused_sites = list(set(site_names) - set(used_sites))

                num_inp += 4
                num_out += 4
                num_ino += 2

            else:
                # Select 5 random sites (IBUF, IBUF, OBUF, OBUF, IOBUF)
                site_names = [s[0] for s in sites]
                used_sites = random.sample(site_names, 5)
                unused_sites = list(set(site_names) - set(used_sites))

                num_inp += 2
                num_out += 2
                num_ino += 1

            # Store data
            region_data.append(
                {
                    "region": region,
                    "iosettings": iosettings,
                    "unused_sites": unused_sites,
                    "input": used_sites[0:2],
                    "output": used_sites[2:4],
                    "inout": used_sites[4:5],
                })
            print(region, iosettings)
        print("----")

        # No more
        if len(region_data) == 0:
            break

        # Generate the design
        verilog = """
module top (
    input  wire [{num_inp}:0] inp,
    inout  wire [{num_ino}:0] ino,
    output wire [{num_out}:0] out
);
""".format(num_inp=num_inp - 1, num_ino=num_ino - 1, num_out=num_out - 1)

        tcl = ""

        inp_idx = 0
        out_idx = 0
        ino_idx = 0

        for i, data in enumerate(region_data):

            is_diff = "DIFF" in data["iosettings"]["iostandard"]
            use_ino = data["iosettings"]["iostandard"] not in IOBUF_NOT_ALLOWED

            iostandard = data["iosettings"]["iostandard"]
            drive = data["iosettings"]["drive"]
            slew = data["iosettings"]["slew"]

            ibuf_param_str = ".IOSTANDARD(\"{}\")".format(iostandard)
            obuf_param_str = str(ibuf_param_str)

            if drive is not None:
                obuf_param_str += ", .DRIVE({})".format(drive)
            if slew is not None:
                obuf_param_str += ", .SLEW(\"{}\")".format(slew)

            keys = {
                "region": data["region"],
                "ibuf_0_loc": data["input"][0],
                "ibuf_1_loc": data["input"][1],
                "obuf_0_loc": data["output"][0],
                "obuf_1_loc": data["output"][1],
                "iobuf_loc": data["inout"][0],
                "inp_0_p": inp_idx,
                "inp_0_n": inp_idx + 2,
                "inp_1_p": inp_idx + 1,
                "inp_1_n": inp_idx + 3,
                "out_0_p": out_idx,
                "out_0_n": out_idx + 2,
                "out_1_p": out_idx + 1,
                "out_1_n": out_idx + 3,
                "ino_p": ino_idx,
                "ino_n": ino_idx + 1,
                "ibuf_param_str": ibuf_param_str,
                "obuf_param_str": obuf_param_str,
            }

            if is_diff:
                inp_idx += 4
                out_idx += 4
                ino_idx += 2
            else:
                inp_idx += 2
                out_idx += 2
                ino_idx += 1

            # Single ended
            if not is_diff:

                tcl += "set_property PACKAGE_PIN {} [get_ports inp[{}]]\n".format(
                    site_to_pkg_pin[keys["ibuf_0_loc"]], keys["inp_0_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports inp[{}]]\n".format(
                    site_to_pkg_pin[keys["ibuf_1_loc"]], keys["inp_1_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports out[{}]]\n".format(
                    site_to_pkg_pin[keys["obuf_0_loc"]], keys["inp_0_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports out[{}]]\n".format(
                    site_to_pkg_pin[keys["obuf_1_loc"]], keys["inp_1_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports ino[{}]]\n".format(
                    site_to_pkg_pin[keys["iobuf_loc"]], keys["ino_p"])

                verilog += """

    // {region}
    wire inp_0_{region};
    wire inp_1_{region};
    wire out_0_{region};
    wire out_1_{region};

    wire ino_i_{region};
    wire ino_o_{region};
    wire ino_t_{region};
""".format(**keys)

                verilog += """
    (* KEEP, DONT_TOUCH *)
    IBUF # ({ibuf_param_str}) ibuf_0_{region} (
    .I(inp[{inp_0_p}]),
    .O(inp_0_{region})
    );

    (* KEEP, DONT_TOUCH *)
    IBUF # ({ibuf_param_str}) ibuf_1_{region} (
    .I(inp[{inp_1_p}]),
    .O(inp_1_{region})
    );

    (* KEEP, DONT_TOUCH *)
    OBUF # ({obuf_param_str}) obuf_0_{region} (
    .I(out_0_{region}),
    .O(out[{out_0_p}])
    );

    (* KEEP, DONT_TOUCH *)
    OBUF # ({obuf_param_str}) obuf_1_{region} (
    .I(out_1_{region}),
    .O(out[{out_1_p}])
    );
""".format(**keys)

                if use_ino:
                    verilog += """

    (* KEEP, DONT_TOUCH *)
    IOBUF # ({obuf_param_str}) iobuf_{region} (
    .I(ino_i_{region}),
    .O(ino_o_{region}),
    .T(ino_t_{region}),
    .IO(ino[{ino_p}])
    );

    assign out_0_{region} = inp_0_{region};
    assign out_1_{region} = ino_o_{region};
    assign ino_i_{region} = inp_0_{region};
    assign ino_t_{region} = inp_1_{region};
""".format(**keys)

                else:
                    verilog += """

    assign out_0_{region} = inp_0_{region};
    assign out_1_{region} = inp_1_{region};
    assign ino[{ino}] = 1'b0;
""".format(**keys)

            # Differential
            else:

                tcl += "set_property PACKAGE_PIN {} [get_ports inp[{}]]\n".format(
                    site_to_pkg_pin[keys["ibuf_0_loc"]], keys["inp_0_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports inp[{}]]\n".format(
                    site_to_pkg_pin[master_to_slave[keys["ibuf_0_loc"]]],
                    keys["inp_0_n"])
                tcl += "set_property PACKAGE_PIN {} [get_ports inp[{}]]\n".format(
                    site_to_pkg_pin[keys["ibuf_1_loc"]], keys["inp_1_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports inp[{}]]\n".format(
                    site_to_pkg_pin[master_to_slave[keys["ibuf_1_loc"]]],
                    keys["inp_1_n"])
                tcl += "set_property PACKAGE_PIN {} [get_ports out[{}]]\n".format(
                    site_to_pkg_pin[keys["obuf_0_loc"]], keys["inp_0_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports out[{}]]\n".format(
                    site_to_pkg_pin[master_to_slave[keys["obuf_0_loc"]]],
                    keys["inp_0_n"])
                tcl += "set_property PACKAGE_PIN {} [get_ports out[{}]]\n".format(
                    site_to_pkg_pin[keys["obuf_1_loc"]], keys["inp_1_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports out[{}]]\n".format(
                    site_to_pkg_pin[master_to_slave[keys["obuf_1_loc"]]],
                    keys["inp_1_n"])
                tcl += "set_property PACKAGE_PIN {} [get_ports ino[{}]]\n".format(
                    site_to_pkg_pin[keys["iobuf_loc"]], keys["ino_p"])
                tcl += "set_property PACKAGE_PIN {} [get_ports ino[{}]]\n".format(
                    site_to_pkg_pin[master_to_slave[keys["iobuf_loc"]]],
                    keys["ino_n"])

                verilog += """

    // {region}
    wire inp_0_{region};
    wire inp_1_{region};
    wire out_0_{region};
    wire out_1_{region};

    wire ino_i_{region};
    wire ino_o_{region};
    wire ino_t_{region};
""".format(**keys)

                verilog += """
    (* KEEP, DONT_TOUCH *)
    IBUFDS # ({ibuf_param_str}) ibufds_0_{region} (
    .I(inp[{inp_0_p}]),
    .IB(inp[{inp_0_n}]),
    .O(inp_0_{region})
    );

    (* KEEP, DONT_TOUCH *)
    IBUFDS # ({ibuf_param_str}) ibufds_1_{region} (
    .I(inp[{inp_1_p}]),
    .IB(inp[{inp_1_n}]),
    .O(inp_1_{region})
    );

    (* KEEP, DONT_TOUCH *)
    OBUFDS # ({obuf_param_str}) obufds_0_{region} (
    .I(out_0_{region}),
    .O(out[{out_0_p}]),
    .OB(out[{out_0_n}])
    );

    (* KEEP, DONT_TOUCH *)
    OBUFDS # ({obuf_param_str}) obufds_1_{region} (
    .I(out_1_{region}),
    .O(out[{out_1_p}]),
    .OB(out[{out_1_n}])
    );
""".format(**keys)

                if use_ino:
                    verilog += """

    (* KEEP, DONT_TOUCH *)
    IOBUFDS # ({obuf_param_str}) iobufds_{region} (
    .I(ino_i_{region}),
    .O(ino_o_{region}),
    .T(ino_t_{region}),
    .IO(ino[{ino_p}]),
    .IOB(ino[{ino_n}])
    );

    assign out_0_{region} = inp_0_{region};
    assign out_1_{region} = ino_o_{region};
    assign ino_i_{region} = inp_0_{region};
    assign ino_t_{region} = inp_1_{region};
""".format(**keys)

                else:
                    verilog += """

    assign out_0_{region} = inp_0_{region};
    assign out_1_{region} = inp_1_{region};
    assign ino[{ino_p}] = 1'b0;
    assign ino[{ino_n}] = 1'b0;
""".format(**keys)

        verilog += "endmodule"

        # Write verilog
        fname = "design_{:03d}.v".format(design_index)
        with open(fname, "w") as fp:
            fp.write(verilog)

        # Write TCL
        fname = "design_{:03d}.tcl".format(design_index)
        with open(fname, "w") as fp:
            fp.write(tcl)

        # Write JSON
        fname = "design_{:03d}.json".format(design_index)

        # Convert Vivado site names to fasm-style TILE.SITE names.
        for data in region_data:
            type_to_loc = {
                "IOB33": "IOB_Y0",
                "IOB33M": "IOB_Y0",
                "IOB33S": "IOB_Y1"
            }
            site_to_loc = {
                s["name"]: "{}.{}".format(s["tile"], type_to_loc[s["type"]])
                for s in iob_sites[data["region"]]
            }

            for l in ["input", "output", "inout", "unused_sites"]:
                data[l] = [site_to_loc[s] for s in data[l]]

        # Write design settings to JSON
        with open(fname, "w") as fp:
            json.dump(region_data, fp, sort_keys=True, indent=1)

        design_index += 1


if __name__ == "__main__":
    run()
