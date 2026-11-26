# Third-party notices

This repository vendors no third-party code. Runtime dependencies introduced by
the executor face (preview.11) are listed below.

## cryptography (Python package)

- Used by `mcp/irreversible_executor.py` (AES-256-GCM for the in-field DEK
  keystore; ciphertext-only ledger bodies; dissipation = key destruction).
- Version range: `cryptography >= 3.4` (AESGCM + InvalidTag imports only).
- License: dual-licensed under the Apache License 2.0 and the BSD 3-Clause
  License. Copyright: the cryptography developers.
- Not vendored: installed as a normal dependency (`pip install cryptography`).

## Lean toolchain (build-time only, not shipped)

- `harness/*.lean` mirrors are verified with Lean 4.15.0 (core-only, no
  mathlib). Lean is a build/verification tool and is not a runtime dependency
  of the plugin.
