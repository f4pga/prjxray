Timing minitest
===============

This minitest uses Vivado to compile a design and extracts the relevant timing
metadata from the design, e.g. what are the nets and how was the design routed.

For each clock path, the final timing is provided for each of the 4 corners of
analysis.

From the timing metadata, ``create_timing_worksheet_db.py`` creates a worksheet
breaking down the interconnect timing calculation and generating a final
comparision between the reduced model implemented in prjxray and the Vivado
timing results.

Model quality
-------------

The prjxray timing handles most nets +/- 1.5% delay.  The large exception to
this is clock nets, which appear to use a table lookup that is not understood
at this time.

Running the model
-----------------

The provided Makefile will by default compile all examples.  It a specific design
family is desired, the family name can be provided.  If a specific design within
a family is desired, use ``<family name>_<iter>``.

Example:
```
# Build all variants of the DFF loopback test
make dff
# Build only DESIGN_NAME=dff ITER=63
make dff_63
```
