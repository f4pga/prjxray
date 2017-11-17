#include <prjxray/memory_mapped_file.h>

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

namespace prjxray {

std::unique_ptr<MemoryMappedFile> MemoryMappedFile::InitWithFile(
	const std::string &path) {

	int fd = open(path.c_str(), O_RDONLY, 0);
	if (fd == -1) return nullptr;

	struct stat statbuf;
	if (fstat(fd, &statbuf) < 0) {
		close(fd);
	}

	void *file_map = mmap(NULL, statbuf.st_size, PROT_READ,
			      MAP_PRIVATE | MAP_POPULATE, fd, 0);

	// If mmap() succeeded, the fd is no longer needed as the mapping will
	// keep the file open.  If mmap() failed, the fd needs to be closed
	// anyway.
	close(fd);

	if (file_map == MAP_FAILED) return nullptr;

	return std::unique_ptr<MemoryMappedFile>(
		new MemoryMappedFile(file_map, statbuf.st_size));
}

MemoryMappedFile::~MemoryMappedFile() {
	munmap(data_, size_);
}

}  // namepsace prjxray
