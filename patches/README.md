# patches

Kernel changes live here as `git format-patch` files against the pinned XNU tag.

```sh
# make a change in third_party/xnu, then:
git -C third_party/xnu format-patch -1 --stdout > patches/0001-my-change.patch

# verify the whole series on a fresh checkout:
scripts/fetch-xnu.sh
scripts/apply-patches.sh
```

Rules:

- one logical change per patch,
- `NNNN-short-description.patch`,
- no Apple binaries, IPSWs, kernelcaches or userland,
- APSL-2.0 for patches derived from XNU; keep Apple's notices,
- no 175 MB XNU fork in git.

The planned series and dependency order are in `docs/patches.md`.
