Adding New Fuzzer
=================

This chapter describes how to create a new fuzzer using a DSP as an example target primitive.
The files that are generated with such fuzzer have been described in more detail in the :doc:`Database<../dev_database/index>` chapter.
The process of creating a new fuzzer consists of two elements, namely base address calculation and feature fuzzing.

Base Address Calculation
------------------------

The base address calculation is based on segmatching (statistical
constraint solver) the base addresses. A similar technique is used in
most fuzzers for solving configuration bits.

Methodology
+++++++++++

In this technique all IP blocks are changed in parallel. This means that
log(N, 2) bitstreams are required instead of N to get the same number of
base addresses. However, as part of this conversion, address propagation
is also generally discouraged. So it is also recommended to toggle bits
in all IP blocks in a column, not just one. In the CLB case, this means
that every single CLB tile gets one bit set to a random value. If there
are 4 CLB CMT columns in the ROI, this means we'd randomly set 4 * 50
bits in every bitstream. With 200 bits, it takes minimum floor(log(200,
2)) => 8 bitstreams (specimens) to solve all of them.

Calculating the base address
++++++++++++++++++++++++++++

#.  Find a tilegrid fuzzer to copy, e.g. "dsp"

#.  Enter your copied directory

#.  Edit `top.py`

    a.  Refer to the `Xilinx 7 Series Library guide <https://www.xilinx.com/support/documentation/sw_manuals/xilinx2012_2/ug953-vivado-7series-libraries.pdf>`_ and/or Vivado layout to understand the primitive you need to instantiate

    b.  Find a single bit parameter that can be easily toggled, such as a clock inverter or a bulk configuration bit

    c.  Find the correct site type in gen_sites()

    d.  Instantiate the correct verilog library macro in top

    e.  LOC it, if necessary. It's necessary to LOC it if there is more than one

#.  Run make, and look at Vivado's output. Especially if you took shortcuts instantiating your macro (ex: not connecting critical ports) you may need to add DRC waivers to generate.tcl

#.  Inspect the ``build/segbits_tilegrid.tdb`` to observe bit addresses, for example ``DSP_L_X22Y0.DWORD:0.DFRAME:1b 0040171B_000_01``

    #.  The ``DFRAME`` etc entries are deltas to convert this feature offset to the base address for the tile

    #.  We will fix them in the subsequent step

#.  Correct Makefile's ``GENERATE_ARGS`` to make it the section base address instead of a specific bit in that memory region

    #.  Align address to 0x80: 0x0040171B => --dframe 1B to yield a base address of 0x00401700

    #.  Correct word offset. This is harder since it requires some knowledge of how and where the IP block memory is as a whole

        i.  If there is only one tile of this type in the DSP column:
            start by assuming it occupies the entire address range.
            In this step add a delta to make the word offset 0 (--dword 0) and later indicate that it occupies 101 words (all of them)

        ii. If there are multiple: compare the delta between adjacent tiles to get the pitch.
            This should give an upper bound on the address size.
            Make a guess with that in mind and you may have to correct it later when you have better information.

    #.  Align bits to 0: 1 => --dbit 1

#.  Run ``make clean && make``

#.  Verify ``build/segbits_tilegrid.tdb`` now looks resolved

    #.  Ex: ``DSP_L_X22Y0.DWORD:0.DFRAME:1b 0040171B_000_01``

    #.  In this case there were several DSP48 sites per DSP column

#.  Find the number of frames for your tile

    #.  Run ``$XRAY_BLOCKWIDTH build/specimen_001/design.bit``

    #.  Find the base address you used above i.e. we used ``0x00401700``, so use ``0x00401700: 0x1B`` (0x1C => 28)

    #.  This information is in the part YAML file, but is not as easy to read

#. Return to the main tilegrid directory

#. Edit ``tilegrid/add_tdb.py``

   #.  Find ``tdb_fns`` and add an entry for your tile type e.g. ``(dsp/build/segbits_tilegrid.tdb", 28, 10)``

   #.  This is declared to be 28 frames wide and occupy 10 words per tile in the DSP column

#. Run ``make`` in the tilegrid directory

#. Look at ``build/tilegrid.json``

   #.  Observe your base address(es) have been inserted (look for bits ``CLB_IO_CLK`` entry in the ``DSP_L_*`` tiles)

Feature Fuzzing
---------------

The general idea behind fuzzers is to pick some element in the device (say a block RAM or IOB) to target and write a design that is implemented in a specific element.
Next, we need to create variations of the design (called specimens) that vary the design parameters, for example, changing the configuration of a single pin and process them in Vivado in order to obtain the respective bitstreams.
Finally, by looking at all the resulting specimens, the information which bits in which frame correspond to a particular choice in the design can be correlated.
Looking at the implemented design in Vivado with "Show Routing Resources" turned on is quite helpful in understanding what all choices exist.

Fuzzer structure
++++++++++++++++

Typically a fuzzer directory consists of a mixture of makefiles, bash,
python and tcl scripts. Many of the scripts are shared among fuzzers and
only some of them have to be modified when working on a new fuzzer.

-   Makefile and a number of sub-makefiles contain various targets that
    have to be run in order to run the fuzzer and commit the results
    to the final database. The most important ones are:

    -   *run* - run the fuzzer to generate the netlist, create
        bitstreams in Vivado, solve the bits and update the final
        database with the newly calculated results.

    -   *database -* run the fuzzer without updating the final database

The changes usually done in the Makefile concern various script
parameters, like number of specimen, regular expressions for inclusion
or exclusion list of features to be calculated or maximal number of
iterations the fuzzer should try to solve the bits for.

-   *top.py* - Python script used to generate the verilog netlist which
    will be used by the fuzzer for all Vivado runs.

-   *generate.tcl -* tcl script used by Vivado to read the base verilog
    design, if necessary tweak some properties and write out the
    specimen bitstreams

-   *generate.py -* Python script that reads the generated bitstream and
    takes a parameterized description of the design (usually in the
    form of a csv file) in order to produce a file with information
    about which features are enabled and which are disabled in a given
    segment.

Creating the fuzzer
+++++++++++++++++++

1.  Open the *top.py* script and modify the content of the top module by
    instantiating a DSP primitive and specifying some parameters. Use
    LOC and DONT_TOUCH attributes to avoid some design optimization
    since the netlists are in many cases very artificial.

2.  Make sure the *top.py* script generates apart from the top.v
    netlist, a csv file with the values of parameters used in the
    generated netlist.

3.  Modify the *generate.tcl* script to read the netlist generated in
    step 1, apply, if necessary, some parameters from the csv file
    generated in step 2 and write out the bitstream

4.  Modify the *generate.py* script to insert the tags, which signify
    whether a feature is disabled or enabled in a site, based on the
    csv parameters file generated in step 1
