#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <vector>
#include <string>
#include <map>
#include <set>

bool mode_c = false;
bool mode_r = false;
bool mode_m = false;
bool mode_x = false;
bool mode_y = false;
bool mode_z = false;
bool mode_p = false;
bool chksum = false;
char *outfile = nullptr;
std::set<uint32_t> frames;

uint32_t frame_range_begin = 0, frame_range_end = 0;

std::vector<uint8_t> bitdata;
int cursor;

std::string header_a, header_b, header_c, header_d;
std::vector<uint32_t> configdata;

uint32_t frameptr = 0;
std::map<uint32_t, std::vector<uint32_t>> configframes;
std::set<uint32_t> configframes_autoincr;

std::vector<uint32_t> zero_frame(101);

uint32_t selbits(uint32_t value, int msb, int lsb)
{
	return (value >> lsb) & ((1 << (msb-lsb+1)) - 1);
}

void print_hexblock(int len)
{
	if (!mode_r) {
		cursor += len;
		return;
	}

	int index = 0;
	std::vector<uint8_t> lastbuf;
	bool in_continue = false;

	while (len > 0)
	{
		char asciibuf[17];
		asciibuf[16] = 0;

		if (len > 16 && mode_c) {
			std::vector<uint8_t> thisbuf(bitdata.begin()+cursor, bitdata.begin()+cursor+16);
			if (lastbuf == thisbuf) {
				if (!in_continue)
					printf("*\n");
				in_continue = true;
				cursor += 16;
				index += 16;
				len -= 16;
				continue;
			}
			lastbuf.swap(thisbuf);
			in_continue = false;
		}

		printf("%06x: ", index);
		index += 16;

		for (int i = 0; i < 16; i++) {
			if (i % 4 == 0)
				printf(" ");
			if (len > 0) {
				printf("%02x ", bitdata.at(cursor));
				asciibuf[i] = (32 <= bitdata.at(cursor) && bitdata.at(cursor) < 128) ? bitdata.at(cursor) : '.';
				cursor++, len--;
			} else {
				printf("   ");
				asciibuf[i] = ' ';
			}
		}

		printf(" |%s|\n", asciibuf);
	}
}

void print_pkt_len2()
{
	int len = (bitdata.at(cursor) << 8) + bitdata.at(cursor+1);

	if (mode_r)
		printf("\nPkt at byte %d with length %d:\n", cursor, len);
	cursor += 2;

	print_hexblock(len);
}

void print_pkt_key_len2()
{
	int key = bitdata.at(cursor);
	int len = (bitdata.at(cursor+1) << 8) + bitdata.at(cursor+2);

	if (mode_r)
		printf("\nPkt '%c' at byte %d with length %d:\n", key, cursor, len);
	cursor += 3;

	print_hexblock(len);
}

void print_pkt_key_len4()
{
	int key = bitdata.at(cursor);
	int len = (bitdata.at(cursor+1) << 24) + (bitdata.at(cursor+2) << 16) + (bitdata.at(cursor+3) << 8) + bitdata.at(cursor+4);

	if (mode_r)
		printf("\nPkt '%c' at byte %d with length %d:\n", key, cursor, len);
	cursor += 5;

	for (int i = 0; i < len; i+= 4)
		configdata.push_back((bitdata.at(cursor+i) << 24) + (bitdata.at(cursor+i+1) << 16) +
				(bitdata.at(cursor+i+2) << 8) + bitdata.at(cursor+i+3));

	print_hexblock(len);
}

#define REG_CRC      0
#define REG_FAR      1
#define REG_FDRI     2
#define REG_FDRO     3
#define REG_CMD      4
#define REG_CTL0     5
#define REG_MASK     6
#define REG_STAT     7
#define REG_LOUT     8
#define REG_COR0     9
#define REG_MFWR    10
#define REG_CBC     11
#define REG_IDCODE  12
#define REG_AXSS    13
#define REG_COR1    14
#define REG_WBSTAR  16
#define REG_TIMER   17
#define REG_CRCSET  19
#define REG_BOOTSTS 22
#define REG_CTL1    24
#define REG_BSPI    31

const char *regname(int addr)
{
	switch (addr)
	{
	case REG_CRC:     return "CRC";
	case REG_FAR:     return "FAR";
	case REG_FDRI:    return "FDRI";
	case REG_FDRO:    return "FDRO";
	case REG_CMD:     return "CMD";
	case REG_CTL0:    return "CTL0";
	case REG_MASK:    return "MASK";
	case REG_STAT:    return "STAT";
	case REG_LOUT:    return "LOUT";
	case REG_COR0:    return "COR0";
	case REG_MFWR:    return "MFWR";
	case REG_CBC:     return "CBC";
	case REG_IDCODE:  return "IDCODE";
	case REG_AXSS:    return "AXSS";
	case REG_COR1:    return "COR1";
	case REG_WBSTAR:  return "WBSTAR";
	case REG_TIMER:   return "TIMER";
	case REG_CRCSET:  return "CRCSET";
	case REG_BOOTSTS: return "BOOTSTS";
	case REG_CTL1:    return "CTL1";
	case REG_BSPI:    return "BSPI";
	default:          return "UNKOWN";
	}
}

