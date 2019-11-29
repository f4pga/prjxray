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
            if len(fields) != 9:
                continue

            iob_sites[fields[3]].append(
                {
                    "tile": fields[0],
                    "name": fields[1],
                    "type": fields[2],
                    "bank": fields[4],
                    "is_bonded": bool(int(fields[5])),
                    "is_clock": bool(int(fields[6])),
                    "is_global_clock": bool(int(fields[7])),
                    "is_vref": bool(int(fields[8])),
                })

    return iob_sites


# =============================================================================

IOBUF_NOT_ALLOWED = [
    'HSTL_I',
    'HSTL_I_18',
    'SSTL18_I',
]


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
        for drive in DRIVES[iostandard]:
            for slew in SLEWS:
                yield {"iostandard": iostandard, "drive": drive, "slew": slew}


# =============================================================================


def run():
    """
    Main.
    """

    # Load IOB data
    iob_sites = load_iob_sites("iobs-{}.csv".format(os.getenv("VIVADO_PART")))

    # Generate designs
    iosettings_gen = gen_iosettings()
    design_index = 0
    while True:

        # Generate clock regions
        region_data = []
        for region in iob_sites:

            # Get IO settings
            try:
                iosettings = next(iosettings_gen)
            except StopIteration:
                break

            # Get sites
            sites = [
                site["name"] for site in iob_sites[region] if site["is_bonded"]
                and not site["is_vref"] and "SING" not in site["tile"]
            ]
            if not len(sites):
                continue

            # Select 5 random sites (IBUF, IBUF, OBUF, OBUF, IOBUF)
            used_sites = random.sample(sites, 5)
            unused_sites = list(set(sites) - set(used_sites))

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

        # No more
        if len(region_data) == 0:
            break

        # Generate the design
        num_inp = len(region_data) * 2
        num_out = len(region_data) * 2
        num_ino = len(region_data)

        verilog = """
module top (
    input  wire [{num_inp}:0] inp,
    inout  wire [{num_ino}:0] ino,
    output wire [{num_out}:0] out
);
""".format(num_inp=num_inp - 1, num_ino=num_ino - 1, num_out=num_out - 1)

        for i, data in enumerate(region_data):

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
                "inp_0": 2 * i + 0,
                "inp_1": 2 * i + 1,
                "out_0": 2 * i + 0,
                "out_1": 2 * i + 1,
                "ino": i,
                "ibuf_param_str": ibuf_param_str,
                "obuf_param_str": obuf_param_str,
            }

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
    (* KEEP, DONT_TOUCH, LOC="{ibuf_0_loc}" *)
    IBUF # ({ibuf_param_str}) ibuf_0_{region} (
    .I(inp[{inp_0}]),
    .O(inp_0_{region})
    );

    (* KEEP, DONT_TOUCH, LOC="{ibuf_1_loc}" *)
    IBUF # ({ibuf_param_str}) ibuf_1_{region} (
    .I(inp[{inp_1}]),
    .O(inp_1_{region})
    );

    (* KEEP, DONT_TOUCH, LOC="{obuf_0_loc}" *)
    OBUF # ({obuf_param_str}) obuf_0_{region} (
    .I(out_0_{region}),
    .O(out[{out_0}])
    );

    (* KEEP, DONT_TOUCH, LOC="{obuf_1_loc}" *)
    OBUF # ({obuf_param_str}) obuf_1_{region} (
    .I(out_1_{region}),
    .O(out[{out_1}])
    );
""".format(**keys)

            if use_ino:
                verilog += """

    (* KEEP, DONT_TOUCH, LOC="{iobuf_loc}" *)
    IOBUF # ({obuf_param_str}) iobuf_{region} (
    .I(ino_i_{region}),
    .O(ino_o_{region}),
    .T(ino_t_{region}),
    .IO(ino[{ino}])
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

        verilog += "endmodule"

        # Write verilog
        fname = "design_{:03d}.v".format(design_index)
        with open(fname, "w") as fp:
            fp.write(verilog)

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
