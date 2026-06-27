# Security goals and scope

This repository uses AVISPA to check symbolic secrecy and authentication goals for two HLPSL models:

- `models/spaka_local_auth_key_update.hlpsl`
- `models/spaka_cross_region.hlpsl`

The checks are performed under the Dolev--Yao attacker model, with bounded sessions and typed messages.

## Secrecy goals

| Model | Goal | Exact HLPSL event | Protocol meaning |
|---|---|---|---|
| Local | `sec_local_key` | `secret(SK_local', sec_local_key, {V, ATAj})` | The first local session key derived after M2/M3 must remain unknown to the network attacker. |
| Local | `sec_updated_key` | `secret(SK_new, sec_updated_key, {V, ATAj})` and `secret(SK_new', sec_updated_key, {V, ATAj})` | The post-update key derived during the local key-update phase must remain unknown to the network attacker. |
| Cross-regional | `sec_cross_key` | `secret(SK_cv', sec_cross_key, {CV, ATAi})` | The cross-regional session key derived after M6 and the post-verification confirmation must remain unknown to the network attacker. |
| Cross-regional | `sec_p1` | `secret(P1', sec_p1, {CV, ATAi, ATAj, TA})` | The first PUF-derived verification value must remain hidden from the network attacker. |
| Cross-regional | `sec_p2` | `secret(P2', sec_p2, {CV, ATAi, ATAj, TA})` | The second PUF-derived verification value must remain hidden from the network attacker. |

## Authentication goals

| Model | Goal | Exact HLPSL event | Protocol meaning |
|---|---|---|---|
| Local | `local_ataj_auth` | `witness(ATAj, V, local_ataj_auth, Ci'.T1')` and `request(V, ATAj, local_ataj_auth, Ci'.T1')` | The vehicle accepts ATAj as the origin of the local challenge message after validating M2. |
| Local | `local_vehicle_auth` | `witness(V, ATAj, local_vehicle_auth, Ci_next'.T2')` and `request(ATAj, V, local_vehicle_auth, Ci_next'.T2')` | ATAj accepts the vehicle as the origin of the second local authentication message after validating M3. |
| Local | `local_key_update_request` | `witness(V, ATAj, local_key_update_request, IDV.Cnew'.Tnew')` and `request(ATAj, V, local_key_update_request, IDV.Cnew'.Tnew')` | ATAj authenticates the vehicle's key-update request. |
| Local | `local_key_update_ack` | `witness(ATAj, V, local_key_update_ack, Tack'.Tnew')` and `request(V, ATAj, local_key_update_ack, Tack'.Tnew)` | The vehicle authenticates the key-update acknowledgement from ATAj. |
| Cross-regional | `cross_atai_auth` | `witness(ATAi, CV, cross_atai_auth, P1_store'.T8_store')` and `request(CV, ATAi, cross_atai_auth, P1_prime'.T8')` | CV authenticates ATAi only after validating `Authi` in M6. |
| Cross-regional | `cross_cv_auth` | `witness(CV, ATAi, cross_cv_auth, P2_prime'.T8')` and `request(ATAi, CV, cross_cv_auth, P2_store.T8_store)` | ATAi authenticates CV only after validating `Authcv` in the final confirmation step. |

## What AVISPA verifies

AVISPA checks whether the HLPSL model admits an attack trace in the explored bounded state space.
For secrecy goals, it searches for a symbolic execution in which the intruder derives the protected term.
For authentication goals, it searches for a trace in which a `request` event is not matched by a corresponding `witness` event with the same protocol identifier and data term.

## What AVISPA does not verify

AVISPA does not prove:

- full computational security;
- resistance to physical PUF extraction or cloning;
- resistance to ageing, vibration, or manufacturing drift;
- resistance to side-channel or fault-injection attacks;
- correctness of implementation details outside the HLPSL abstraction;
- numerical clock-window checks such as `|t_current - t_i| < Delta t`.

## Exact interpretation of SAFE

A `SAFE` result means that, for the explored bounded-session symbolic model, AVISPA did not find an attack trace violating the modeled secrecy or authentication goals.
It does not mean:

- that the real-world protocol is proven secure in every deployment;
- that the implementation is free of bugs;
- that the PUF hardware is physically secure;
- that the model covers all possible session counts or all timing behaviors.

`SAFE` should therefore be read as a bounded symbolic non-attack result, not as an unconditional security proof.
