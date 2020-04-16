/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <fstream>
#include <iostream>

#include <absl/strings/str_cat.h>
#include <absl/strings/str_split.h>
#include <absl/time/clock.h>
#include <absl/time/time.h>

#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_writer.h>
#include <prjxray/xilinx/configuration.h>
#include <prjxray/xilinx/configuration_packet_with_payload.h>
#include <prjxray/xilinx/nop_packet.h>
#include <prjxray/xilinx/spartan6/command.h>
#include <prjxray/xilinx/xc7series/command.h>
#include <prjxray/xilinx/xc7series/configuration_options_0_value.h>

namespace prjxray {
namespace xilinx {

template <>
Configuration<Spartan6>::PacketData
Configuration<Spartan6>::createType2ConfigurationPacketData(
    const Frames<Spartan6>::Frames2Data& frames,
    absl::optional<Spartan6::Part>& part) {
	// Generate a single type 2 packet that writes everything at once.
	PacketData packet_data;
	for (auto& frame : frames) {
		std::copy(frame.second.begin(), frame.second.end(),
		          std::back_inserter(packet_data));
	}

	// Insert payload length
	size_t packet_data_size = packet_data.size() - 2;
	packet_data.insert(packet_data.begin(), packet_data_size & 0xFFFF);
	packet_data.insert(packet_data.begin(),
	                   (packet_data_size >> 16) & 0xFFFF);
	return packet_data;
}

template <>
void Configuration<Spartan6>::createConfigurationPackage(
    Spartan6::ConfigurationPackage& out_packets,
    const PacketData& packet_data,
    absl::optional<Spartan6::Part>& part) {
	using ArchType = Spartan6;
	using ConfigurationRegister = ArchType::ConfRegType;
	// Initialization sequence
	//
	// Reset CRC
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::RCRC)}));

	// NOP
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());

	// Frame length
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FLR, {0x0380}));

	// Configuration Options 1
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR1, {0x3d08}));

	// Configurations Options2
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR2, {0x9ee}));

	// IDCODE
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<2, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::IDCODE,
	        {part->idcode() >> 16, part->idcode()}));

	// Control MASK
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0xcf}));

	// Control options
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL, {0x81}));

	// NOP packets
	for (int i = 0; i < 17; i++) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}

	// CCLK FREQ
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CCLK_FREQ, {0x3cc8}));

	// PWRDN_REG
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::PWRDN_REG, {0x881}));

	// EYE MASK
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::EYE_MASK, {0x0}));

	// House Clean Option
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::HC_OPT_REG, {0x1f}));

	// Configuration Watchdog Timer
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CWDT, {0xffff}));

	// GWE cycle during wake-up from suspend
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::PU_GWE, {0x5}));

	// GTS cycle during wake-up from suspend
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::PU_GTS, {0x4}));

	// Reboot mode
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MODE_REG, {0x100}));

	// General options 1
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::GENERAL1, {0x0}));

	// General options 2
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::GENERAL2, {0x0}));

	// General options 3
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::GENERAL3, {0x0}));

	// General options 4
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::GENERAL4, {0x0}));

	// General options 5
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::GENERAL5, {0x0}));

	// SEU frequency, enable and status
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::SEU_OPT, {0x1be2}));

	// Expected readback signature for SEU detection
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<2, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::EXP_SIGN, {0x0, 0x0}));

	// NOP
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());

	// FAR
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<2, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR_MAJ, {0x0, 0x0}));

	// Write Configuration Data
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::WCFG)}));

	// Frame data write
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE2, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, {packet_data}));

	// NOP packets
	for (int i = 0; i < 24; i++) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}

	// Finalization sequence
	//
	// Set/reset the IOB and CLB flip-flops
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::GRESTORE)}));

	// Last Frame
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::LFRM)}));

	// NOP packets
	for (int i = 0; i < 4; i++) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}

	// Set/reset the IOB and CLB flip-flops
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::GRESTORE)}));

	// Startup sequence
	//
	// Start
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::START)}));

	// Control MASK
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0xff}));

	// Control options
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL, {0x81}));

	// CRC
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<2, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CRC, {0x39, 0xe423}));

	// Desync
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(spartan6::Command::DESYNC)}));

	// NOP packets
	for (int i = 0; i < 14; i++) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
}

