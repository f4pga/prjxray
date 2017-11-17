#include <prjxray/memory_mapped_file.h>

#include <gtest/gtest.h>

TEST(MemoryMappedFileTest, NonExistantFile) {
	EXPECT_FALSE(prjxray::MemoryMappedFile::InitWithFile("does_not_exist"));
}

TEST(MemoryMappedFileTest, ExistingFile) {
	auto file = prjxray::MemoryMappedFile::InitWithFile("small_file");
	ASSERT_TRUE(file);
	EXPECT_EQ(static_cast<size_t>(4), file->size());
	EXPECT_EQ(0, memcmp("foo\n", file->data(), 4));
}
