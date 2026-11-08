#include "payload.h"

#include "board.h"
#include "pl011.h"

#include <stdint.h>

static const uint32_t crc32_nibble[16] = {
    0x00000000u, 0x1DB71064u, 0x3B6E20C8u, 0x26D930ACu, 0x76DC4190u, 0x6B6B51F4u,
    0x4DB26158u, 0x5005713Cu, 0xEDB88320u, 0xF00F9344u, 0xD6D6A3E8u, 0xCB61B38Cu,
    0x9B64C2B0u, 0x86D3D2D4u, 0xA00AE278u, 0xBDBDF21Cu,
};

static uint32_t crc32_update(uint32_t crc, const uint8_t *data, uint32_t length)
{
	uint32_t i;

	for (i = 0; i < length; i++) {
		crc = (crc >> 4) ^ crc32_nibble[(crc ^ data[i]) & 0xFu];
		crc = (crc >> 4) ^ crc32_nibble[(crc ^ (data[i] >> 4)) & 0xFu];
	}
	return crc;
}

static uint32_t payload_crc(const uint8_t *buffer, uint64_t total_size)
{
	static const uint8_t zero_crc[4] = {0, 0, 0, 0};
	uint32_t crc = 0xFFFFFFFFu;

	/* The CRC field is at offset 92 in the header. */
	crc = crc32_update(crc, buffer, 92u);
	crc = crc32_update(crc, zero_crc, sizeof(zero_crc));
	crc = crc32_update(crc, buffer + 96u, (uint32_t)(total_size - 96u));
	return crc ^ 0xFFFFFFFFu;
}

int payload_validate(const void *buffer, uint32_t max_size, struct payload_info *info)
{
	const struct payload_header *header = (const struct payload_header *)buffer;
	const uint8_t *bytes = (const uint8_t *)buffer;
	uint64_t table_end;
	uint32_t i;
	int magic_ok = 1;

	if (max_size < PAYLOAD_HEADER_SIZE) {
		return 0;
	}
	for (i = 0; i < sizeof(header->magic); i++) {
		if (header->magic[i] != PAYLOAD_MAGIC[i]) {
			magic_ok = 0;
			break;
		}
	}
	if (!magic_ok || header->version != PAYLOAD_VERSION ||
	    header->header_size < PAYLOAD_HEADER_SIZE || header->total_size > max_size ||
	    header->total_size < PAYLOAD_HEADER_SIZE || header->nsegs == 0 ||
	    header->nsegs > PAYLOAD_MAX_SEGMENTS) {
		return 0;
	}

	if (header->header_size > header->total_size ||
	    header->nsegs > (header->total_size - header->header_size) / PAYLOAD_SEGMENT_SIZE) {
		return 0;
	}
	table_end = header->header_size + (uint64_t)header->nsegs * PAYLOAD_SEGMENT_SIZE;
	if (table_end > header->total_size || header->adt_offset > header->total_size ||
	    header->adt_size > header->total_size - header->adt_offset ||
	    header->cmdline_offset > header->total_size ||
	    header->cmdline_size > header->total_size - header->cmdline_offset) {
		return 0;
	}

	if (payload_crc(bytes, header->total_size) != header->crc32) {
		return 0;
	}

	for (i = 0; i < header->nsegs; i++) {
		const struct payload_segment *segment =
		    (const struct payload_segment *)(bytes + header->header_size +
						     (uint64_t)i * PAYLOAD_SEGMENT_SIZE);
		uint64_t offset;

		if (segment->file_offset > header->total_size ||
		    segment->file_size > header->total_size - segment->file_offset ||
		    segment->vmaddr < header->virt_base) {
			return 0;
		}
		offset = segment->vmaddr - header->virt_base;
		if (offset > header->mem_size || segment->vmsize > header->mem_size - offset) {
			return 0;
		}
	}

	if (info != 0) {
		info->header = header;
		info->segments = (const struct payload_segment *)(bytes + header->header_size);
		info->adt = bytes + header->adt_offset;
		info->cmdline = (const char *)(bytes + header->cmdline_offset);
		info->cmdline_size = (uint32_t)header->cmdline_size;
	}
	return 1;
}

void payload_print(const struct payload_info *info)
{
	const struct payload_header *header = info->header;
	uint32_t i;

	pl011_puts(PL011_BASE, "payload:  ");
	pl011_puts(PL011_BASE, PAYLOAD_MAGIC);
	pl011_puts(PL011_BASE, " v");
	pl011_put_hex32(PL011_BASE, header->version);
	pl011_puts(PL011_BASE, " size=");
	pl011_put_hex(PL011_BASE, header->total_size);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "entry:    ");
	pl011_put_hex(PL011_BASE, header->entry_va);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "virt:     ");
	pl011_put_hex(PL011_BASE, header->virt_base);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "phys:     ");
	pl011_put_hex(PL011_BASE, header->phys_base);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "mem:      ");
	pl011_put_hex(PL011_BASE, header->mem_size);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "segments: ");
	pl011_put_hex32(PL011_BASE, header->nsegs);
	pl011_puts(PL011_BASE, "\n");

	for (i = 0; i < header->nsegs; i++) {
		pl011_puts(PL011_BASE, "  seg ");
		pl011_put_hex(PL011_BASE, info->segments[i].vmaddr);
		pl011_puts(PL011_BASE, " size ");
		pl011_put_hex(PL011_BASE, info->segments[i].file_size);
		pl011_puts(PL011_BASE, "\n");
	}

	if (info->cmdline_size > 0 && info->cmdline[info->cmdline_size - 1] == '\0') {
		pl011_puts(PL011_BASE, "cmdline:  ");
		pl011_puts(PL011_BASE, info->cmdline);
		pl011_puts(PL011_BASE, "\n");
	} else {
		pl011_puts(PL011_BASE, "cmdline:  (invalid)\n");
	}
}
