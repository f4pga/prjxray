# Timing analysis fuzzer (timfuz)

WIP: 2018-09-10: this process is just starting together and is going to get significant cleanup. But heres the general idea

This runs various designs through Vivado and processes the
resulting timing informationin order to create very simple timing models.
While Vivado might have more involved models (say RC delays, fanout, etc),
timfuz creates simple models that bound realistic min and max element delays.

Currently this document focuses exclusively on fabric timing delays.


## Quick start

```
make -j$(nproc)
```

This will take a relatively long time (say 45 min) and generate build/timgrid-v.json.
You can do a quicker test run (say 3 min) using:

```
make PRJ=oneblinkw PRJN=1 -j$(nproc)
```


## Vivado background

Examples are for a XC750T on Vivado 2017.2.

TODO maybe move to: https://github.com/SymbiFlow/prjxray/wiki/Timing


### Speed index

Vivado seems to associate each delay model with a "speed index".
The fabric has these in two elements: wires (ie one delay element per tile) and pips.
For example, LUT output node A (ex: CLBLL_L_X12Y100/CLBLL_LL_A) has a single wire, also called CLBLL_L_X12Y100/CLBLL_LL_A.
This has speed index 733. Speed models can be queried and we find this corresponds to model C_CLBLL_LL_A.

There are various speed model types:
* bel_delay
* buffer
* buffer_switch
* content_version
* functional
* inpin
* outpin
* parameters
* pass_transistor
* switch
* table_lookup
* tl_buffer
* vt_limits
* wire

IIRC the interconnect is only composed of switch and wire types.

Indices with value 65535 (0xFFFF) never appear. Presumably these are unused models.
They are used for some special models such as those of type "content_version".
For example, the "xilinx" model is of type "content_version".

There are also "cost codes", but these seem to be very course (only around 30 of these)
and are suspected to be related more to PnR than timing model.


### Timing paths

The Vivado timing analyzer can easily output the following:
* Full: delay from BEL pin to BEL pin
* Interconnect only (ICO): delay from BEL pin to BEL pin, but only report interconnect delays (ie exclude site delays)

There is also theoretically an option to report delays up to a specific pip,
but this option is poorly documented and I was unable to get it to work.

Each timing path reports a fast process and a slow process min and max value. So four process values are reported in total:
* fast_max
* fast_min
* slow_max
* slow_min

For example, if the device is end of life, was poorly made, and at an extreme temperature, the delay may be up to the slow_max value.
Since ICO can be reported for each of these, fully analyzing a timing path results in 8 values.

Finally, part of this was analyzing tile regularity to discover what a reasonably compact timing model was.
We verified that all tiles of the same type have exactly the same delay elements.



## Methodology

Make sure you've read the Vivado background section first


### Background

This section briefly describes some of the mathmatics used by this technique that readers may not be familiar with.
These definitions are intended to be good enough to provide a high level understanding and may not be precise.

Numerical analysis: the study of algorithms that use numerical approximation (as opposed to general symbolic manipulations)

numpy: a popular numerical analysis python library. Often written np (import numpy as np).

scipy: provides higher level functionality on top of numpy

sympy ("symbolic python"): like numpy, but is designed to work with rational numbers.
For example, python actually stores 0.1 as 0.1000000000000000055511151231257827021181583404541015625.
However, sympy can represent this as the fraction 1/10, eliminating numerical approximation issues.

Least squares (ex: scipy.optimize.least_squares): approximation method to do a best fit of several variables to a set of equations.
For example, given the equations "x = 1" and "x = 2" there isn't an exact solution.
However, "x = 1.5" is a good compromise since its reasonably solves both equations.

Linear programming (ex: scipy.optimize.linprog aka linprog): approximation method that finds a set of variables that satisfy a set of inequalities.
For example,

Reduced row echelon form (RREF, ex: sympy.Matrix.rref): the simplest form that a system of linear equations can be solved to.
For example, given "x = 1" and "x + y = 9", one can solve for "x = 1" and "y = 8".
However, given "x + y = 1" and "x + y + z = 9", there aren't enough variables to solve this fully.
In this case RREF provides a best effort by giving the ratios between correlated variables.
One variable is normalized to 1 in each of these ratios and is called the "pivot".
Note that if numpy.linalg.solve encounters an unsolvable matrix it may either complain
or generate a false solution due to numerical approximation issues.


### What didn't work

First some quick background on things that didn't work to illustrate why the current approach was chosen.
I first tried to directly through things into linprog, but it unfairly weighted towards arbitrary shared variables. For example, feeding in:
* t0 >= 10
* t0 + t1 >= 100

It would declare "t0 = 100", "t1 = 0" instead of the more intuitive "t0 = 10", "t1 = 90".
I tried to work around this in several ways, notably subtracting equations from each other to produce additional constraints.
This worked okay, but was relatively slow and wasn't approaching nearly solved solutions, even when throwing a lot of data at it.

