Bitstream format
================

FPGAs are configured with a binary file called the bitstream.
The bitstream carries the information on which logical elements on the fabric should be configured and how in order to implement the target design.
Moreover, it contains vital information on how to perform the configuration.
The format of the bitstream is architecture specific, although the formats for devices of the same vendor often share a number of features.
This chapter covers some details of the bitstream format for FPGA architectures which are currently supported in SymbiFlow's bitstream manipulation tools.

Xilinx
------

Xilinx provides a big variety of architectures (Spartan6, Series7, UltraScale, UltraScale+) that differ in the list of features and size.
Despite these differences the bitstream format is pretty much alike and differs in some small details.

Bitstream header
++++++++++++++++

The bitstream header contains various information about the origin and content of the entire bitstream, such as generation timestamp, name of target part or length of the configuration data.
The header itself is ignored by the device as only the subsequent words take part in the configuration process.
The presence of the bit header provides the distinction between .bin and .bit for HDL software like ``Vivado``.
The data in the header is stored in the `Tag-Length-Value(TLV) <http://www.fpga-faq.com/FAQ_Pages/0026_Tell_me_about_bit_files.htm>`_ format.

Synchronization word
++++++++++++++++++++

Before any configuration packet is processed by the FPGA the configuration logic needs to find the synchronization word.
The so called ``Sync word`` for Xilinx devices is ``0xAA995566``.
It is used to allow the configuration logic to align at a 32-bit word boundary and requires the bus width to be detected successfully for parallel configuration mode beforehand.

Bus Width Auto Detection
++++++++++++++++++++++++

A specific byte pattern is inserted at the beginning of the bitstream file to allow the hardware to determine the width of the bus providing the configuration data.
The configuration logic checks the lower eight bits of the parallel bus and depending on the received sequence the appropriate external bus width is chosen.
The pattern is inserted before the 32-bit synchronization word and is ignored by the configuration state machine.

Configuration Packets
+++++++++++++++++++++

All words that follow the synchronization word are interpreted by the configuration logic.
Depending on the architecture the words are interpreted as 16 or 32 bit big-endian words and form the configuration packets.
There are three types of packets identified by the header which can contain three major commands: NOP, READ, WRITE.
While NOP is used for inserting required delays in the configuration sequence the most common are read and write operations.
These supported packet types are:

* Type 0 - these packets exist only when performing zero-fill between rows
* Type 1 - used for read/writes of a number of words specified by the word count portion of the header which differs between architectures
* Type 2 - this type of packets expands the word count field that Type 1 packets have.
  For Series-7 FPGAs Type 2 expands to 27 bits by omitting the register address, but has to follow a Type 1 packet which carries the address information.
  Spartan6's Type 2 packets still contain the frame address, however the configuration logic expects the header to be followed by two 16-bit words with the MSB in the first word.


Configuration Registers
+++++++++++++++++++++++

The addresses that are specified in the configuration packets are mapped to a set of registers that provide low-level control over the chip.
Only some of them take part in the programming sequence whereas the rest controls various physical aspects of the configuration interface.
Some of the key registers used during programming are:

* IDCODE - Before writing to the configuration memory, a 32-bit device ID code must be written to this register. Reads from the register return the attached device's ID code.
* CRC - When a packet is received by the device, it automatically updates an internal CRC calculation to include the contents of that packet. A write to the CRC register checks that the calculated CRC matches the expected value written to the register. This CRC check is only used to provide integrity checking of the packet stream, not the configuration memory contents, and are not required for programming. If you are modifying a bitstream, CRC writes can simply be removed instead of recalculating them.
* Command - Most of the programming sequence is implemented as a state machine that is controlled via one-shot actions. Writes to this register arm an action that, depending on the action requested, may be triggered immediately or delayed until some other condition is met. During autoincremented frame writes, the current command is rewritten during every autoincrement. This has the effect of rearming the action on every frame written.
* Frame Address Register (FAR) - Writes to this register set the starting address for the next frame read or write.
* FDRI - When a frame is written to FDRI, the frame data is written to the configuration memory address specified by FAR. If the write to FDRI contains more than one frame, FAR is autoincremented at the end of each frame.

For more information on the available configuration registers refer to the configuration guides for `Series-7 <https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf>`_ (table 5.23) and `Spartan6 <https://www.xilinx.com/support/documentation/user_guides/ug380.pdf>`_ (table 5.30).

Configuration Sequence
++++++++++++++++++++++