void handle_write(int regaddr, uint32_t data)
{
	if (regaddr == REG_FAR) {
		frameptr = data;
		configframes[frameptr].clear();
		configframes_autoincr.erase(frameptr);
	}

	if (regaddr == REG_FDRI) {
		if (configframes[frameptr].size() == 101) {
			configframes[++frameptr].clear();
			configframes_autoincr.insert(frameptr);
		}
		configframes[frameptr].push_back(data);
	}
}

class frameid
{
	uint32_t value;

public:
	frameid(uint32_t v) : value(v) { }

	uint32_t get_value() const {
		return value;
	}

	int get_type() const {
		return selbits(value, 25, 23);
	}

	int get_topflag() const {
		return selbits(value, 22, 22);
	}

	int get_rowaddr() const {
		return selbits(value, 21, 17);
	}

	int get_coladdr() const {
		return selbits(value, 16, 7);
	}

	int get_minor() const {
		return selbits(value, 6, 0);
	}
};

int main(int argc, char **argv)
{
	int opt;
	while ((opt = getopt(argc, argv, "crmxyzpCf:F:o:")) != -1)
		switch (opt)
		{
		case 'c':
			mode_c = true;
			break;
		case 'r':
			mode_r = true;
			break;
		case 'm':
			mode_m = true;
			break;
		case 'x':
			mode_x = true;
			break;
		case 'y':
			mode_y = true;
			break;
		case 'z':
			mode_z = true;
			break;
		case 'p':
			mode_p = true;
			break;
		case 'C':
			chksum = true;
			break;
		case 'f':
			frames.insert(strtol(optarg, nullptr, 0));
			break;
		case 'F':
			frame_range_begin = strtol(strtok(optarg, ":"), nullptr, 0);
			frame_range_end = strtol(strtok(nullptr, ":"), nullptr, 0)+1;
			break;
		case 'o':
			outfile = optarg;
			break;
		default:
			goto help;
		}

	if (optind != argc && optind+1 != argc) {
help:
		fprintf(stderr, "\n");
		fprintf(stderr, "Usage: %s [options] [bitfile]\n", argv[0]);
		fprintf(stderr, "\n");
		fprintf(stderr, "  -c\n");
		fprintf(stderr, "    continuation mode. output '*' for repeating patterns\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -r\n");
		fprintf(stderr, "    raw mode. only decode top-level .bit file format framing\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -m\n");
		fprintf(stderr, "    command mode. print commands in config stream\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -z\n");
		fprintf(stderr, "    skip zero frames (frames with all bits cleared) in outout\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -x\n");
		fprintf(stderr, "    use format 'bit_%%08x_%%02x_%%02x_t%%d_h%%d_r%%d_c%%d_m%%d_w%%d_b%%d'\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -y\n");
		fprintf(stderr, "    use format 'bit_%%08x_%%02x_%%02x'\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -p\n");
		fprintf(stderr, "    output a binary netpgm image\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -C\n");
		fprintf(stderr, "    do not ignore the checksum in each frame\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -f <frame_address>\n");
		fprintf(stderr, "    only dump the specified frame (might be used more than once)\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -F <first_frame_address>:<last_frame_address>\n");
		fprintf(stderr, "    only dump frame in the specified range\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "  -o <outfile>\n");
		fprintf(stderr, "    write machine-readable output file with config frames\n");
		fprintf(stderr, "\n");
		fprintf(stderr, "In -x format the fields have the following meaning:\n");
		fprintf(stderr, "  - complete 32 bit hex frame id\n");
		fprintf(stderr, "  - hex word index within that frame\n");
		fprintf(stderr, "  - hex bit index within that word\n");
		fprintf(stderr, "  - decoded frame type from frame id\n");
		fprintf(stderr, "  - decoded top/botttom from frame id (top=0)\n");
		fprintf(stderr, "  - decoded row address from frame id\n");
		fprintf(stderr, "  - decoded column address from frame id\n");
		fprintf(stderr, "  - decoded minor address from frame id\n");
		fprintf(stderr, "  - word index with that frame (decimal)\n");
		fprintf(stderr, "  - bit index with that word (decimal)\n");
		fprintf(stderr, "\n");
		return 1;
	}

	if (optind+1 == argc) {
		FILE *f = fopen(argv[optind], "rb");
		if (f == nullptr) {
			printf("Can't open input file '%s' for reading!\n", argv[optind]);
			return 1;
		}
		while (1) {
			int c = fgetc(f);
			if (c == EOF) break;
			bitdata.push_back(c);
		}
		fclose(f);
	} else {
		while (1) {
			int c = getchar();
			if (c == EOF) break;
			bitdata.push_back(c);
		}
	}

	printf("Bitstream size: %d bytes\n", int(bitdata.size()));

	cursor = 0;
	while (cursor < int(bitdata.size()))
	{
		if (bitdata.at(cursor) == 0x00) {
			header_a = (const char*)&bitdata.at(cursor+2);
			print_pkt_len2();
			continue;
		}

		if (bitdata.at(cursor) == 0x62) {
			header_b = (const char*)&bitdata.at(cursor+3);
			print_pkt_key_len2();
			continue;
		}

		if (bitdata.at(cursor) == 0x63) {
			header_c = (const char*)&bitdata.at(cursor+3);
			print_pkt_key_len2();
			continue;
		}

		if (bitdata.at(cursor) == 0x64) {
			header_d = (const char*)&bitdata.at(cursor+3);
			print_pkt_key_len2();
			continue;
		}

		if (bitdata.at(cursor) == 0x65) {
			print_pkt_key_len4();
			continue;
		}

		printf("Top-level framing error at byte %d.\n", cursor);
		return 1;
	}

	if (!mode_r)
	{
		printf("Header A: %s\n", header_a.c_str());
		printf("Header B: %s\n", header_b.c_str());
		printf("Header C: %s\n", header_c.c_str());
		printf("Header D: %s\n", header_d.c_str());
		printf("Config size: %d words\n", int(configdata.size()));

		cursor = 0;
		while (cursor < int(configdata.size()))
			if (configdata.at(cursor++) == 0xAA995566)
				break;

		printf("Skipped %d padding/header words.\n", cursor);

		int current_write_reg = -1;

		while (cursor < int(configdata.size()))
		{
			uint32_t cmd = configdata.at(cursor);
			int cmd_header = selbits(cmd, 31, 29);

			// Type 1 Packet
			if (cmd_header == 1)
			{
				int opcode = selbits(cmd, 28, 27);
				int regaddr = selbits(cmd, 26, 13);
				int reserved = selbits(cmd, 12, 11);
				int wcount = selbits(cmd, 10, 0);

				if (reserved != 0 || regaddr > 31)
					goto cmderror;

				if (opcode == 0) {
					if (mode_m) {
						printf("%8d: 0x%08x NOP\n", cursor, configdata.at(cursor));
						if (mode_c && cmd == 0x20000000 && cursor+1 < int(configdata.size()) && cmd == configdata.at(cursor+1)) {
							while (cursor+1 < int(configdata.size()) && cmd == configdata.at(cursor+1)) cursor++;
							printf("*\n");
						}
					}
					goto handle_type1_payload;
				}

				if (opcode == 1) {
					if (mode_m)
						printf("%8d: 0x%08x Read %s register (%d)\n", cursor, configdata.at(cursor), regname(regaddr), regaddr);
					goto handle_type1_payload;
				}

				if (opcode == 2) {
					if (mode_m)
						printf("%8d: 0x%08x Write %s register (%d)\n", cursor, configdata.at(cursor), regname(regaddr), regaddr);
					current_write_reg = regaddr;
					goto handle_type1_payload;
				}

				if (0) {
			handle_type1_payload:
					cursor++;

					uint32_t last_word = wcount ? ~configdata.at(cursor) : 0;
					bool in_continue = false;

					while (wcount--) {
						if (mode_m) {
							uint32_t this_word = configdata.at(cursor);
							if (mode_c && last_word == this_word) {
								if (!in_continue)
									printf("*\n");
								in_continue = true;
							} else {
								if (current_write_reg == REG_FAR) {
									frameid fid(this_word);
									printf("%8d: 0x%08x FAR: Type=%d, Top=%d, Row=%d, Col=%d, Minor=%d\n",
											cursor, fid.get_value(), fid.get_type(), fid.get_topflag(),
											fid.get_rowaddr(), fid.get_coladdr(), fid.get_minor());
								} else
									printf("%8d: 0x%08x\n", cursor, this_word);
								in_continue = false;
							}
							last_word = this_word;
						}
						handle_write(regaddr, configdata.at(cursor));
						cursor++;
					}
					continue;
				}
			}

			// Type 2 Packet
			if (cmd_header == 2)
			{
				int opcode = selbits(cmd, 28, 27);
				int wcount = selbits(cmd, 26, 0);

				if (opcode != 2)
					goto cmderror;

				if (mode_m)
					printf("%8d: 0x%08x Type 2 write\n", cursor, configdata.at(cursor));

				uint32_t last_word = configdata.at(cursor);
				bool in_continue = false;

				cursor++;
				while (wcount--)
				{
					uint32_t this_word = configdata.at(cursor);
					handle_write(current_write_reg, this_word);

					if (mode_m) {
						if (mode_c && last_word == this_word) {
							if (!in_continue)
								printf("*\n");
							in_continue = true;
						} else {
							in_continue = false;
							printf("%8d: Payload: 0x%08x\n", cursor, this_word);
						}
					}

					last_word = this_word;
					cursor++;
				}
				continue;
			}

		cmderror:
			printf("%8d: Unknown config command: 0x%08x\n", cursor, cmd);
			return 1;
		}

		printf("Number of configuration frames: %d\n", int(configframes.size()));

		FILE *f = stdout;

		if (outfile != nullptr)
		{
			f = fopen(outfile, "w");

			if (f == nullptr) {
				printf("Can't open output file '%s' for writing!\n", outfile);
				return 1;
			}
		}

		if (outfile == nullptr)
			fprintf(f, "\n");

		std::vector<std::vector<bool>> pgmdata;
		std::vector<int> pgmsep;

		for (auto &it : configframes)
		{
			if (mode_z && it.second == zero_frame)
				continue;

			frameid fid(it.first);

			if (!frames.empty() && !frames.count(fid.get_value()))
				continue;

			if (frame_range_begin != frame_range_end && (fid.get_value() < frame_range_begin || frame_range_end <= fid.get_value()))
				continue;

			if (outfile == nullptr)
				printf("Frame 0x%08x (Type=%d Top=%d Row=%d Column=%d Minor=%d%s):\n", fid.get_value(), fid.get_type(), fid.get_topflag(),
						fid.get_rowaddr(), fid.get_coladdr(), fid.get_minor(), configframes_autoincr.count(fid.get_value()) ? " AUTO_INCREMENT" : "");

			if (it.second.size() != 101) {
				printf(" unusual frame size: %d\n", int(it.second.size()));
				return 1;
			}

			if (mode_p)
			{
				if (fid.get_minor() == 0 && !pgmdata.empty())
					pgmsep.push_back(pgmdata.size());

				pgmdata.push_back(std::vector<bool>());

				for (int i = 0; i < 101; i++)
				for (int k = 0; k < 32; k++)
					pgmdata.back().push_back((it.second.at(i) & (1 << k)) != 0);
			}
			else
			if (mode_x || mode_y)
			{
				for (int i = 0; i < 101; i++)
				for (int k = 0; k < 32; k++)
					if ((i != 50 || chksum) && ((it.second.at(i) & (1 << k)) != 0)) {
						if (mode_x)
							fprintf(f, "bit_%08x_%02x_%02x_t%d_h%d_r%d_c%d_m%d_w%d_b%d\n",
									fid.get_value(), i, k, fid.get_type(), fid.get_topflag(), fid.get_rowaddr(),
									fid.get_coladdr(), fid.get_minor(), i, k);
						else
							fprintf(f, "bit_%08x_%02x_%02x\n", fid.get_value(), i, k);
					}
				if (outfile == nullptr)
					fprintf(f, "\n");
			}
			else
			{
				if (outfile != nullptr)
					fprintf(f, ".frame 0x%08x%s\n", fid.get_value(), configframes_autoincr.count(fid.get_value()) ? " AI" : "");

				for (int i = 0; i < 101; i++)
					fprintf(f, "%08x%s", (i != 50 || chksum) ? it.second.at(i) : 0, (i % 6) == 5 ? "\n" : " ");
				fprintf(f, "\n\n");
			}
		}

		if (mode_p)
		{
			int width = pgmdata.size() + pgmsep.size();
			int height = 101*32+100;
			fprintf(f, "P5 %d %d 15\n", width, height);

			for (int y = 0, bit = 101*32-1; y < height; y++, bit--)
			{
				for (int x = 0, frame = 0, sep = 0; x < width; x++, frame++)
				{
					if (sep < int(pgmsep.size()) && frame == pgmsep.at(sep)) {
						fputc(8, f);
						x++, sep++;
					}

					fputc(pgmdata.at(frame).at(bit) ? 15 : 0, f);
				}

				if (bit % 32 == 0 && y) {
					for (int x = 0; x < width; x++)
						fputc(8, f);
					y++;
				}
			}
		}

		if (outfile != nullptr)
			fclose(f);
	}

	printf("DONE\n");
	return 0;
}

