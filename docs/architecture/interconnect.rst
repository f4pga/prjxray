Interconnect :term:`PIPs <pip>`
===============================

Fake :term:`PIPs <pip>`
-----------------------

Some :term:`PIPs <pip>` are not "real", in the sense that no bit pattern in the bit-stream correspond to the PIP being used. This is the case for all the :term:`PIPs <pip>` in the switchbox in a CLB tile (ex: CLBLM_L_INTER): They either correspond to buffers that are always on (i.e. 1:1 connections such as `CLBLL_L.CLBLL_L_AQ->CLBLL_LOGIC_OUTS0`), or they correspond to permutations of LUT input signals, which is handled by changing the LUT init value accordingly, or they are used to "connect" two signals that are driven by the same signal from within the CLB.

.. warning:: FIXME: Check the above is true.

The bit switchbox in an :term:`INTs <INT>` tile also contains a few 1:1 connections that are in fact always present and have no corresponding configuration bits.

Regular :term:`PIPs <pip>`
--------------------------

Regular :term:`PIPs <pip>` correspond to a bit pattern that is present in the bit stream when the PIP is used in the current design. There is a block of up to 10-ish bits for each destination signal. For each configuration (i.e. source net that can drive the destination) there is a pair of bits that is set.

.. warning:: FIXME: Check if the above is true for PIPs outside of the INT switch box.

For example, when the bits 05_57 and 11_56 are set then SR1END3->SE2BEG3 is enabled, but when 08_56 and 11_56 are set then ER1END3->SE2BEG3 is enabled (in an :term:`INT_L <INT>` tile paired with a CLBLL_L tile). A configuration in which all three bits are set is invalid. See `segbits_int_[lr].db` for a complete list of bit pattern for configuring :term:`PIPs <pip>`.

VCC Drivers
-----------

The default state for a net is to be driven high. The :term:`PIPs <pip>` that drive a net from `VCC_WIRE` correspond to the "empty configuration" with no bits set.

Bidirectional :term:`PIPs <pip>`
--------------------------------

Bidirectional :term:`PIPs <pip>` are used to stitch together long traces (LV*, LVB*). In case of bidirectional :term:`PIPs <pip>` there are two different configuration patterns, one for each direction.
