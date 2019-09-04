.. _architecture_overview-label:

Overview
========

.. todo:: add diagrams.

Xilinx 7-Series architecture utilizes a hierarchical design of chainable
structures to scale across the Spartan, Artix, Kintex, and Virtex product
lines.  This documentation focuses on the Artix and Kintex devices and omits
some concepts introduced in Virtex devices.

At the top-level, 7-Series devices are divided into two :term:`halves <half>`
by a virtual horizontal line separating two sets of global clock buffers
(BUFGs). While global clocks can be connected such that they span both sets of
BUFGs, the two halves defined by this division are treated as separate entities
as related to configuration. The halves are referred to simply as the top and
bottom halves.

Each half is next divided vertically into one or more :term:`horizontal clock
rows <horizontal clock row>`, numbered outward from the global clock buffer
dividing line. Each horizontal clock row contains 12 clock lines that extend
across the device perpendicular to the global clock spine.  Similar to the
global clock spine, each horizontal clock row is divided into two halves by two
sets of horizontal clock buffers (BUFHs), one on each side of the global clock
spine, yielding two :term:`clock domains <clock domain>`.  Horizontal clocks
may be used within a single clock domain, connected to span both clock domains
in a horizontal clock row, or connected to global clocks.

Clock domains have a fixed height of 50 :term:`interconnect tiles
<tile>` centered around the horizontal clock lines (25 above, 25
below). Various function tiles, such as :term:`CLBs <CLB>`, are attached to interconnect
tiles.
