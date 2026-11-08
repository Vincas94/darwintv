#ifndef DARWINTV_BOOT_ARGS_H
#define DARWINTV_BOOT_ARGS_H

#include <stdint.h>

#define BOOT_LINE_LENGTH 608

struct boot_video {
	uint64_t v_baseAddr;
	uint64_t v_display;
	uint64_t v_rowBytes;
	uint64_t v_width;
	uint64_t v_height;
	uint64_t v_depth;
};

/*
 * XNU arm64 boot_args, Revision 2 / Version 2.
 * Source: pexpert/pexpert/arm64/boot.h in xnu-8796.141.3.
 *
 * The M1 loader does not fill this yet. It is here so the next patch has one
 * definition shared by the loader, the ADT writer and the tests.
 */
struct boot_args {
	uint16_t Revision;
	uint16_t Version;
	uint64_t virtBase;
	uint64_t physBase;
	uint64_t memSize;
	uint64_t topOfKernelData;
	struct boot_video Video;
	uint32_t machineType;
	uint64_t deviceTreeP;
	uint32_t deviceTreeLength;
	char CommandLine[BOOT_LINE_LENGTH];
	uint64_t bootFlags;
	uint64_t memSizeActual;
};

#endif /* DARWINTV_BOOT_ARGS_H */
