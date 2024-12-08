# Makefile for DSP IO registers minitests

# Define the top-level design file
TOP = top.v

# Define the build directory
BUILD_DIR = build

# Define the output bitstream file
BITSTREAM = $(BUILD_DIR)/design.bit

# Define the Vivado project name
PROJECT = design

# Define the part number
PART = xc7a35tcsg324-1

# Define the Xilinx Vivado toolchain path
VIVADO = vivado

# Define the synthesis and implementation scripts
SYNTH_SCRIPT = synth.tcl
IMPL_SCRIPT = impl.tcl

# Define the default target
all: $(BITSTREAM)

# Create the build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Synthesize the design
$(BUILD_DIR)/$(PROJECT).dcp: $(TOP) | $(BUILD_DIR)
	$(VIVADO) -mode batch -source $(SYNTH_SCRIPT) -tclargs $(TOP) $(BUILD_DIR) $(PROJECT) $(PART)

# Implement the design
$(BITSTREAM): $(BUILD_DIR)/$(PROJECT).dcp
	$(VIVADO) -mode batch -source $(IMPL_SCRIPT) -tclargs $(BUILD_DIR) $(PROJECT)

# Clean the build directory
clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean
