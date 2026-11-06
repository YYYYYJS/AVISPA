# Model-to-protocol mapping

## Local authentication and key update

The model uses native XOR. Receiving `N xor R` with the known PUF-dependent R binds the peer nonce and is equivalent to recovering `N = M xor R`. All values bound in a receive transition use the corresponding primed HLPSL variables. The current local session key is used in the subsequent update.

The author confirmed that ATA records each issued challenge immediately and rejects used challenges in M3. In the single-session, initially empty-cache model, Used={Ci} before the sole M3 receive. The stored Ci and `Ci_next' /= Ci` express this check. It is not a shared cache model for concurrent sessions or preexisting challenge history.

Auths remains `H(Ms.Ri.T1)`; Authd remains `H(Md.Ri_next.T2)`. Key derivations and authentication-event payloads are retained. A completed execution reaches V=4 and ATA=3 with equal local and updated keys and four matching authentication requests.

## Cross-regional exchange

ATAi receives and forwards M1 as an opaque public-key ciphertext; TA verifies its nested contents. The protected backend messages carry the identity, both challenges and the session-specific verification values through the trusted infrastructure.

P1 is `H(IDVcv.PUF(PUFSeed,C1).T6)` and P2 is `H(IDVcv.PUF(PUFSeed,C2).T6)`. The two response branches are separate. Authi remains `H(P1.T8)`, and the session key remains `H(P1.P2.T8)`.

CV sends `{H(P2_prime'.T8')}_SK_cv'` in its final protected record. ATAi receives `{H(P2.T8)}_SK_cv` under its own derived key before accepting CV. The generated IF represents this with symmetric `scrypt`, not public-key encryption. The key remains the prescribed hash-derived value.

The goals comprise session-key/P1/P2 secrecy and authentication on the two branch values. They do not establish that CV's complete key matches ATAi's at CV's earlier M6 acceptance. A completed normal execution reaches CV=2, ATAi=3, TA=2 and ATAj=1 with equal keys and two matching requests.

## Evidence

Exact goal declarations are in `declared_goals.json` and in the model sources. The verifier checks their equality before running the backends. Tool versions, commands, source/IF hashes and native results are captured automatically. Completed traces are checked for terminal states, equal keys, matching witness/request events and supported, satisfiable residual constraints.
