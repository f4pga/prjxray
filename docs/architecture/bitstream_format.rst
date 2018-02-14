Bitstream format
================

.. todo::
  Expand on rough notes

* Specific byte pattern at beginning of file to allow hardware to determine
  width of bus providing configuration data.
* Rest of file is 32-bit big-endian words
* All data before 32-bit synchronization word (0xAA995566) is ignored by
  configuration state machine
* Packetized format used to perform register reads/writes
  * Three packet header types

    * Type 0 packets exist only when performing zero-fill between rows
    * Type 1 used for writes up to 4096 words
    * Type 2 expands word count field to 27 bits by omitting register address
    * Type 2 must always be proceeded by Type 1 which sets register address

  * NOP packets are used for inserting required delays
  * Most registers only accept 1 word of data
  * Allowed register operations depends on interface used to send packets

    * Writing LOUT via JTAG is treated as a bad command
    * Single-frame FDRI writes via JTAG fail

* CRC

  * Calculated automatically from writes: register address and data written
  * Expected value is written to CRC register
  * If there is a mismatch, error is flagged in status register
  * Writes to CRC register can be safely removed from a bitstream
  * Alternatively, replace with write to command register to reset calculated
    CRC value

* Xilinx BIT header

  * Additional information about how bitstream was generated
  * Unofficially documented at
    http://www.fpga-faq.com/FAQ_Pages/0026_Tell_me_about_bit_files.htm
  * Really does require NULL-terminated Pascal strings
  * Having this header is the distinction between .bin and .bit in Vivado
  * Is ignored entirely by devices
