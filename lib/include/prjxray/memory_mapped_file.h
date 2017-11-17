#ifndef PRJXRAY_LIB_MEMORY_MAPPED_FILE
#define PRJXRAY_LIB_MEMORY_MAPPED_FILE

#include <memory>
#include <string>

namespace prjxray {

class MemoryMappedFile {
 public:
	~MemoryMappedFile();

	static std::unique_ptr<MemoryMappedFile> InitWithFile(
			const std::string &path);

	const void* data() { return data_; }
	const size_t size() { return size_; }

 private:
	MemoryMappedFile(void *data, size_t size)
		: data_(data), size_(size) {};

	void *data_;
	size_t size_;
};

} // namespace prjxray

#endif  // PRJXRAY_LIB_MEMORY_MAPPED_FILE
