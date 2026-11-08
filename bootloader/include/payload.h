#ifndef DARWINTV_PAYLOAD_H
#define DARWINTV_PAYLOAD_H

#include <stdint.h>

#define PAYLOAD_MAGIC "DTVPLD01"
#define PAYLOAD_VERSION 1u
#define PAYLOAD_HEADER_SIZE 128u
#define PAYLOAD_SEGMENT_SIZE 40u
#define PAYLOAD_MAX_SIZE 0x04000000u
#define PAYLOAD_MAX_SEGMENTS 64u

struct payload_header {
	char magic[8];
	uint32_t version;
	uint32_t header_size;
	uint64_t total_size;
	uint64_t entry_va;
	uint64_t virt_base;
	uint64_t phys_base;
	uint64_t mem_size;
	uint64_t adt_offset;
	uint64_t adt_size;
	uint64_t cmdline_offset;
	uint64_t cmdline_size;
	uint32_t nsegs;
	uint32_t crc32;
	uint8_t reserved[32];
} __attribute__((packed));

struct payload_segment {
	uint64_t file_offset;
	uint64_t file_size;
	uint64_t vmaddr;
	uint64_t vmsize;
	uint64_t reserved;
} __attribute__((packed));

struct payload_info {
	const struct payload_header *header;
	const struct payload_segment *segments;
	const uint8_t *adt;
	const char *cmdline;
	uint32_t cmdline_size;
};

int payload_validate(const void *buffer, uint32_t max_size, struct payload_info *info);
void payload_print(const struct payload_info *info);

#endif /* DARWINTV_PAYLOAD_H */
