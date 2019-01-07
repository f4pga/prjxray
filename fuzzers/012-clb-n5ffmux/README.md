# CLBn5FFMUX Fuzzer

## Purpose
Document A5FFMUX family of CLB muxes

## Algorithm
5FFMUX  
Inputs can come from either the LUT6_2 NO5 output or the CLB NX input  
To perturb the CLB the smallest, want LUT6 always instantiated  
However, some routing congestion that would require putting FFs in bypass  
(which turns out is actually okay, but didn't realize that at the time)  
Decided instead ot instantiate LUT8, but not use the output  
Turns out this is okay and won't optimize things away  
So then, the 5FF D input is switched between the O5 output and an external CLB input  

## Outcome
Bits are one hot encoded per mux position

