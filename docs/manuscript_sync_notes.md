# Manuscript synchronization notes

Use this checklist to keep the manuscript aligned with the final HLPSL models.

- [ ] After Step 7 of Section 5.3, add the exact final confirmation sentence below:

  ```latex
  Finally, \(CV\) sends \(Auth_{cv}=\mathrm{Hash}(P'_2\parallel t_8)\) to \(ATA_i\). The \(ATA_i\) accepts \(CV\) only if \(Auth_{cv}=\mathrm{Hash}(P_2\parallel t_8)\), after which both parties activate \(ck_{cv}\).
  ```

- [ ] Keep Fig. 5 unchanged. Do not introduce `t9` or any alternate confirmation flow.
- [ ] State explicitly that `ATA_i` accepts `CV` only after validating `Authcv`.
- [ ] Update the AVISPA description and the security-goal description so that they use the same identifiers as the final HLPSL files.
- [ ] Decide that the additional `Authcv` field is included in the communication-cost accounting, because it is a transmitted protocol message element.
- [ ] Use the exact same names for identities, challenges, timestamps, PUF-derived values, authentication values, and session keys as in the final HLPSL files:
  - identities: `CV`, `ATAi`, `ATAj`, `TA`, `IDVcv`, `IDAi`
  - challenges and timestamps: `C1`, `C2`, `T3`, `T4`, `T5`, `T6`, `T7`, `T8`, `T0`, `T1`, `T2`, `Tnew`, `Tack`
  - PUF-derived values: `R1`, `R2`, `P1`, `P2`, `Ri`, `Ri_next`, `Rnew`
  - authenticators: `Authi`, `Authcv`, `Auths`, `Authd`, `Hup`, `Hack`
  - session keys: `SK_local`, `SK_new`, `SK_cv`

- [ ] Keep the manuscript language consistent with the bounded symbolic interpretation of AVISPA: `SAFE` means no attack trace was found in the explored HLPSL model, not that the real-world protocol is proven secure.
