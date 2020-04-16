/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_OPTIONS_0_VALUE_H
#define PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_OPTIONS_0_VALUE_H

#include <prjxray/bit_ops.h>
#include <prjxray/xilinx/configuration_packet.h>
#include <prjxray/xilinx/configuration_register.h>

namespace prjxray {
namespace xilinx {
namespace xc7series {

class ConfigurationOptions0Value {
       public:
	enum class StartupClockSource : uint32_t {
		CCLK = 0x0,
		User = 0x1,
		JTAG = 0x2,
	};

	enum class SignalReleaseCycle : uint32_t {
		Phase1 = 0x0,
		Phase2 = 0x1,
		Phase3 = 0x2,
		Phase4 = 0x3,
		Phase5 = 0x4,
		Phase6 = 0x5,
		TrackDone = 0x6,
		Keep = 0x7,
	};

	enum class StallCycle : uint32_t {
		Phase0 = 0x0,
		Phase1 = 0x1,
		Phase2 = 0x2,
		Phase3 = 0x3,
		Phase4 = 0x4,
		Phase5 = 0x5,
		Phase6 = 0x6,
		NoWait = 0x7,
	};

	ConfigurationOptions0Value() : value_(0) {}

	operator uint32_t() const { return value_; }

	ConfigurationOptions0Value& SetUseDonePinAsPowerdownStatus(
	    bool enabled) {
		value_ = bit_field_set(value_, 27, 27, enabled ? 1 : 0);
		return *this;
	}

	ConfigurationOptions0Value& SetAddPipelineStageForDoneIn(bool enabled) {
		value_ = bit_field_set(value_, 25, 25, enabled ? 1 : 0);
		return *this;
	}

	ConfigurationOptions0Value& SetDriveDoneHigh(bool enabled) {
		value_ = bit_field_set(value_, 24, 24, enabled);
		return *this;
	}

	ConfigurationOptions0Value& SetReadbackIsSingleShot(bool enabled) {
		value_ = bit_field_set(value_, 23, 23, enabled);
		return *this;
	}

	ConfigurationOptions0Value& SetCclkFrequency(uint32_t mhz) {
		value_ = bit_field_set(value_, 22, 17, mhz);
		return *this;
	}

	ConfigurationOptions0Value& SetStartupClockSource(
	    StartupClockSource source) {
		value_ = bit_field_set(value_, 16, 15,
		                       static_cast<uint32_t>(source));
		return *this;
	}

	ConfigurationOptions0Value& SetReleaseDonePinAtStartupCycle(
	    SignalReleaseCycle cycle) {
		value_ =
		    bit_field_set(value_, 14, 12, static_cast<uint32_t>(cycle));
		return *this;
	}

	ConfigurationOptions0Value& SetStallAtStartupCycleUntilDciMatch(
	    StallCycle cycle) {
		value_ =
		    bit_field_set(value_, 11, 9, static_cast<uint32_t>(cycle));
		return *this;
	};

	ConfigurationOptions0Value& SetStallAtStartupCycleUntilMmcmLock(
	    StallCycle cycle) {
		value_ =
		    bit_field_set(value_, 8, 6, static_cast<uint32_t>(cycle));
		return *this;
	};

	ConfigurationOptions0Value& SetReleaseGtsSignalAtStartupCycle(
	    SignalReleaseCycle cycle) {
		value_ =
		    bit_field_set(value_, 5, 3, static_cast<uint32_t>(cycle));
		return *this;
	}

	ConfigurationOptions0Value& SetReleaseGweSignalAtStartupCycle(
	    SignalReleaseCycle cycle) {
		value_ =
		    bit_field_set(value_, 2, 0, static_cast<uint32_t>(cycle));
		return *this;
	}

       private:
	uint32_t value_;
};  // namespace xc7series

}  // namespace xc7series
}  // namespace xilinx
}  // namespace prjxray

#endif  // PRJXRAY_LIB_XILINX_XC7SERIES_CONFIGURATION_OPTIONS_0_VALUE_H