Next we tried randomly combining a bunch of the equations together and solving them like a regular linear algebra matrix (numpy.linalg.solve).
However, this illustrated that the system was under-constrained.
Further analysis revealed that there are some delay element combinations that simply can't be linearly separated.
This was checked primarily using numpy.linalg.matrix_rank, with some use of numpy.linalg.slogdet.
matrix_rank was preferred over slogdet since its more flexible against non-square matrices.


### Process

Above ultimately led to the idea that we should come up with a set of substitutions that would make the system solvable. This has several advantages:
* Easy to evaluate which variables aren't covered well enough by source data
* Easy to evaluate which variables weren't solved properly (if its fully constrained it should have had a non-zero delay)

At a high level, the above learnings gave this process:
* Find correlated variables by using RREF (sympy.Matrix.rref) to create variable groups
  - Note pivots
  - You must input a fractional type (ex: fractions.Fraction, but surprisingly not int) to get exact results, otherwise it seems to fall back to numerical approximation
  - This is by far the most computationally expensive step
  - Mixing RREF substitutions from one data set to another may not be recommended
* Use RREF result to substitute groups on input data, creating new meta variables, but ultimately reducing the number of columns
* Pick a corner
  - Examples assume fast_max, but other corners are applicable with appropriate column and sign changes
* De-duplicate by removing equations that are less constrained
  - Ex: if solving for a max corner and given:
  - t0 + t1 >= 10
  - t0 + t1 >= 12
  - The first equation is redundant since the second provides a stricter constraint
  - This significantly reduces computational time
* Use least squares (scipy.optimize.least_squares) to fit variables near input constraints
  - Helps fairly weight delays vs the original input constraints
  - Does not guarantee all constraints are met. For example, if this was put in (ignoring these would have been de-duplicated):
  - t0 = 10
  - t0 = 12
  - It may decide something like t0 = 11, which means that the second constraint was not satisfied given we actually want t0 >= 12
* Use linear programming (scipy.optimize.linprog aka linprog) to formally meet all remaining constraints
  - Start by filtering out all constraints that are already met. This should eliminate nearly all equations
* Map resulting constraints onto different tile types
  - Group delays map onto the group pivot variable, typically setting other elements to 0 (if the processed set is not the one used to create the pivots they may be non-zero)


## TODO

Milestone 1 (MVP)
* DONE
* Provide any process corner with at least some of the fabric

Milestone 2
* Provide all four fabric corners
* Simple makefile based flow
* Cleanup/separate fabric input targets

Milestone 3
* Create site delay model

Final
* Investigate ZERO
* Investigate virtual switchboxes
* Compare our vs Xilinx output on random designs


### Improve test cases

Test cases are somewhat random right now. We could make much more targetted cases using custom routing to improve various fanout estimates and such.
Also there are a lot more elements that are not covered.
At a minimum these should be moved to their own directory.


### ZERO models

Background: there are a number of speed models with the name ZERO in them.
These generally seem to be zero delay, although needs more investigation.

Example: see virtual switchbox item below

The timing models will probably significantly improve if these are removed.
In the past I was removing them, but decided to keep them in for now in the spirit of being more conservative.

They include:
 * _BSW_CLK_ZERO
 * BSW_CLK_ZERO
 * _BSW_ZERO
 * BSW_ZERO
 * _B_ZERO
 * B_ZERO
 * C_CLK_ZERO
 * C_DSP_ZERO
 * C_ZERO
 * I_ZERO
 * _O_ZERO
 * O_ZERO
 * RC_ZERO
 * _R_ZERO
 * R_ZERO


### Virtual switchboxes

Background: several low level configuration details are abstracted with virtual configurable elements.
For example, LUT inputs can be rearranged to reduce routing congestion.
However, the LUT configuratioon must be changed to match the switched inputs.
This is handled by the CLBLL_L_INTER switchbox, which doesn't encode any physical configuration bits.
However, this contains PIPs with delay models.

For example, LUT A, input A1 has node CLBLM_M_A1 coming from pip junction CLBLM_M_A1 has PIP CLBLM_IMUX7->CLBLM_M_A1
with speed index 659 (R_ZERO).

This might be further evidence on related issue that ZERO models should probably be removed.


### Incporporate fanout

We could probably significantly improve model granularity by studying delay impact on fanout


### Investigate RC delays

Suspect accuracy could be significantly improved by moving to SPICE based models. But this will take significantly more characterization


### Characterize real hardware

A few people have expressed interest on running tests on real hardware. Will take some thought given we don't have direct access


### Review approximation errors

Ex: one known issue is that the objective function linearly weights small and large delays.
This is only recommended when variables are approximately the same order of magnitude.
For example, carry chain delays are on the order of 7 ps while other delays are 100 ps.
Its very easy to put a large delay on the carry chain while it could have been more appropriately put somewhere else.

