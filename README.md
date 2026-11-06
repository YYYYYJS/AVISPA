# SPAKA AVISPA supplementary models

OFMC and CL-AtSe returned **SAFE** for both HLPSL models under the declared security goals and bounded-session setting. OFMC 2024 reports the corresponding result as **NO_ATTACK_FOUND**.

| Model | OFMC | CL-AtSe |
| --- | --- | --- |
| Vehicle authentication and key update | SAFE | SAFE |
| Cross-regional key generation and authentication | SAFE | SAFE |

The source models, generated IF, unmodified backend outputs, normal-execution traces and reproducible verification scripts are supplied together. Exact goals are defined in each HLPSL `goal` block and recorded in [declared_goals.json](docs/declared_goals.json). The source hashes and execution provenance are recorded in `verification_manifest.json`.

## Model scope

Each model instantiates one composed session with Dolev-Yao network control. The local ATA used-challenge cache is initially empty; recording the issued Ci and rejecting `Ci_next = Ci` implements its sole M3 receive check in this environment. Timestamps are symbolic values. The model does not implement numerical freshness windows, persistent history or unrestricted concurrent sessions.

The PUF is an ideal private-seed response abstraction. Backend messages and the final Authcv application record use ideal symmetric protection. Physical SRAM behavior, actual nonce/tag encoding and implementation-level AEAD behavior are outside the model.

Cross-regional authentication checks concern `P1.t8` at the vehicle and `P2.t8` after the ATA successfully processes the protected final record. SAFE does not establish vehicle-side full-key agreement at the earlier M6 step: M6 does not authenticate the second challenge, whose alteration can change the vehicle's provisional key; the ATA then rejects the mismatching final record. The reported results apply to the goals declared in the supplied models.

Normal-execution traces separately confirm reachable terminal states, matching endpoint keys and matching authentication events. They establish that the modeled exchanges can complete; they are not standalone security proofs. See [model mapping](docs/model_mapping.md).

## Files

- `models/`: HLPSL sources.
- `if/`: raw hlpsl2if output for CL-AtSe.
- `ofmc_if/`: equivalent IF state layout for OFMC, with adapter checks.
- `results/`: unmodified translator/backend outputs, tool versions and runtime setup logs.
- `execution/`: normal completed-execution traces.
- `verification_manifest.json`: exact commands, model/IF/log/source hashes and results.
- `verification/`: the matching complete evidence archive.
- `scripts/`: pinned runtime setup, IF adaptation and verification.

## Reproduce

On Linux x86_64 with Python 3, bash, curl, tar, unzip and dpkg-deb:

    bash scripts/setup-linux-runtime.sh /tmp/spaka-avispa
    source /tmp/spaka-avispa/activate.sh
    bash scripts/setup-ofmc2024.sh /tmp/spaka-ofmc2024
    source /tmp/spaka-ofmc2024/activate.sh
    bash scripts/run_avispa.sh

The setup scripts fetch official distributions, verify SHA256 hashes and unpack dependencies into isolated directories. Versions: hlpsl2if 2.0, OFMC 2012c, OFMC 2024 and CL-AtSe 2.3-4. CL-AtSe is run with its default preprocessing and with preprocessing disabled. Outputs are written to `validation-output/`.

The OFMC adapter reversibly reorders state fields for backend compatibility and preserves the attack predicates. CL-AtSe uses the original translator IF. Verification fails on translation errors, unexpected results, changed declared goals or an unverified normal completion.

The evidence manifest retains the actual build commit and run identifiers. Publication may package those outputs in a later snapshot; verify the listed source hashes against the supplied files. This release preserves the manuscript protocol formulas and does not modify the manuscript itself.
