#ifndef PRJXRAY_LIB_BIT_OPS_H
#define PRJXRAY_LIB_BIT_OPS_H

namespace prjxray {

template<typename UInt>
constexpr UInt bit_mask(const int bit) {
	return (static_cast<UInt>(1) << bit);
}

template<typename UInt>
constexpr UInt bit_sizeof() {
	return sizeof(UInt) * 8;
}

template<typename UInt>
constexpr UInt bit_all_ones() {
	return ~static_cast<UInt>(0);
}

template<typename UInt>
constexpr UInt bit_mask_range(const int top_bit, const int bottom_bit) {
	return ((bit_all_ones<UInt>() >> (bit_sizeof<UInt>() - 1 - top_bit)) &
		(bit_all_ones<UInt>() - bit_mask<UInt>(bottom_bit) +
		 static_cast<UInt>(1)));
}


template<typename UInt>
constexpr UInt bit_field_get(UInt value, const int top_bit, const int bottom_bit) {
	return (value & bit_mask_range<UInt>(top_bit, bottom_bit)) >> bottom_bit;
}

template<typename UInt>
constexpr UInt bit_field_set(const UInt reg_value,
			     const int top_bit, const int bottom_bit,
			     const UInt field_value) {
	return ((reg_value & ~bit_mask_range<UInt>(top_bit, bottom_bit)) |
		((static_cast<UInt>(field_value) << bottom_bit) &
		 bit_mask_range<UInt>(top_bit, bottom_bit)));
}

}  // namespace prjxray

#endif  // PRJXRAY_LIB_BIT_OPS_H
