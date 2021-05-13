uint32_t icap_crc(uint32_t addr, uint32_t data, uint32_t prev) {
	int kAddressBitWidth = 5;
	constexpr int kDataBitWidth = 32;
	constexpr uint32_t kCrc32CastagnoliPolynomial = 0x82F63B78;

	uint64_t poly = static_cast<uint64_t>(kCrc32CastagnoliPolynomial) << 1;
	uint64_t val = (static_cast<uint64_t>(addr) << 32) | data;
	uint64_t crc = prev;

	for (int i = 0; i < kAddressBitWidth + kDataBitWidth; i++) {
		if ((val & 1) != (crc & 1))
			crc ^= poly;

		val >>= 1;
		crc >>= 1;
	}
	return crc;
}
