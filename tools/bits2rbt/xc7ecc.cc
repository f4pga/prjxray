#include "ecc.h"
#include <cassert>
#include <iostream>

const std::unordered_map<std::string, size_t> ECC::ecc_word_per_architecture = {
    {"Series7", 50},
    {"UltraScale", 60},
    {"UltraScalePlus", 45}};

uint32_t ECC::GetSeries7WordEcc(uint32_t idx,
                                uint32_t data,
                                uint32_t ecc) const {
	uint32_t val = idx * 32;  // bit offset

	if (idx > 0x25)  // avoid 0x800
		val += 0x1360;
	else if (idx > 0x6)  // avoid 0x400
		val += 0x1340;
	else  // avoid lower
		val += 0x1320;

	if (idx == 0x32)  // mask ECC
		data &= 0xFFFFE000;

	for (int i = 0; i < 32; i++) {
		if (data & 1)
			ecc ^= val + i;

		data >>= 1;
	}

	if (idx == 0x64) {  // last index
		uint32_t v = ecc & 0xFFF;
		v ^= v >> 8;
		v ^= v >> 4;
		v ^= v >> 2;
		v ^= v >> 1;
		ecc ^= (v & 1) << 12;  // parity
	}

	return ecc;
}

uint64_t ECC::GetUSEccFrameOffset(int word, int bit) const {
	int nib = bit / 4;
	int nibbit = bit % 4;
	// ECC offset is expanded to 1 bit per nibble,
	// and then shifted based on the bit index in nibble
	// e.g. word 3, bit 9
	// offset: 0b10100110010 - concatenate (3 + (255 - last_frame_index(e.g.
	// 92 for US+)) [frame offset] and 9/4 [nibble offset] becomes:
	// 0x10100110010 shifted by bit in nibble (9%4): 0x20200220020
	uint32_t offset = (word + (255 - (frame_words_ - 1))) << 3 | nib;
	uint64_t exp_offset = 0;
	// Odd parity
	offset ^= (1 << 11);
	for (int i = 0; i < 11; i++)
		if (offset & (1 << i))
			offset ^= (1 << 11);
	// Expansion
	for (int i = 0; i < 12; i++)
		if (offset & (1 << i))
			exp_offset |= (1ULL << (4 * i));
	return exp_offset << nibbit;
};

uint64_t ECC::GetUSWordEcc(uint32_t idx, uint32_t data, uint64_t ecc) const {
	if (idx == ecc_word_) {
		data = 0x0;
	}
	if (idx == ecc_word_ + 1) {
		data &= 0xffff0000;
	}
	for (int i = 0; i < 32; i++) {
		if (data & 1) {
			ecc ^= GetUSEccFrameOffset(idx, i);
		}
		data >>= 1;
	}
	return ecc;
}

uint64_t ECC::CalculateECC(const std::vector<uint32_t>& data) const {
	uint64_t ecc = 0;
	for (size_t w = 0; w < data.size(); ++w) {
		const uint32_t& word = data.at(w);
		if (architecture_ == "Series7") {
			ecc = GetSeries7WordEcc(w, word, ecc);
		} else {
			ecc = GetUSWordEcc(w, word, ecc);
		}
	}
	return ecc;
}

void ECC::UpdateFrameECC(std::vector<uint32_t>& data) const {
	assert(data.size() >= ecc_word_);
	uint64_t ecc(CalculateECC(data));
	if (architecture_ == "Series7") {
		data[ecc_word_] &= 0xffffe000;
		data[ecc_word_] |= ecc & 0x1fff;
	} else {
		data[ecc_word_] = ecc;
		data[ecc_word_ + 1] &= 0xffff0000;
		data[ecc_word_ + 1] |= (ecc >> 32) & 0xffff;
	}
}
