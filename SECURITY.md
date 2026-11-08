# Security policy

## Supported versions

DarwinTV is pre-alpha research software. There are no supported releases and no security
guarantees. Do not run it on hardware you cannot afford to lose.

## Reporting a vulnerability

Please **do not open a public issue** for a security problem. Use GitHub's private
"Report a vulnerability" advisory flow on this repository, or contact the maintainers listed in
`CODEOWNERS`.

Include:

- affected component and commit,
- reproduction steps,
- impact,
- any suggested fix.

## Scope

In scope:

- memory-safety bugs in the loader, host tools or kernel patches,
- supply-chain problems in the build or CI,
- accidentally committed secrets or Apple material.

Out of scope:

- Apple's own firmware, kernel or userland vulnerabilities,
- bypassing activation, DRM or code signing,
- "jailbreak" requests for retail Apple devices.

## Safe harbor

We will not pursue legal action against researchers who act in good faith, avoid privacy
violations, avoid data destruction, and give us reasonable time to fix the issue before
disclosure.
