meta:
  id: xilinx_bitstream
  title: Xilinx FPGA Bitstream
  license: Apache-2.0
  endian: be
seq:
  - id: padding
    terminator: 0xaa
  - id: magic
    contents: [0x99, 0x55, 0x66]
  - id: contents
    type: packet
    repeat: eos
types:
  packet:
    seq:
      - id: header
        size: 4
        type: header
      - id: data
        if: header.opcode != opcode::nop
        size: header.word_count * 4
        type:
          switch-on: header.register_address
          cases:
            register::crc: reg_crc
            register::timer: reg_timer
            register::wbstar: reg_wbstar
            register::cmd: reg_cmd
            register::cor0: reg_cor0
            register::cor1: reg_cor1
            register::idcode: reg_idcode
            register::mask: reg_mask
            register::ctl0: reg_ctl0
            register::ctl1: reg_ctl1
            register::far: reg_far
            register::fdri: reg_fdri
  header:
    seq:
      - id: type
        type: b3
      - id: opcode
        type: b2
        enum: opcode
      - id: register_address
        type: b14
        enum: register
        if: type == 0x1
      - id: reserved
        type: b2
        if: type == 0x1
      - id: word_count
        type: b11
        if: type == 0x1
      - id: word_count
        type: b27
        if: type == 0x2
  reg_crc:
    seq:
      - id: expected_crc
        type: u4
  reg_timer:
    seq:
      - id: timer_usr_mon
        type: b1
        enum: enable
      - id: timer_cfg_mon
        type: b1
        enum: enable
      - id: timer_value
        type: b30
  reg_wbstar:
    seq:
      - id: rs
        type: b2
        doc: 'RS[1:0] pin value on next warm boot.'
      - id: rs_ts_b
        type: b1
        doc: 'Whether RS[1:0] are tristated on next warm boot.'
        enum: tristate_enable
      - id: start_address
        type: b29
        doc: 'Address of bitstream to start on next warm boot.'
  reg_cmd:
    seq:
      - id: command
        type: u4
        enum: command
  reg_cor0:
    seq:
      - id: pwrdwn_stat
        type: b1
        enum: cor0_pwrdwn_stat
      - id: done_pipe
        type: b1
        doc: 'When set, adds a register between DONEIN and any configuration logic'
      - id: drive_done
        type: b1
        enum: cor0_drive_done
      - id: single
        type: b1
        doc: 'When set, readback is a single-shot operation and must be reset by loading RCAP into CMD.'
      - id: oscfsel
        type: b6
        doc: 'CCLK frequency in MHz when in Master modes'
      - id: ssclksrc
        type: b2
        enum: cor0_ssclksrc
      - id: done_cycle
        type: b3
        enum: cor0_startup_phase
      - id: match_cycle
        type: b3
        enum: cor0_startup_phase_no_wait
      - id: lock_cycle
        type: b3
        enum: cor0_startup_phase_no_wait
      - id: gts_cycle
        type: b3
        enum: cor0_startup_phase
      - id: gwe_cycle
        type: b3
        enum: cor0_startup_phase
  reg_cor1:
    seq:
      - id: reserved
        type: u4
  reg_idcode:
    seq:
      - id: idcode
        type: u4
  reg_mask:
    seq:
      - id: mask
        type: u4
  reg_ctl0:
    seq:
      - id: efuse_key
        type: b1
        enum: ctl0_efuse_key
      - id: icap_select
        type: b1
        enum: ctl0_icap_select
      - id: reserved1
        type: b17
      - id: overtemp_power_down
        type: b1
        enum: enable
      - id: reserved2
        type: b1
      - id: config_fallback
        enum: disable
        type: b1
      - id: reserved3
        type: b1
      - id: glutmask_b
        type: b1
        enum: ctl0_glutmask_b
      - id: farsrc
        type: b1
        enum: ctl0_farsrc
      - id: dec
        type: b1
        enum: enable
      - id: sbits
        type: b2
        enum: ctl0_sbits
      - id: persist
        type: b1
        enum: enable
      - id: gts_usr_b
        type: b1
        enum: tristate_enable
  reg_ctl1:
    seq:
      - id: reserved
        type: u4
  reg_far:
    seq:
      - id: reserved
        type: b7
      - id: block_type
        type: b2
        enum: far_block_type
      - id: is_bottom_half_rows
        type: b1
      - id: row_address
        type: b5
      - id: column_address
        type: b10
      - id: minor_address
        type: b7
  reg_fdri:
    seq:
      - id: frames
        type: frame
        repeat: eos
  frame:
    seq:
      - id: config_word
        type: u4
        repeat: expr
        repeat-expr: 101
enums:
  opcode:
    0: nop
    1: read
    2: write
    3: reserved
  register:
    0: crc
    1: far
    2: fdri
    3: fdro
    4: cmd
    5: ctl0
    6: mask
    7: stat
    8: lout
    9: cor0
    10: mfwr
    11: cbc
    12: idcode
    13: axxs
    14: cor1
    16: wbstar
    17: timer
    22: bootsts
    24: ctl1
    31: bspi
  enable:
    0: disabled
    1: enabled
  disable:
    0: enabled
    1: disabled
  tristate_enable:
    0: tristate
    1: driven
  command:
    0: 'null'
    1: wcfg
    2: mfw
    3: dghigh_lfrm
    4: rcfg
    5: start
    6: rcap
    7: rcrc
    8: aghigh
    9: switch
    10: grestore
    11: shutdown
    12: gcapture
    13: desync
    15: iprog
    16: crcc
    17: ltimer
    18: bspi_read
    19: fall_edge
  cor0_pwrdwn_stat:
    0: done_pin
    1: powerdown_pin
  cor0_startup_phase_no_wait:
    0: startup_phase_0
    1: startup_phase_1
    2: startup_phase_2
    3: startup_phase_3
    4: startup_phase_4
    5: startup_phase_5
    6: startup_phase_6
    7: no_wait
  cor0_startup_phase:
    0: startup_phase_1
    1: startup_phase_2
    2: startup_phase_3
    3: startup_phase_4
    4: startup_phase_5
    5: startup_phase_6
    6: track_done
    7: keep
  cor0_ssclksrc:
    0: cclk
    1: userclk
    2: jtagclk
    3: jtagclk
  cor0_drive_done:
    0: open_drain
    1: drive_high
  ctl0_efuse_key:
    0: battery_backed_ram
    1: efuse
  ctl0_icap_select:
    0: top
    1: bottom
  ctl0_glutmask_b:
    0: exclude_memory_cells_in_readback
    1: include_memory_cells_in_readback
  ctl0_farsrc:
    0: efar
    1: far
  ctl0_sbits:
    0: read_write
    1: write_only
    2: none
  far_block_type:
    0: clb_io_clk
    1: block_ram
    2: cfg_clb