create_project -in_memory -part xc7z020clg400-1
read_verilog top.v
synth_design -top top
set_property -dict {PACKAGE_PIN B19 IOSTANDARD LVDS_25} [get_ports {in_p[0]}]
set_property -dict {PACKAGE_PIN A20 IOSTANDARD LVDS_25} [get_ports {in_n[0]}]
set_property -dict {PACKAGE_PIN C20 IOSTANDARD LVDS_25} [get_ports {in_p[1]}]
set_property -dict {PACKAGE_PIN B20 IOSTANDARD LVDS_25} [get_ports {in_n[1]}]
set_property -dict {PACKAGE_PIN D19 IOSTANDARD LVDS_25} [get_ports {in_p[2]}]
set_property -dict {PACKAGE_PIN D20 IOSTANDARD LVDS_25} [get_ports {in_n[2]}]
set_property -dict {PACKAGE_PIN E17 IOSTANDARD LVDS_25} [get_ports {in_p[3]}]
set_property -dict {PACKAGE_PIN D18 IOSTANDARD LVDS_25} [get_ports {in_n[3]}]
set_property -dict {PACKAGE_PIN E18 IOSTANDARD LVDS_25} [get_ports {in_p[4]}]
set_property -dict {PACKAGE_PIN E19 IOSTANDARD LVDS_25} [get_ports {in_n[4]}]
set_property -dict {PACKAGE_PIN F16 IOSTANDARD LVDS_25} [get_ports {in_p[5]}]
set_property -dict {PACKAGE_PIN F17 IOSTANDARD LVDS_25} [get_ports {in_n[5]}]
set_property -dict {PACKAGE_PIN F19 IOSTANDARD LVDS_25} [get_ports {in_p[6]}]
set_property -dict {PACKAGE_PIN F20 IOSTANDARD LVDS_25} [get_ports {in_n[6]}]
set_property -dict {PACKAGE_PIN G17 IOSTANDARD LVDS_25} [get_ports {in_p[7]}]
set_property -dict {PACKAGE_PIN G18 IOSTANDARD LVDS_25} [get_ports {in_n[7]}]
set_property -dict {PACKAGE_PIN G19 IOSTANDARD LVDS_25} [get_ports {in_p[8]}]
set_property -dict {PACKAGE_PIN G20 IOSTANDARD LVDS_25} [get_ports {in_n[8]}]
set_property -dict {PACKAGE_PIN H15 IOSTANDARD LVDS_25} [get_ports {in_p[9]}]
set_property -dict {PACKAGE_PIN G15 IOSTANDARD LVDS_25} [get_ports {in_n[9]}]
set_property -dict {PACKAGE_PIN H16 IOSTANDARD LVDS_25} [get_ports {in_p[10]}]
set_property -dict {PACKAGE_PIN H17 IOSTANDARD LVDS_25} [get_ports {in_n[10]}]
set_property -dict {PACKAGE_PIN J18 IOSTANDARD LVDS_25} [get_ports {in_p[11]}]
set_property -dict {PACKAGE_PIN H18 IOSTANDARD LVDS_25} [get_ports {in_n[11]}]
set_property -dict {PACKAGE_PIN J20 IOSTANDARD LVDS_25} [get_ports {in_p[12]}]
set_property -dict {PACKAGE_PIN H20 IOSTANDARD LVDS_25} [get_ports {in_n[12]}]
set_property -dict {PACKAGE_PIN K14 IOSTANDARD LVDS_25} [get_ports {in_p[13]}]
set_property -dict {PACKAGE_PIN J14 IOSTANDARD LVDS_25} [get_ports {in_n[13]}]
set_property -dict {PACKAGE_PIN K16 IOSTANDARD LVDS_25} [get_ports {in_p[14]}]
set_property -dict {PACKAGE_PIN J16 IOSTANDARD LVDS_25} [get_ports {in_n[14]}]
set_property -dict {PACKAGE_PIN K17 IOSTANDARD LVDS_25} [get_ports {in_p[15]}]
set_property -dict {PACKAGE_PIN K18 IOSTANDARD LVDS_25} [get_ports {in_n[15]}]
set_property -dict {PACKAGE_PIN K19 IOSTANDARD LVDS_25} [get_ports {in_p[16]}]
set_property -dict {PACKAGE_PIN J19 IOSTANDARD LVDS_25} [get_ports {in_n[16]}]
set_property -dict {PACKAGE_PIN L14 IOSTANDARD LVDS_25} [get_ports {in_p[17]}]
set_property -dict {PACKAGE_PIN L15 IOSTANDARD LVDS_25} [get_ports {in_n[17]}]
set_property -dict {PACKAGE_PIN L16 IOSTANDARD LVDS_25} [get_ports {in_p[18]}]
set_property -dict {PACKAGE_PIN L17 IOSTANDARD LVDS_25} [get_ports {in_n[18]}]
set_property -dict {PACKAGE_PIN L19 IOSTANDARD LVDS_25} [get_ports {in_p[19]}]
set_property -dict {PACKAGE_PIN L20 IOSTANDARD LVDS_25} [get_ports {in_n[19]}]
set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVDS_25} [get_ports {in_p[20]}]
set_property -dict {PACKAGE_PIN M15 IOSTANDARD LVDS_25} [get_ports {in_n[20]}]
set_property -dict {PACKAGE_PIN M17 IOSTANDARD LVDS_25} [get_ports {in_p[21]}]
set_property -dict {PACKAGE_PIN M18 IOSTANDARD LVDS_25} [get_ports {in_n[21]}]
set_property -dict {PACKAGE_PIN M19 IOSTANDARD LVDS_25} [get_ports {in_p[22]}]
set_property -dict {PACKAGE_PIN M20 IOSTANDARD LVDS_25} [get_ports {in_n[22]}]
set_property -dict {PACKAGE_PIN N15 IOSTANDARD LVDS_25} [get_ports {in_p[23]}]
set_property -dict {PACKAGE_PIN N16 IOSTANDARD LVDS_25} [get_ports {in_n[23]}]
set_property -dict {PACKAGE_PIN N17 IOSTANDARD LVDS_25} [get_ports {in_p[24]}]
set_property -dict {PACKAGE_PIN P18 IOSTANDARD LVDS_25} [get_ports {in_n[24]}]
set_property -dict {PACKAGE_PIN N18 IOSTANDARD LVDS_25} [get_ports {in_p[25]}]
set_property -dict {PACKAGE_PIN P19 IOSTANDARD LVDS_25} [get_ports {in_n[25]}]
set_property -dict {PACKAGE_PIN N20 IOSTANDARD LVDS_25} [get_ports {in_p[26]}]
set_property -dict {PACKAGE_PIN P20 IOSTANDARD LVDS_25} [get_ports {in_n[26]}]
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVDS_25} [get_ports {in_p[27]}]
set_property -dict {PACKAGE_PIN R14 IOSTANDARD LVDS_25} [get_ports {in_n[27]}]
set_property -dict {PACKAGE_PIN P15 IOSTANDARD LVDS_25} [get_ports {in_p[28]}]
set_property -dict {PACKAGE_PIN P16 IOSTANDARD LVDS_25} [get_ports {in_n[28]}]
set_property -dict {PACKAGE_PIN R16 IOSTANDARD LVDS_25} [get_ports {in_p[29]}]
set_property -dict {PACKAGE_PIN R17 IOSTANDARD LVDS_25} [get_ports {in_n[29]}]
set_property -dict {PACKAGE_PIN T5 IOSTANDARD LVDS_25} [get_ports {in_p[30]}]
set_property -dict {PACKAGE_PIN U5 IOSTANDARD LVDS_25} [get_ports {in_n[30]}]
set_property -dict {PACKAGE_PIN T9 IOSTANDARD LVDS_25} [get_ports {in_p[31]}]
set_property -dict {PACKAGE_PIN U10 IOSTANDARD LVDS_25} [get_ports {in_n[31]}]
set_property -dict {PACKAGE_PIN T11 IOSTANDARD LVDS_25} [get_ports {in_p[32]}]
set_property -dict {PACKAGE_PIN T10 IOSTANDARD LVDS_25} [get_ports {in_n[32]}]
set_property -dict {PACKAGE_PIN T12 IOSTANDARD LVDS_25} [get_ports {in_p[33]}]
set_property -dict {PACKAGE_PIN U12 IOSTANDARD LVDS_25} [get_ports {in_n[33]}]
set_property -dict {PACKAGE_PIN T14 IOSTANDARD LVDS_25} [get_ports {in_p[34]}]
set_property -dict {PACKAGE_PIN T15 IOSTANDARD LVDS_25} [get_ports {in_n[34]}]
set_property -dict {PACKAGE_PIN T16 IOSTANDARD LVDS_25} [get_ports {in_p[35]}]
set_property -dict {PACKAGE_PIN U17 IOSTANDARD LVDS_25} [get_ports {in_n[35]}]
set_property -dict {PACKAGE_PIN T17 IOSTANDARD LVDS_25} [get_ports {in_p[36]}]
set_property -dict {PACKAGE_PIN R18 IOSTANDARD LVDS_25} [get_ports {in_n[36]}]
set_property -dict {PACKAGE_PIN T20 IOSTANDARD LVDS_25} [get_ports {in_p[37]}]
set_property -dict {PACKAGE_PIN U20 IOSTANDARD LVDS_25} [get_ports {in_n[37]}]
set_property -dict {PACKAGE_PIN U7 IOSTANDARD LVDS_25} [get_ports {in_p[38]}]
set_property -dict {PACKAGE_PIN V7 IOSTANDARD LVDS_25} [get_ports {in_n[38]}]
set_property -dict {PACKAGE_PIN U9 IOSTANDARD LVDS_25} [get_ports {in_p[39]}]
set_property -dict {PACKAGE_PIN U8 IOSTANDARD LVDS_25} [get_ports {in_n[39]}]
set_property -dict {PACKAGE_PIN U13 IOSTANDARD LVDS_25} [get_ports {in_p[40]}]
set_property -dict {PACKAGE_PIN V13 IOSTANDARD LVDS_25} [get_ports {in_n[40]}]
set_property -dict {PACKAGE_PIN U14 IOSTANDARD LVDS_25} [get_ports {in_p[41]}]
set_property -dict {PACKAGE_PIN U15 IOSTANDARD LVDS_25} [get_ports {in_n[41]}]
set_property -dict {PACKAGE_PIN U18 IOSTANDARD LVDS_25} [get_ports {in_p[42]}]
set_property -dict {PACKAGE_PIN U19 IOSTANDARD LVDS_25} [get_ports {in_n[42]}]
set_property -dict {PACKAGE_PIN V6 IOSTANDARD LVDS_25} [get_ports {in_p[43]}]
set_property -dict {PACKAGE_PIN W6 IOSTANDARD LVDS_25} [get_ports {in_n[43]}]
set_property -dict {PACKAGE_PIN V8 IOSTANDARD LVDS_25} [get_ports {in_p[44]}]
set_property -dict {PACKAGE_PIN W8 IOSTANDARD LVDS_25} [get_ports {in_n[44]}]
set_property -dict {PACKAGE_PIN V11 IOSTANDARD LVDS_25} [get_ports {in_p[45]}]
set_property -dict {PACKAGE_PIN V10 IOSTANDARD LVDS_25} [get_ports {in_n[45]}]
set_property -dict {PACKAGE_PIN V12 IOSTANDARD LVDS_25} [get_ports {in_p[46]}]
set_property -dict {PACKAGE_PIN W13 IOSTANDARD LVDS_25} [get_ports {in_n[46]}]
set_property -dict {PACKAGE_PIN V15 IOSTANDARD LVDS_25} [get_ports {in_p[47]}]
set_property -dict {PACKAGE_PIN W15 IOSTANDARD LVDS_25} [get_ports {in_n[47]}]
set_property -dict {PACKAGE_PIN V16 IOSTANDARD LVDS_25} [get_ports {in_p[48]}]
set_property -dict {PACKAGE_PIN W16 IOSTANDARD LVDS_25} [get_ports {in_n[48]}]
set_property -dict {PACKAGE_PIN V17 IOSTANDARD LVDS_25} [get_ports {in_p[49]}]
set_property -dict {PACKAGE_PIN V18 IOSTANDARD LVDS_25} [get_ports {in_n[49]}]
set_property -dict {PACKAGE_PIN V20 IOSTANDARD LVDS_25} [get_ports {in_p[50]}]
set_property -dict {PACKAGE_PIN W20 IOSTANDARD LVDS_25} [get_ports {in_n[50]}]
set_property -dict {PACKAGE_PIN W10 IOSTANDARD LVDS_25} [get_ports {in_p[51]}]
set_property -dict {PACKAGE_PIN W9 IOSTANDARD LVDS_25} [get_ports {in_n[51]}]
set_property -dict {PACKAGE_PIN W11 IOSTANDARD LVDS_25} [get_ports {in_p[52]}]
set_property -dict {PACKAGE_PIN Y11 IOSTANDARD LVDS_25} [get_ports {in_n[52]}]
set_property -dict {PACKAGE_PIN W14 IOSTANDARD LVDS_25} [get_ports {in_p[53]}]
set_property -dict {PACKAGE_PIN Y14 IOSTANDARD LVDS_25} [get_ports {in_n[53]}]
set_property -dict {PACKAGE_PIN W18 IOSTANDARD LVDS_25} [get_ports {in_p[54]}]
set_property -dict {PACKAGE_PIN W19 IOSTANDARD LVDS_25} [get_ports {in_n[54]}]
set_property -dict {PACKAGE_PIN Y7 IOSTANDARD LVDS_25} [get_ports {in_p[55]}]
set_property -dict {PACKAGE_PIN Y6 IOSTANDARD LVDS_25} [get_ports {in_n[55]}]
set_property -dict {PACKAGE_PIN Y9 IOSTANDARD LVDS_25} [get_ports {in_p[56]}]
set_property -dict {PACKAGE_PIN Y8 IOSTANDARD LVDS_25} [get_ports {in_n[56]}]
set_property -dict {PACKAGE_PIN Y12 IOSTANDARD LVDS_25} [get_ports {in_p[57]}]
set_property -dict {PACKAGE_PIN Y13 IOSTANDARD LVDS_25} [get_ports {in_n[57]}]
set_property -dict {PACKAGE_PIN Y16 IOSTANDARD LVDS_25} [get_ports {in_p[58]}]
set_property -dict {PACKAGE_PIN Y17 IOSTANDARD LVDS_25} [get_ports {in_n[58]}]
set_property -dict {PACKAGE_PIN Y18 IOSTANDARD LVDS_25} [get_ports {in_p[59]}]
set_property -dict {PACKAGE_PIN Y19 IOSTANDARD LVDS_25} [get_ports {in_n[59]}]
set_property -dict {PACKAGE_PIN G14 IOSTANDARD LVCMOS25} [get_ports out]
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 2.5 [current_design]
set_property BITSTREAM.GENERAL.COMPRESS FALSE [current_design]
opt_design
place_design
route_design
report_io -file baseline-io.txt
write_checkpoint -force routed.dcp
proc emit {name enabled} {
    for {set i 0} {$i < 60} {incr i} {
        set val [expr {[lsearch -exact $enabled $i] >= 0 ? "TRUE" : "FALSE"}]
        set_property DIFF_TERM $val [get_ports [format {in_p[%d]} $i]]
    }
    report_io -file $name-io.txt
    write_bitstream -force $name.bit
}
emit off {}
emit pair0 {0}
emit pair1 {1}
emit pair2 {2}
emit pair3 {3}
emit pair4 {4}
emit pair5 {5}
emit pair6 {6}
emit pair7 {7}
emit pair8 {8}
emit pair9 {9}
emit pair10 {10}
emit pair11 {11}
emit pair12 {12}
emit pair13 {13}
emit pair14 {14}
emit pair15 {15}
emit pair16 {16}
emit pair17 {17}
emit pair18 {18}
emit pair19 {19}
emit pair20 {20}
emit pair21 {21}
emit pair22 {22}
emit pair23 {23}
emit pair24 {24}
emit pair25 {25}
emit pair26 {26}
emit pair27 {27}
emit pair28 {28}
emit pair29 {29}
emit pair30 {30}
emit pair31 {31}
emit pair32 {32}
emit pair33 {33}
emit pair34 {34}
emit pair35 {35}
emit pair36 {36}
emit pair37 {37}
emit pair38 {38}
emit pair39 {39}
emit pair40 {40}
emit pair41 {41}
emit pair42 {42}
emit pair43 {43}
emit pair44 {44}
emit pair45 {45}
emit pair46 {46}
emit pair47 {47}
emit pair48 {48}
emit pair49 {49}
emit pair50 {50}
emit pair51 {51}
emit pair52 {52}
emit pair53 {53}
emit pair54 {54}
emit pair55 {55}
emit pair56 {56}
emit pair57 {57}
emit pair58 {58}
emit pair59 {59}
emit all {0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59}
emit off-repeat {}
