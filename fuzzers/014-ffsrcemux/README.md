# FFSRCEMUX Fuzzer

## Purpose
Document CEUSEDMUX, SRUSEDMUX muxes

## Algorithm

## Results

### CEUSEDMUX: whether clock enable (CE) is used or clock always on
0: always on  
1: controlled  
CLB.SLICE_X0.CEUSEDMUX 00_39  
CLB.SLICE_X1.CEUSEDMUX <0 candidates>  


### SRUSEDMUX: whether FF can be reset or simply uses D value
(How used when SR?)  
0: never reset  
1: controlled  
CLB.SLICE_X0.SRUSEDMUX 00_35  
CLB.SLICE_X1.SRUSEDMUX <0 candidates>  

