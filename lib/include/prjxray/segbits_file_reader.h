#ifndef PRJXRAY_LIB_SEGBITS_FILE_READER_H
#define PRJXRAY_LIB_SEGBITS_FILE_READER_H

#include <iterator>
#include <memory>

#include <absl/strings/string_view.h>
#include <prjxray/memory_mapped_file.h>

namespace prjxray {

class SegbitsFileReader {
 public:
	class value_type {
	 public:
		absl::string_view tag() const { return tag_; }
		absl::string_view bit() const { return bit_; }

	 private:
		friend SegbitsFileReader;

		value_type(const absl::string_view &view);

		absl::string_view tag_;
		absl::string_view bit_;
	};

	class iterator
		: public std::iterator<std::input_iterator_tag, value_type> {
	 public:
		iterator& operator++();

		bool operator==(iterator other) const {
			return view_ == other.view_; }
		bool operator!=(iterator other) const {
			return !(*this == other);}

		const value_type& operator*() const { return value_; }
		const value_type* operator->() const { return &value_; }

	 protected:
		explicit iterator(absl::string_view view)
			: view_(view), value_(view) {}

	 private:
		friend SegbitsFileReader;

		absl::string_view view_;
		value_type value_;
	};

	static std::unique_ptr<SegbitsFileReader> InitWithFile(
		const std::string &path);

	iterator begin();
	iterator end();

 private:
	SegbitsFileReader(std::unique_ptr<MemoryMappedFile> &&mapped_file)
		: mapped_file_(std::move(mapped_file)) {};

	std::unique_ptr<MemoryMappedFile> mapped_file_;
};

} // namespace prjxray

#endif  // PRJXRAY_LIB_SEGBITS_FILE_READER_H
