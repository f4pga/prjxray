#ifndef ECC_H_
#define ECC_H_

#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

class ECC {
       public:
	ECC(const std::string& architecture, size_t words_per_frame)
	    : architecture_(architecture),
	      frame_words_(words_per_frame),
	      ecc_word_(ecc_word_per_architecture.at(architecture)) {}

	void UpdateFrameECC(std::vector<uint32_t>& data) const;

       private:
	const std::string architecture_;
	const size_t frame_words_;
	const size_t ecc_word_;
	static const std::unordered_map<std::string, size_t>
	    ecc_word_per_architecture;

	uint64_t CalculateECC(const std::vector<uint32_t>& words) const;
	uint64_t GetUSEccFrameOffset(int word, int bit) const;
	uint32_t GetSeries7WordEcc(uint32_t idx,
	                           uint32_t data,
	                           uint32_t ecc) const;
	uint64_t GetUSWordEcc(uint32_t idx, uint32_t data, uint64_t ecc) const;
};

#endif  // ECC_H_
