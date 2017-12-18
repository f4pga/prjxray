#include <prjxray/xilinx/xc7series/configuration_frame_address.h>

#include <gtest/gtest.h>

namespace xc7series = prjxray::xilinx::xc7series;

TEST(ConfigurationFrameAddressTest, YamlEncode) {
	xc7series::ConfigurationFrameAddress address(
		xc7series::BlockType::BLOCK_RAM,
		false, 10, 0, 5);

	YAML::Node node(address);

	EXPECT_EQ(node.Tag(), "xilinx/xc7series/configuration_frame_address");
	EXPECT_EQ(node["block_type"].as<std::string>(), "BLOCK_RAM");
	EXPECT_EQ(node["row_half"].as<std::string>(), "top");
	EXPECT_EQ(node["row"].as<std::string>(), "10");
	EXPECT_EQ(node["column"].as<std::string>(), "0");
	EXPECT_EQ(node["minor"].as<std::string>(), "5");
}

TEST(ConfigurationFrameAddressTest, YamlDecode) {
	YAML::Node node;
	node.SetTag("xilinx/xc7series/configuration_frame_address");
	node["block_type"] = "BLOCK_RAM";
	node["row_half"] = "bottom";
	node["row"] = "0";
	node["column"] = "5";
	node["minor"] = "11";

	xc7series::ConfigurationFrameAddress address =
			node.as<xc7series::ConfigurationFrameAddress>();
	EXPECT_EQ(address.block_type(), xc7series::BlockType::BLOCK_RAM);
	EXPECT_TRUE(address.is_bottom_half_rows());
	EXPECT_EQ(address.row_address(), 0);
	EXPECT_EQ(address.column_address(), 5);
	EXPECT_EQ(address.minor_address(), 11);
}
