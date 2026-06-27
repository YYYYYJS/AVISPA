# SPAKA AVISPA Artifacts

This repository contains the HLPSL models, IF translations, backend verification logs, and supporting notes for the SPAKA protocol study. The models are aligned with the manuscript-level protocol description and are intended for bounded symbolic analysis in AVISPA.

The verification claim supported here is deliberately limited:

> Under the modeled bounded-session Dolev-Yao setting, no attack trace violating the stated symbolic secrecy and authentication goals was found for the local model; the cross-regional model does produce an attack trace on the `cross_cv_auth` authentication goal and that trace is preserved in `results/`.

This repository does not claim a real-world proof of security.

## Repository layout

```text
README.md
models/
  spaka_local_auth_key_update.hlpsl
  spaka_cross_region.hlpsl
if/
  spaka_local_auth_key_update.if
  spaka_cross_region.if
results/
  spaka_local_auth_key_update_hlpsl2if.txt
  spaka_local_auth_key_update_ofmc.txt
  spaka_local_auth_key_update_clatse.txt
  spaka_cross_region_hlpsl2if.txt
  spaka_cross_region_ofmc.txt
  spaka_cross_region_clatse.txt
docs/
  protocol_to_model_mapping.md
  security_goals_and_scope.md
  manuscript_sync_notes.md
scripts/
  run_avispa.sh
  run_avispa.ps1
legacy/
  old_simplified/
```

The `legacy/old_simplified/` directory preserves the earlier simplified artifacts. They are not the final verification models.

## Toolchain and environment

The models were validated in the SPAN Ubuntu VM (`SPAN-Ubuntu10.10-light`) using the bundled AVISPA toolchain:

- `hlpsl2if` from `/home/span/span/bin/translator/hlpsl2if`
- `ofmc` from `/home/span/span/bin/backends/ofmc/ofmc`
- `cl-atse` from `/home/span/span/bin/backends/cl/cl-atse`

The bundled OFMC binary reports:

```text
OFMC Version of 2006/02/13
```

`cl-atse` did not print an explicit version banner in this environment.

## How to run the verification

Inside the VM, from the repository root:

```bash
cd /home/span/Desktop/share_AVISPA

/home/span/span/bin/translator/hlpsl2if models/spaka_local_auth_key_update.hlpsl
cp models/spaka_local_auth_key_update.if if/
/home/span/span/bin/backends/ofmc/ofmc if/spaka_local_auth_key_update.if
/usr/bin/timeout 60 /home/span/span/bin/backends/cl/cl-atse if/spaka_local_auth_key_update.if

/home/span/span/bin/translator/hlpsl2if models/spaka_cross_region.hlpsl
cp models/spaka_cross_region.if if/
/home/span/span/bin/backends/ofmc/ofmc if/spaka_cross_region.if
/usr/bin/timeout 60 /home/span/span/bin/backends/cl/cl-atse if/spaka_cross_region.if
```

On Windows, the recommended entry point is `scripts/run_avispa.ps1`, which invokes the same workflow inside the running SPAN VM via `VBoxManage guestcontrol`. The Bash script `scripts/run_avispa.sh` is the direct VM-side runner.

## Modeling assumptions

The verification uses the standard AVISPA symbolic model:

- Dolev-Yao attacker control on the network.
- Bounded sessions and bounded search.
- Symbolic freshness for nonces, timestamps, and challenges.
- Symbolic `PUF(C)` behavior implemented as a private challenge-dependent function shared only by the enrolled vehicle and its home ATA.

The PUF abstraction is intentionally symbolic. It does not model:

- physical extraction or cloning of a real PUF,
- ageing, vibration, or temperature drift,
- side-channel leakage,
- fault injection,
- implementation-level cryptographic hardening,
- numerical timestamp-window checks such as `|t_current - t_i| < Delta t`.

## Interpretation of results

- `SAFE` means that AVISPA found no counterexample within the explored bounded symbolic state space.
- `UNSAFE` means that AVISPA found an attack trace in the explored model.
- `SAFE` does not prove full real-world security.
- `UNSAFE` does not automatically imply the real protocol is insecure; it does mean the modeled abstraction admits an attack trace that must be taken seriously.

## Verification summary

| Model | HLPSL-to-IF | OFMC | CL-AtSe | Notes |
| --- | --- | --- | --- | --- |
| `spaka_local_auth_key_update.hlpsl` | Success | SAFE | SAFE | hlpsl2if reported one warning on `local_v` transition 3; no attack trace found in the bounded symbolic model. |
| `spaka_cross_region.hlpsl` | Success | UNSAFE | UNSAFE | Attack trace preserved for `cross_cv_auth`. |
