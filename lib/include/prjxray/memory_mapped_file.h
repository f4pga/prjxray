#ifndef PRJXRAY_LIB_MEMORY_MAPPED_FILE
#define PRJXRAY_LIB_MEMORY_MAPPED_FILE

#include <memory>
#include <string>

#include <absl/types/span.h>

namespace prjxray {

class MemoryMappedFile {
 public:
	~MemoryMappedFile();

	static std::unique_ptr<MemoryMappedFile> InitWithFile(
			const std::string &path);

	void* const data() const { return data_; }
	const size_t size() const { return size_; }

	absl::Span<uint8_t> as_bytes() const {
		return {static_cast<uint8_t*>(data_), size_};
	}

 private:
	MemoryMappedFile(void *data, size_t size)
		: data_(data), size_(size) {};

	void *data_;
	size_t size_;
};

} // namespace prjxray

#endif  // PRJXRAY_LIB_MEMORY_MAPPED_FILE
