/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/memory_mapped_file.h>

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

// https://stackoverflow.com/questions/35568112/use-of-undeclared-identifier-map-populate#answer-43505799
// man 2 mmap
#if __linux__
#include <linux/version.h>
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 22)
#define _MAP_POPULATE_AVAILABLE
#endif
#endif

#ifdef _MAP_POPULATE_AVAILABLE
#define MMAP_FLAGS (MAP_PRIVATE | MAP_POPULATE)
#else
#define MMAP_FLAGS MAP_PRIVATE
#endif

namespace prjxray {

std::unique_ptr<MemoryMappedFile> MemoryMappedFile::InitWithFile(
    const std::string& path) {
	int fd = open(path.c_str(), O_RDONLY, 0);
	if (fd == -1)
		return nullptr;

	struct stat statbuf;
	if (fstat(fd, &statbuf) < 0) {
		close(fd);
		return nullptr;
	}

	// mmap() will fail with EINVAL if length==0. If this file is
	// zero-length, return an object (to indicate the file exists) but
	// load it with a nullptr and zero length.
	if (statbuf.st_size == 0) {
		close(fd);
		return std::unique_ptr<MemoryMappedFile>(
		    new MemoryMappedFile(nullptr, 0));
	}

	void* file_map =
	    mmap(NULL, statbuf.st_size, PROT_READ, MMAP_FLAGS, fd, 0);

	// If mmap() succeeded, the fd is no longer needed as the mapping will
	// keep the file open.  If mmap() failed, the fd needs to be closed
	// anyway.
	close(fd);

	if (file_map == MAP_FAILED)
		return nullptr;

	return std::unique_ptr<MemoryMappedFile>(
	    new MemoryMappedFile(file_map, statbuf.st_size));
}

MemoryMappedFile::~MemoryMappedFile() {
	munmap(data_, size_);
}

}  // namespace prjxray