template <>
void Configuration<Series7>::createConfigurationPackage(
    Series7::ConfigurationPackage& out_packets,
    const PacketData& packet_data,
    absl::optional<Series7::Part>& part) {
	using ArchType = Series7;
	using ConfigurationRegister = ArchType::ConfRegType;
	// Initialization sequence
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::TIMER, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::WBSTAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::NOP)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::UNKNOWN, {0x0}));

	// Configuration Options 0
	out_packets.emplace_back(new ConfigurationPacketWithPayload<
	                         1, ConfigurationRegister>(
	    ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::COR0,
	    {xc7series::ConfigurationOptions0Value()
	         .SetAddPipelineStageForDoneIn(true)
	         .SetReleaseDonePinAtStartupCycle(
	             xc7series::ConfigurationOptions0Value::SignalReleaseCycle::
	                 Phase4)
	         .SetStallAtStartupCycleUntilDciMatch(
	             xc7series::ConfigurationOptions0Value::StallCycle::NoWait)
	         .SetStallAtStartupCycleUntilMmcmLock(
	             xc7series::ConfigurationOptions0Value::StallCycle::NoWait)
	         .SetReleaseGtsSignalAtStartupCycle(
	             xc7series::ConfigurationOptions0Value::SignalReleaseCycle::
	                 Phase5)
	         .SetReleaseGweSignalAtStartupCycle(
	             xc7series::ConfigurationOptions0Value::SignalReleaseCycle::
	                 Phase6)}));

	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR1, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::IDCODE, {part->idcode()}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::SWITCH)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x401}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL0, {0x501}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL1, {0x0}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::WCFG)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());

	// Frame data write
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE1, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, {}));
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE2, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, packet_data));

	// Finalization sequence
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::GRESTORE)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::LFRM)}));
	for (int ii = 0; ii < 100; ++ii) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::START)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x3be0000}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x501}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL0, {0x501}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::DESYNC)}));
	for (int ii = 0; ii < 400; ++ii) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
}

template <>
void Configuration<UltraScale>::createConfigurationPackage(
    UltraScale::ConfigurationPackage& out_packets,
    const PacketData& packet_data,
    absl::optional<UltraScale::Part>& part) {
	using ArchType = UltraScale;
	using ConfigurationRegister = ArchType::ConfRegType;
	// Initialization sequence
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::TIMER, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::WBSTAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::NOP)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::UNKNOWN, {0x0}));

	// Configuration Options 0
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR0, {0x38003fe5}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR1, {0x400000}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::IDCODE, {part->idcode()}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::SWITCH)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x1}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL0, {0x101}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL1, {0x0}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::WCFG)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());

	// Frame data write
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE1, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, {}));
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE2, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, packet_data));

	// Finalization sequence
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::GRESTORE)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::LFRM)}));
	for (int ii = 0; ii < 100; ++ii) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::START)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x3be0000}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x101}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL0, {0x101}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::DESYNC)}));
	for (int ii = 0; ii < 400; ++ii) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
}

template <>
void Configuration<UltraScalePlus>::createConfigurationPackage(
    UltraScalePlus::ConfigurationPackage& out_packets,
    const PacketData& packet_data,
    absl::optional<UltraScalePlus::Part>& part) {
	using ArchType = UltraScalePlus;
	using ConfigurationRegister = ArchType::ConfRegType;
	// Initialization sequence
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::TIMER, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::WBSTAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::NOP)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::UNKNOWN, {0x0}));

	// Configuration Options 0
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR0, {0x38003fe5}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::COR1, {0x400000}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::IDCODE, {part->idcode()}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::SWITCH)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x1}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL0, {0x101}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL1, {0x0}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x0}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::WCFG)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());

	// Frame data write
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE1, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, {}));
	out_packets.emplace_back(new ConfigurationPacket<ConfigurationRegister>(
	    TYPE2, ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	    ConfigurationRegister::FDRI, packet_data));

	// Finalization sequence
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::GRESTORE)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::LFRM)}));
	for (int ii = 0; ii < 100; ++ii) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::START)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::FAR, {0x3be0000}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::MASK, {0x101}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CTL0, {0x101}));
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::RCRC)}));
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(new NopPacket<ConfigurationRegister>());
	out_packets.emplace_back(
	    new ConfigurationPacketWithPayload<1, ConfigurationRegister>(
	        ConfigurationPacket<ConfigurationRegister>::Opcode::Write,
	        ConfigurationRegister::CMD,
	        {static_cast<uint32_t>(xc7series::Command::DESYNC)}));
	for (int ii = 0; ii < 400; ++ii) {
		out_packets.emplace_back(
		    new NopPacket<ConfigurationRegister>());
	}
}
}  // namespace xilinx
}  // namespace prjxray
