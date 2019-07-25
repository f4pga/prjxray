# assign pins
set_property -dict {PACKAGE_PIN V2 IOSTANDARD LVCMOS33} [get_ports {din[0]}]
set_property -dict {PACKAGE_PIN W2 IOSTANDARD LVCMOS33} [get_ports {din[1]}]
set_property -dict {PACKAGE_PIN V3 IOSTANDARD LVCMOS33} [get_ports {dout[0]}]
set_property -dict {PACKAGE_PIN W3 IOSTANDARD LVCMOS33} [get_ports {dout[1]}]
set_property -dict {PACKAGE_PIN W5 IOSTANDARD LVCMOS33} [get_ports {clk}]

# create roi pblock
create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells -quiet [list roi]]
resize_pblock [get_pblocks roi] -add {SLICE_X36Y0:SLICE_X65Y49}
set_property CONTAIN_ROUTING 1 [get_pblocks roi]
set_property EXCLUDE_PLACEMENT 1 [get_pblocks roi]

# other stuff
set_property DONT_TOUCH true [get_cells roi]
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

# fix LUT locations

## ins
set_property BEL A6LUT [get_cells {roi/ins[0].lut}]
set_property LOC SLICE_X64Y40 [get_cells {roi/ins[0].lut}]
set_property BEL A6LUT [get_cells {roi/ins[1].lut}]
set_property LOC SLICE_X64Y39 [get_cells {roi/ins[1].lut}]

## outs
set_property BEL A6LUT [get_cells {roi/outs[0].lut}]
set_property LOC SLICE_X64Y38 [get_cells {roi/outs[0].lut}]
set_property BEL A6LUT [get_cells {roi/outs[1].lut}]
set_property LOC SLICE_X64Y37 [get_cells {roi/outs[1].lut}]

## clk
set_property BEL AFF [get_cells {roi/clk_reg_reg}]
set_property LOC SLICE_X36Y24 [get_cells {roi/clk_reg_reg}]


# fix routes
set_property FIXED_ROUTE { { IOB_IBUF0 RIOI_I0 RIOI_ILOGIC0_D IOI_ILOGIC0_O IOI_LOGIC_OUTS18_1 INT_INTERFACE_LOGIC_OUTS18 WL1BEG_N3 NW2BEG0 IMUX7 CLBLM_M_A1 }  } [get_nets {din_IBUF[0]}]
set_property FIXED_ROUTE { { IOB_IBUF1 RIOI_I1 RIOI_ILOGIC1_D IOI_ILOGIC1_O IOI_LOGIC_OUTS18_0 INT_INTERFACE_LOGIC_OUTS18 WL1BEG_N3 NW2BEG0 IMUX7 CLBLM_M_A1 }  } [get_nets {din_IBUF[1]}]

set_property FIXED_ROUTE { { CLBLM_M_A CLBLM_LOGIC_OUTS12 EE2BEG0 BYP_ALT0 BYP_BOUNCE0 IMUX34 IOI_OLOGIC0_D1 RIOI_OLOGIC0_OQ RIOI_O0 }  } [get_nets {roi/dout[0]}]
set_property FIXED_ROUTE { { CLBLM_M_A CLBLM_LOGIC_OUTS12 EE2BEG0 BYP_ALT0 BYP_BOUNCE0 IMUX34 IOI_OLOGIC1_D1 RIOI_OLOGIC1_OQ RIOI_O1 }  } [get_nets {roi/dout[1]}]

set_property FIXED_ROUTE {} [get_nets roi/<const0>]

# revert back to original instance
current_instance -quiet
