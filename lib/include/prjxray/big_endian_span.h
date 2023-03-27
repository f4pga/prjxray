/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_BIG_ENDIAN_SPAN
#define PRJXRAY_LIB_BIG_ENDIAN_SPAN

#include <cassert>
#include <iterator>

#include <absl/types/span.h>

namespace prjxray {

template <typename WordType, typename ByteType>
class BigEndianSpan {
       public:
	constexpr static size_t kBytesPerElement = sizeof(WordType);

	using byte_type = ByteType;
	using word_type = WordType;
	using size_type = std::size_t;

	class value_type {
	       public:
		operator WordType() const {
			WordType word = 0;
			for (size_t ii = 0; ii < kBytesPerElement; ++ii) {
				word |= (static_cast<WordType>(bytes_[ii])
				         << ((kBytesPerElement - 1 - ii) * 8));
			}
			return word;
		}

		value_type& operator=(WordType word) {
			for (size_t ii = 0; ii < kBytesPerElement; ++ii) {
				bytes_[ii] =
				    ((word >>
				      ((kBytesPerElement - 1 - ii) * 8)) &
				     0xFF);
			}
			return *this;
		}

	       protected:
		friend class BigEndianSpan<WordType, ByteType>;

		value_type(absl::Span<ByteType> bytes) : bytes_(bytes){};

	       private:
		absl::Span<ByteType> bytes_;
	};

	class iterator {
	       public:
	       
	        using iterator_category = std::input_iterator_tag;
        	using value_type = BigEndianSpan::value_type;
        	using difference_type = std::ptrdiff_t;
        	using pointer = value_type*;
        	using reference = value_type&;
        	
		value_type operator*() const { return value_type(bytes_); }

		bool operator==(const iterator& other) const {
			return bytes_ == other.bytes_;
		}

		bool operator!=(const iterator& other) const {
			return bytes_ != other.bytes_;
		}

		iterator& operator++() {
			bytes_ = bytes_.subspan(kBytesPerElement);
			return *this;
		}

	       protected:
		friend class BigEndianSpan<WordType, ByteType>;

		iterator(absl::Span<ByteType> bytes) : bytes_(bytes){};

	       private:
		absl::Span<ByteType> bytes_;
	};

	using pointer = value_type*;
	using reference = value_type&;

	BigEndianSpan(absl::Span<ByteType> bytes) : bytes_(bytes){};

	constexpr size_type size() const noexcept {
		return bytes_.size() / kBytesPerElement;
	};

	constexpr size_type length() const noexcept { return size(); }

	constexpr bool empty() const noexcept { return size() == 0; }

	value_type operator[](size_type pos) const {
		assert(pos >= 0 && pos < size());
		return value_type(bytes_.subspan((pos * kBytesPerElement)));
	}

	constexpr reference at(size_type pos) const {
		return this->operator[](pos);
	}

	iterator begin() const { return iterator(bytes_); }
	iterator end() const { return iterator({}); }

       private:
	absl::Span<ByteType> bytes_;
};

template <typename WordType, typename Container>
BigEndianSpan<WordType, typename Container::value_type> make_big_endian_span(
    Container& bytes) {
	return BigEndianSpan<WordType, typename Container::value_type>(
	    absl::Span<typename Container::value_type>(bytes));
}

}  // namespace prjxray

#endif  // PRJXRAY_LIB_BIG_ENDIAN_SPAN