The basic steps for configuring a Series-7 and a Spartan6 device are the same.
The first steps are responsible for the setup and include power-up, clearing the configuration memory and sampling mode pins.
Further steps are related to loading the bitstream which is done in the following stages:

* synchronization
* check device ID
* load configuration data frames
* CRC check
* startup sequence

More details on the configuration sequence can be found in the `Series-7 configuration guide <https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf>`_ (page 84)

Example programming sequence
****************************

A high-level overview of a programming sequence for a Series-7 device is presented in the table below:

===================  ==============  ============
Command              Data            Description
===================  ==============  ============
Write TIMER          0x00000000	     Disable the watchdog timer
Write WBSTAR	     0x00000000	     On the next device boot, start with the bitstream at address zero. This may be different if the bitstream contains a multi-boot configuration.
Write COMMAND	     0x00000000	     Switch to the NULL command.
Write COMMAND	     0x00000007	     Reset the calculated CRC to zero.
Write register 0x13  0x00000000	     Undocumented register. No idea what this does yet.
Write COR0	     0x02003fe5	     Setup timing of various device startup operations such as which startup cycle to wait in until MMCMs have locked and which clock settings to use during startup.
Write COR1	     0x00000000	     Writing defaults to various device options such as the page size used to read from BPI and whether continuous configuration memory CRC calculation is enabled.
Write IDCODE	     0x0362c093      Tell the device that this is a bitstream for a XC7A50T. If the device is an XC7A50T, configuration memory writes will be enabled.
Write COMMAND	     0x00000009	     Activate the clock configuration specified in Configuration Option Register 0. Up to this point, the device was using whatever clock configuration the last loaded bitstream used.
Write MASK	     0x00000401	     Set a bit-wise mask that is applied to subsequent writes to Control 0 and Control 1. This seems unnecessary for programming but is used to toggle certain bits in those registers instead of using precomputed values.
                                     It might make more sense in a use case where the exact value of Control 0 or Control 1 is unknown but a bit needs to be flipped.
Write Control 0	     0x00000501	     Due to the previous write to MASK, 0x401 is actually written to this register which is the default value. Mostly disable fallback boot mode and masks out memory bits in the configuration memory during readback.
Write MASK	     0x00000000      Clear the write mask for Control 0 and Control 1
Write Control 1	     0x00000000      Control 1 is officially undocumented.
Write FAR	     0x00000000      Set starting address for frame writes to zero.
Write COMMAND	     0x00000001	     Arm a frame write. The write will occur on the next write to FDRI.
Write FDRI	     <547420 words>  Write desired configuration to configuration memory. Since more than 101 words are written, FAR autoincrementing is being used. 547420 words is 5420 frames. Between each frame, COMMAND will be rewritten with 0x1 which re-arms the next write.
                                     Note that the configuration memory space is fragmented and autoincrement moves to the next valid address.
Write COMMAND	     0x0000000A	     Update the routing and configuration flip-flops with the new values in the configuration memory. At this point, the device configuration has been updated but the device is still in programming mode.
Write COMMAND        0x00000003	     Tell the device that the last configuration frame has been received. The device re-enabled its interconnect.
Write COMMAND	     0x00000005	     Arm the device startup sequence. Documentation claims both a valid CRC check and a DESYNC command are required to trigger the startup. In practice, a bitstream with no CRC checks works just fine.
Write COMMAND	     0x0000000D	     Exit programming mode. After this, the device will ignore data on the configuration interfaces until the sync word is seen again. This also triggers the previously armed device startup sequence.
===================  ==============  ============




Differences in the programming sequence between Xilinx architectures
********************************************************************

As stated at the beginning of this chapter the bitstream formats for various Xilinx devices have a lot in common.
However, there are some small differences which include:

* Device ID - the ID is not only architecture, but actually part specific.
* Configuration Frame Length - number of words in a configuration frame for Series7 is 101, UltraScale - 123, UltraScale+ - 93 and 65 for Spartan6.
* Configuration Registers - The registers and the corresponding addresses are shared among Series7, UltraScale and UltraScale+ architectures, Spartan6 however has a different set of these registers which has to be taken into account during the configuration sequence.

Other features
++++++++++++++

* CRC

  * Calculated automatically from writes: register address and data written
  * Expected value is written to CRC register
  * If there is a mismatch, error is flagged in status register
  * Writes to CRC register can be safely removed from a bitstream
  * Alternatively, replace with write to command register to reset calculated
    CRC value
