#!/usr/bin/env python3
import sys
from os import environ

import rapidwright
from com.xilinx.rapidwright.design import Design
from com.xilinx.rapidwright.device import PseudoPIPHelper, Device
import com.xilinx.rapidwright.device.TileTypeEnum as TileType

part = environ["XRAY_PART"]
device = Device.getDevice(part)
ppipmap = PseudoPIPHelper.getPseudoPIPMap(device)
tiletypes = ppipmap.keys()
for tiletype in tiletypes:
    filename = f"build/ppips_{str(tiletype.toString()).lower()}.db"
    with open(filename, 'w') as f:
        rioi = ppipmap[tiletype]
        ppipnames = [str(ph.getPseudoPIPName()) for ph in list(rioi.values())]
        for ppip in ppipnames:
            src, dest = ppip.split(str(tiletype) + ".")[-1].split("->")
            f.write(f"{tiletype}.{dest}.{src} always")