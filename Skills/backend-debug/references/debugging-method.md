# The debugging method (in depth)

The six steps, with what each looks like done well. The discipline is the point — most wrong
fixes come from skipping step 1 or 3.

## 1. Establish what the code ACTUALLY does
- Reproduce the failure, or pin the exact failing line from the stack trace.
- State the observed behaviour as `inputs → actual output/error`, precisely. "It's broken" is
  not a statement of behaviour.
- Read the real code on the failing path. Ignore what the function is *named* and what a comment
  *claims*; note what the statements actually execute.
- Separate the symptom (where it blew up) from the behaviour (what went wrong).

> Example: "POST /client/auth/refresh returns 500. Trace ends at `jwt.decode` raising
> `JWTError: Invalid audience`. So: a valid-looking refresh token is being rejected at decode."

## 2. Trace to the true origin
- Walk backwards from the symptom through the call chain to the first point where reality
  diverges from what's required.
- The origin is usually **upstream** of the exception. A `NoneType` error at line 80 is a
  symptom; the bug is wherever that value was supposed to be set and wasn't.
- Cite `file:line` for the origin.

> Example: refresh tokens are minted with `aud=JWT_AUDIENCE` but `verify_token` decodes with a
> different `audience=` because the refresh path passes a stale setting. Origin: token creation,
> not the decode that threw.

## 3. Explain WHY, causally
- Answer "why is the state wrong *here*?" in terms of ordering, assumptions, or missing
  invariants — not just "the value is null."
- If you can't explain the mechanism, you don't have the cause yet; keep tracing.

> Example: the aud mismatch happens because two code paths were built at different times with
> different audience values; nothing enforces they agree. The invariant "issue-aud == verify-aud"
> is unstated and violated.

## 4. Enumerate hidden edge cases + adjacent bugs
- **Edge cases:** what other inputs/states hit this same flaw? (empty, null, expired, concurrent,
  first-run, large, unicode, timezone, missing config.)
- **Adjacent code paths:** search for the same pattern elsewhere — a copy-pasted check, the same
  missing guard, the same assumption. Backend bugs are often duplicated across the four
  personas/domains.
- A real fix addresses the class, not just the reported instance.

> Example: the same aud/iss decode appears in `get_current_user`, the OTP flow, and the portal
> guard — check all three, not just refresh.

## 5. Propose the most robust fix + state the trade-off
- Prefer the fix that makes the bad state unrepresentable or fails fast, over a local patch.
- **State the trade-off explicitly**: performance cost, added complexity, behaviour change,
  required migration, or reduced flexibility. A fix with no stated cost is under-analysed.
- If only a narrow/temporary patch is possible now, label it as such and name the real cause it
  leaves open.

> Example: centralise audience/issuer in one constant used by both mint and verify (robust,
> removes the class). Trade-off: touches every token call site; needs a redeploy; existing tokens
> keep working because the value is unchanged.

## 6. Verify
- Exercise the actual failing path and observe the corrected behaviour — not the diff, not a
  unit test of a different function. See [verification.md](verification.md).
- Confirm the edge cases from step 4 are handled.
- If verification isn't possible in the environment, say so and state exactly what still needs
  checking.

## Output shape
When you report a diagnosis, make the six steps legible: **what it does → true origin (file:line)
→ why (causal) → other affected paths → the fix + its trade-off → how it was verified.**
