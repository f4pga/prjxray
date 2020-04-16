/*
 *
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/segbits_file_reader.h>

#include <map>
#include <string>

#include <gtest/gtest.h>

TEST(SegbitsFileReaderTest, NonExistantFileReturnsNull) {
	EXPECT_FALSE(
	    prjxray::SegbitsFileReader::InitWithFile("does_not_exist"));
}

TEST(SegbitsFileReaderTest, ZeroLengthFileYieldsNoItems) {
	auto segbits_reader =
	    prjxray::SegbitsFileReader::InitWithFile("empty_file");
	ASSERT_TRUE(segbits_reader);

	EXPECT_EQ(segbits_reader->begin(), segbits_reader->end());
}

TEST(SegbitsFileReaderTest, FileWithOneEntry) {
	auto segbits_reader =
	    prjxray::SegbitsFileReader::InitWithFile("one_entry.segbits");
	ASSERT_TRUE(segbits_reader);

	auto begin_iter = segbits_reader->begin();
	EXPECT_EQ(begin_iter->tag(), "CLBLL_L.SLICEL_X0.A5FF.ZINI");
	EXPECT_EQ(begin_iter->bit(), "31_06");

	EXPECT_EQ(++begin_iter, segbits_reader->end());
}

TEST(SegbitsFileReaderTest, FileWithOneEntryWithEmptyTag) {
	auto segbits_reader = prjxray::SegbitsFileReader::InitWithFile(
	    "one_entry_empty_tag.segbits");
	ASSERT_TRUE(segbits_reader);

	auto begin_iter = segbits_reader->begin();
	EXPECT_EQ(begin_iter->tag(), "");
	EXPECT_EQ(begin_iter->bit(), "31_06");

	EXPECT_EQ(++begin_iter, segbits_reader->end());
}

TEST(SegbitsFileReaderTest, FileWithOneEntryMissingBit) {
	auto segbits_reader = prjxray::SegbitsFileReader::InitWithFile(
	    "one_entry_missing_bit.segbits");
	ASSERT_TRUE(segbits_reader);

	auto begin_iter = segbits_reader->begin();
	EXPECT_EQ(begin_iter->tag(), "CLBLL_L.SLICEL_X0.A5FF.ZINI");
	EXPECT_EQ(begin_iter->bit(), "");

	EXPECT_EQ(++begin_iter, segbits_reader->end());
}

TEST(SegbitsFileReaderTest, FileWithOneEntryWithExtraWhitespace) {
	auto segbits_reader = prjxray::SegbitsFileReader::InitWithFile(
	    "one_entry_extra_whitespace.segbits");
	ASSERT_TRUE(segbits_reader);

	auto begin_iter = segbits_reader->begin();
	EXPECT_EQ(begin_iter->tag(), "CLBLL_L.SLICEL_X0.A5FF.ZINI");
	EXPECT_EQ(begin_iter->bit(), "31_06");

	EXPECT_EQ(++begin_iter, segbits_reader->end());
}

TEST(SegbitsFileReaderTest, FileWithTwoEntries) {
	auto segbits_reader =
	    prjxray::SegbitsFileReader::InitWithFile("two_entries.segbits");
	ASSERT_TRUE(segbits_reader);

	auto iter = segbits_reader->begin();
	EXPECT_EQ(iter->tag(), "CLBLL_L.SLICEL_X0.A5FF.ZINI");
	EXPECT_EQ(iter->bit(), "31_06");

	++iter;
	EXPECT_EQ(iter->tag(), "CLBLL_L.SLICEL_X0.AFF.ZINI");
	EXPECT_EQ(iter->bit(), "31_03");

	EXPECT_EQ(++iter, segbits_reader->end());
}
