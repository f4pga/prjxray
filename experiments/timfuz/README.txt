Timing analysis fuzzer
This runs some random designs through Vivado and extracts timing information in order to derive timing models
While Vivado has more involved RC (spice?) models incorporating fanout and other things,
for now we are shooting for simple, conservative models with a min and max timing delay


*******************************************************************************
Background
*******************************************************************************

Vivado seems to associate each delay model with a "speed index"
In particular, we are currently looking at pips and wires, each of which have a speed index associated with them
For every timeing path, we record the total delay from one site to another, excluding site delays
(timing analyzer provides an option to make this easy)
We then walk along the path and record all wires and pips in between
These are converted to their associated speed indexes
This gives an equation that a series of speed indexes was given a certain delay value
These equations are then fed into scipy.optimize.linprog to give estimates for the delay models

However, there are some complications. For example:
Given a system of equations like:
t0           = 5
t0 + t1      = 10
t0 + t1 + t2 = 12
The solver puts all the delays in t0
To get around this, we subtract equations from each other

Some additional info here: https://github.com/SymbiFlow/prjxray/wiki/Timing


*******************************************************************************
Quick start
*******************************************************************************

./speed.sh
python timfuz_delay.py --cols-max 9 timfuz_dat/s1_timing2.txt
Which will report something like 
Delay on 36 / 162

Now add some more data in:
python timfuz_delay.py --cols-max 9 timfuz_dat/speed_json.json timfuz_dat/s*_timing2.txt
Which should get a few more delay elements, say:
Delay on 57 / 185


*******************************************************************************
From scratch
*******************************************************************************

Roughly something like this
Edit generate.tcl
Uncomment speed_models2
Run "make N=1"
python speed_json.py specimen_001/speed_model.txt speed_json.json
Edit generate.tcl
Comment speed_models2
Run "make N=4" to generate some more timing data
Now run as in the quick start
python timfuz_delay.py --cols-max 9 speed_json.json specimen_*/timing2.txt


*******************************************************************************
TODO:
*******************************************************************************

Verify elements are being imported correctly throughout the whole chain
Can any wires or similar be aggregated?
    Ex: if a node consisents of two wire delay models and that pair is never seen elsewhere
Look at virtual switchboxes. Can these be removed?
Look at suspicous elements like WIRE_RC_ZERO

