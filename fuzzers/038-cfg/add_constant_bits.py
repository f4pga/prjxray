import sys

constant_bits = {
    "CFG_CENTER_MID.ALWAYS_ON_PROP1": "26_2206",
    "CFG_CENTER_MID.ALWAYS_ON_PROP2": "26_2207",
    "CFG_CENTER_MID.ALWAYS_ON_PROP3": "27_2205"
}

with open(sys.argv[1], "a") as f:
    for bit_name, bit_value in constant_bits.items():
        f.write(bit_name + " " + bit_value + "\n")
