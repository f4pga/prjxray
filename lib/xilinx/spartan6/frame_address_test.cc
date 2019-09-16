#include <prjxray/xilinx/spartan6/frame_address.h>

#include <gtest/gtest.h>

namespace spartan6 = prjxray::xilinx::spartan6;

TEST(FrameAddressTest, YamlEncode) {
	spartan6::FrameAddress address(spartan6::BlockType::BLOCK_RAM, 10, 0,
	                               5);

	YAML::Node node(address);

	EXPECT_EQ(node.Tag(), "xilinx/spartan6/frame_address");
	EXPECT_EQ(node["block_type"].as<std::string>(), "BLOCK_RAM");
	EXPECT_EQ(node["row"].as<std::string>(), "10");
	EXPECT_EQ(node["column"].as<std::string>(), "0");
	EXPECT_EQ(node["minor"].as<std::string>(), "5");
}

TEST(FrameAddressTest, YamlDecode) {
	YAML::Node node;
	node.SetTag("xilinx/spartan6/frame_address");
	node["block_type"] = "BLOCK_RAM";
	node["row"] = "0";
	node["column"] = "5";
	node["minor"] = "11";

	spartan6::FrameAddress address = node.as<spartan6::FrameAddress>();
	EXPECT_EQ(address.block_type(), spartan6::BlockType::BLOCK_RAM);
	EXPECT_EQ(address.row(), 0);
	EXPECT_EQ(address.column(), 5);
	EXPECT_EQ(address.minor(), 11);
}
