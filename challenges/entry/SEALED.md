# Sealed challenge answers — commitment ledger

**Append-only (M12).** Each row commits to an expected answer before the challenge is posted. The plaintext and salt are
added in a later commit only after the challenge closes, so anyone can recompute the hash.

Commitment: `sha256("<ID>|<pinned commit>|<expected answer>|<salt>")`, UTF-8, with no trailing newline. Use a salt of
at least 16 random bytes in hex.

The sealer must be the owner, or a constructor who did not build the code under test. Claude never writes sealed
answers ([RECRUITMENT_PROTOCOL.md](../../RECRUITMENT_PROTOCOL.md) §6).

```
# compute on device (Termux):
printf '%s' 'PA-C6a|<commit>|<answer>|<salt>' | sha256sum
```

| ID | Kind (revealed at close) | Pinned commit | Commitment (SHA-256) | Sealed on | Sealed by | Closed / revealed |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

*No challenges are sealed yet.*
