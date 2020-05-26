/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/segbits_file_reader.h>

namespace prjxray {

std::unique_ptr<SegbitsFileReader> SegbitsFileReader::InitWithFile(
    const std::string& path) {
	auto mapped_file = MemoryMappedFile::InitWithFile(path);
	if (!mapped_file)
		return nullptr;

	return std::unique_ptr<SegbitsFileReader>(
	    new SegbitsFileReader(std::move(mapped_file)));
}

SegbitsFileReader::iterator SegbitsFileReader::begin() {
	return iterator(
	    absl::string_view(static_cast<const char*>(mapped_file_->data()),
	                      mapped_file_->size()));
}

SegbitsFileReader::iterator SegbitsFileReader::end() {
	return iterator(absl::string_view());
}

SegbitsFileReader::value_type::value_type(const absl::string_view& view) {
	size_t separator_start = view.find_first_of(" \t\n");
	if (separator_start == absl::string_view::npos) {
		tag_ = view;
		bit_ = absl::string_view();
		return;
	}

	size_t bit_start = view.find_first_not_of(" \t", separator_start);
	size_t newline = view.find('\n', bit_start);
	if (newline == absl::string_view::npos) {
		tag_ = view.substr(0, separator_start);
		bit_ = view.substr(bit_start);
		return;
	}

	size_t bit_len = newline - bit_start;
	tag_ = view.substr(0, separator_start);
	bit_ = view.substr(bit_start, bit_len);
	return;
}

SegbitsFileReader::iterator& SegbitsFileReader::iterator::operator++() {
	size_t newline = view_.find('\n');
	if (newline == absl::string_view::npos) {
		view_ = absl::string_view();
	}

	view_.remove_prefix(newline + 1);
	value_ = value_type(view_);
	return *this;
}

}  // namespace prjxray
