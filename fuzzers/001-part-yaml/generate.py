#!/usr/bin/env python3
import os, sys, re
import yaml
#from ruamel.yaml.representer import RoundTripRepresenter

xilinx_part = "xilinx/xc7series/part"
xilinx_clock_region = "xilinx/xc7series/global_clock_region"
xilinx_rows = "xilinx/xc7series/row"
xilinx_config_column = "xilinx/xc7series/configuration_column"
xilinx_config_bus = "xilinx/xc7series/configuration_bus"

design_dir = "specimen_001"

### YAML CLASSES for tags
class XColumn(yaml.YAMLObject):
	yaml_tag = u'{}'.format(xilinx_config_column)
	def __init__(self, frame_count):
		self.frame_count = frame_count

class XRegion(yaml.YAMLObject):
	yaml_tag = u'{}'.format(xilinx_clock_region)
	def __init__(self, rows):
		self.rows = rows

class XRow(yaml.YAMLObject):
	yaml_tag = u'{}'.format(xilinx_rows)
	def __init__(self, bus):
		self.configuration_buses = bus

class XBus(yaml.YAMLObject):
	yaml_tag = u'{}'.format(xilinx_config_bus)
	def __init__(self, columns):
		self.configuration_columns = columns

class XPart(yaml.YAMLObject):
	yaml_tag = u'{}'.format(xilinx_part)
	def __init__(self, idcode, gcr):
		self.idcode = idcode
		self.global_clock_regions = gcr

class IdCode():
	def __init__(self, idcode):
		self.idcode = idcode

def get_config(config_file):
	file = open(config_file)

	config = list()

	num_rows = int(file.readline())

	bufg = file.readline()
	bufg_pos = int(int(re.match('.*?([0-9]+)$', bufg).group(1)) / 50)

	config = {
		'n_rows': num_rows,
		'bufg_pos': bufg_pos,
	}

	return config

def get_column_id(element):
	return int(re.search('X(\d+)', element).group(1))

def get_frame_count(element):
	is_clb = re.search(".*CLB.*", element)
	is_io = re.search(".*IOI.*", element)
	is_bram = re.search(".*BRAM.*", element)
	is_dsp = re.search(".*DSP.*", element)

	if is_clb:
		return 36
	elif is_io:
		return 42
	elif is_bram:
		return 28
	elif is_dsp:
		return 28
	else:
		return 30

def fill_unknown(columns, max_value):
	for i in range(max_value):
		if i not in columns:
			column_data = XColumn(30)
			columns[i] = column_data
	return columns

def count_elements(elements, name):
	count = 0
	for e in elements:
		match = re.search(".*{}.*".format(name), e)
		if match:
			count += 1
	return count

def create_bram_columns(bram_count):
	columns = dict()
	for i in range(bram_count):
		columns[i] = XColumn(128)

	return columns

def create_rows(bufg_pos, num_rows, top=True):
	row_id = 0
	rows = dict()
	clb_io_clk_columns = dict()
	bram_columns = dict()
	for i in range(bufg_pos, num_rows):
		if top:
			file = open("row_{}.cfg".format(i), "r")
		else:
			file = open("row_{}.cfg".format(bufg_pos - i), "r")
		elements = file.readline()
		split = elements.split()

		for e in split:
			column_id = get_column_id(e)
			frame_count = get_frame_count(e)
			#XXX
			column_data = XColumn(frame_count)

			clb_io_clk_columns[column_id] = column_data

		max_value = get_column_id(split[-1])
		clb_io_clk_columns = fill_unknown(clb_io_clk_columns, max_value)

		bram_count = count_elements(split, "BRAM")
		bram_columns = create_bram_columns(bram_count)

		rows[row_id] =  XRow({
					'CLB_IO_CLK': XBus(clb_io_clk_columns),
					'BLOCK_RAM': XBus(bram_columns)
				})

		row_id += 1

	return rows

def hexint_presenter(dumper, data):
	return dumper.represent_int(hex(data.idcode))

def main():
	config = get_config("device.cfg")
	bufg_pos = config['bufg_pos']
	num_rows = config['n_rows']

	idcode = IdCode(int(input()))

	regions = dict()

	top_rows = XRegion(create_rows(bufg_pos, num_rows))
	bottom_rows = XRegion(create_rows(bufg_pos, num_rows, False))

	regions = {
		'top': top_rows,
		'bottom': bottom_rows
	}

	data = XPart(idcode, regions)

	yaml.add_representer(IdCode, hexint_presenter)

	with open('part.yaml'.format(os.environ['XRAY_PART']), 'w') as outfile:
		yaml.dump(data, outfile, default_flow_style=False)

if __name__ == '__main__':
	main()
