#ifndef PRJXRAY_LIB_BIT_OPS_H
#define PRJXRAY_LIB_BIT_OPS_H

namespace prjxray {

template<typename UInt>
constexpr UInt bit_mask(int bit) {
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
constexpr UInt bit_mask_range(int top_bit, int bottom_bit) {
	return ((bit_all_ones<UInt>() >> (bit_sizeof<UInt>() - 1 - top_bit)) &
		(bit_all_ones<UInt>() - bit_mask<UInt>(bottom_bit) +
		 static_cast<UInt>(1)));
}


template<typename UInt>
constexpr UInt bit_field_get(UInt value, int top_bit, int bottom_bit) {
	return (value & bit_mask_range<UInt>(top_bit, bottom_bit)) >> bottom_bit;
}

}  // namespace prjxray

#endif  // PRJXRAY_LIB_BIT_OPS_H
