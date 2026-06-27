# SPAKA AVISPA Artifacts

This repository contains the HLPSL models and AVISPA validation artifacts for the SPAKA protocol in a bounded symbolic setting.
The models cover:

- local authentication and dynamic key update;
- cross-regional authentication with TA-mediated forwarding;
- raw IF translations and backend logs;
- reproducible execution scripts for the SPAN Ubuntu guest.

The models are evaluated under the Dolev--Yao attacker model with bounded sessions and typed messages.
The SRAM-PUF behavior is represented symbolically by a private challenge-dependent function `puf(PUFSeed, C)` that is known only to the enrolled vehicle and the corresponding home ATA.
In the cross-regional model, the final `Authcv` check is represented as a logical receive event, but it corresponds to a field piggybacked in the first protected application payload rather than to an extra counted packet.

Validation was last executed on 2026-06-27.

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

The `legacy/old_simplified/` directory preserves earlier simplified models for reference only.
Those files are not the final verified artifacts.

## Validation summary

| Model | HLPSL translation | OFMC | CL-AtSe | Notes |
|---|---|---|---|---|
| `models/spaka_local_auth_key_update.hlpsl` | Successful, with one non-fatal translator warning about a missing event in `local_v` transition 3 | SAFE | SAFE | Bounded-session typed-model result |
| `models/spaka_cross_region.hlpsl` | Successful | SAFE | SAFE | Bounded-session typed-model result |

The raw backend outputs are stored in `results/`.

## Required environment

The current verification workflow was run inside the VirtualBox guest `SPAN-Ubuntu10.10-light` with the AVISPA/SPAN tool bundle installed under:

```text
/home/span/span/bin/translator/hlpsl2if
/home/span/span/bin/backends/ofmc/ofmc
/home/span/span/bin/backends/cl/cl-atse
```

The guest shared folder is mounted at:

```text
/home/span/Desktop/share_AVISPA
```

The Windows-side helper script uses `VBoxManage.exe` and VirtualBox guest control to launch the guest-side script.

## Exact verification commands

Run the full workflow inside the Ubuntu guest:

```bash
cd /home/span/Desktop/share_AVISPA
./scripts/run_avispa.sh
```

Run the same workflow from Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_avispa.ps1
```

Manual commands for one model are:

```bash
/home/span/span/bin/translator/hlpsl2if models/spaka_local_auth_key_update.hlpsl
cp -f models/spaka_local_auth_key_update.if if/spaka_local_auth_key_update.if
/home/span/span/bin/backends/ofmc/ofmc if/spaka_local_auth_key_update.if
/home/span/span/bin/backends/cl/cl-atse if/spaka_local_auth_key_update.if
```

and:

```bash
/home/span/span/bin/translator/hlpsl2if models/spaka_cross_region.hlpsl
cp -f models/spaka_cross_region.if if/spaka_cross_region.if
/home/span/span/bin/backends/ofmc/ofmc if/spaka_cross_region.if
/home/span/span/bin/backends/cl/cl-atse if/spaka_cross_region.if
```

## Modeling assumptions

- Dolev--Yao network attacker with full control of the public channel.
- Bounded-session analysis only; the backends search a finite symbolic state space.
- Typed HLPSL model.
- Fresh timestamps and nonces are abstracted by `new()` and bound into the relevant messages and hashes.
- The PUF is represented symbolically by `puf(PUFSeed, C)` rather than by a physical hardware model.

## Verification limitations

The AVISPA runs in this repository do not verify:

- physical PUF extraction or cloning resistance;
- ageing, drift, vibration, or environmental reliability of the PUF;
- side-channel or fault-injection resistance;
- implementation-level security;
- numerical timestamp-window checks such as `|t_current - t_i| < Delta t`;
- a proof of full real-world protocol security.

In particular, `SAFE` means only that no symbolic attack trace was found in the explored bounded model.
It does not mean the protocol is proven secure in all executions or against all implementation-level threats.

## Generated files

- `if/` contains the IF files used by the backends.
- `results/` contains the raw AVISPA outputs captured during validation.
- `models/*.hlpsl` are the authoritative source models.
