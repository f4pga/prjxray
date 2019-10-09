#include <fstream>
#include <iostream>

#include <absl/strings/str_cat.h>
#include <absl/strings/str_split.h>
#include <absl/time/clock.h>
#include <absl/time/time.h>

#include <prjxray/xilinx/architectures.h>
#include <prjxray/xilinx/bitstream_writer.h>
#include <prjxray/xilinx/configuration.h>
#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/configuration_packet_with_payload.h>
#include <prjxray/xilinx/nop_packet.h>
#include <prjxray/xilinx/xc7series/command.h>
#include <prjxray/xilinx/xc7series/configuration_options_0_value.h>

namespace prjxray {
namespace xilinx {

template <>
Configuration<Series7>::PacketData
Configuration<Series7>::createType2ConfigurationPacketData(
    const Frames<Series7>::Frames2Data& frames,
    absl::optional<Series7::Part>& part) {
	PacketData packet_data;
	for (auto& frame : frames) {
		std::copy(frame.second.begin(), frame.second.end(),
		          std::back_inserter(packet_data));

		auto next_address = part->GetNextFrameAddress(frame.first);
		if (next_address &&
		    (next_address->block_type() != frame.first.block_type() ||
		     next_address->is_bottom_half_rows() !=
		         frame.first.is_bottom_half_rows() ||
		     next_address->row() != frame.first.row())) {
			packet_data.insert(packet_data.end(), 202, 0);
		}
	}
	packet_data.insert(packet_data.end(), 202, 0);
	return packet_data;
}

template <>
Configuration<UltraScale>::PacketData
Configuration<UltraScale>::createType2ConfigurationPacketData(
    const Frames<UltraScale>::Frames2Data& frames,
    absl::optional<UltraScale::Part>& part) {
	PacketData packet_data;
	for (auto& frame : frames) {
		std::copy(frame.second.begin(), frame.second.end(),
		          std::back_inserter(packet_data));

		auto next_address = part->GetNextFrameAddress(frame.first);
		if (next_address &&
		    (next_address->block_type() != frame.first.block_type() ||
		     next_address->is_bottom_half_rows() !=
		         frame.first.is_bottom_half_rows() ||
		     next_address->row() != frame.first.row())) {
			packet_data.insert(packet_data.end(),
			                   UltraScale::words_per_frame * 2, 0);
		}
	}
	packet_data.insert(packet_data.end(), UltraScale::words_per_frame * 2,
	                   0);
	return packet_data;
}

template <>
Configuration<UltraScalePlus>::PacketData
Configuration<UltraScalePlus>::createType2ConfigurationPacketData(
    const Frames<UltraScalePlus>::Frames2Data& frames,
    absl::optional<UltraScalePlus::Part>& part) {
	PacketData packet_data;
	for (auto& frame : frames) {
		std::copy(frame.second.begin(), frame.second.end(),
		          std::back_inserter(packet_data));

		auto next_address = part->GetNextFrameAddress(frame.first);
		if (next_address &&
		    (next_address->block_type() != frame.first.block_type() ||
		     next_address->is_bottom_half_rows() !=
		         frame.first.is_bottom_half_rows() ||
		     next_address->row() != frame.first.row())) {
			packet_data.insert(packet_data.end(),
			                   UltraScalePlus::words_per_frame * 2,
			                   0);
		}
	}
	packet_data.insert(packet_data.end(),
	                   UltraScalePlus::words_per_frame * 2, 0);
	return packet_data;
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
