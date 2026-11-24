---
name: frontend-debug
description: Debug a frontend bug to its true causal origin with discipline — establish what the component/hook actually does, reproduce and trace the failure (render bug, stale cache, race condition, state desync, hydration mismatch, effect loop, memory leak) to root cause, explain why it happens causally, enumerate every other place the same bug pattern likely hides, propose the most robust fix with its trade-offs, and verify the fix actually works before claiming success. Use for any misbehaving UI, data, or state — not for adding features (frontend-components/frontend-data) or broad audits (frontend-reverse-engineer).
---

# frontend-debug

Same discipline as `backend-debug`, applied to the frontend. **Find the true cause, don't
pattern-match a symptom.** Convention baseline: [`../_shared-web/`](../_shared-web/README.md).

## The method (do not skip steps)

### 1. Establish what the code ACTUALLY does

Read the component/hook and its data path before theorizing. State, in one paragraph, the real
behavior — props in, state transitions, effects, what renders when. Don't trust names or comments.
If you can't explain the current behavior, you can't fix it.

### 2. Reproduce & observe

Get a deterministic repro (inputs, route, auth state, timing). Observe with the real tools, not
guesses:
- `read_console_messages` / `preview_logs` for errors + warnings (React key/hydration/act
  warnings are signal).
- `read_network_requests` for the actual request/response (status, body, headers, timing) — is the
  bug in the data or the render?
- React DevTools-style reasoning: which state/prop changed, which effect fired, render count.

### 3. Trace to true origin

Follow the causal chain backward from the symptom to the first thing that's actually wrong. Common
frontend root causes (with their tells):

| Class | Tells | Usual root cause |
|-------|-------|------------------|
| Stale cache | UI shows old data after mutation | missing/incorrect `invalidateQueries`; wrong/inline query key |
| State desync | two sources of truth disagree | server state duplicated into `useState`; context not synced to props |
| Race condition | works slow, breaks fast; flicker | unguarded async in effect; no `cancelQueries`; out-of-order responses |
| Effect loop | infinite renders/requests | unstable deps (new object/array/fn each render) in `useEffect`/`useMemo` |
| Hydration mismatch | "content did not match" warning | `Date`/random/`window` in render; server vs client branch |
| Render bug | wrong value shown, key warnings | derived state not recomputed; non-stable `key`; stale closure |
| Auth/refresh | random 401s, redirect loops | token expiry handling; middleware vs client refresh; cookie flags |

Name the class, then point to the exact line that is the origin — not where it surfaces.

### 4. Explain WHY (causally)

Write the mechanism: "X renders with a new `filters` object each time → `useQuery` sees a new key →
refetch → parent re-renders → new object … loop." If you can't state the mechanism, you haven't
found the cause yet.

### 5. Enumerate other occurrences

The same bug pattern rarely lives alone. Grep the codebase for the pattern (e.g. other inline
query keys, other effects with object deps, other server-state-copied-to-useState) and list every
site at risk. Fixing one and leaving five is a failure.

### 6. Propose the most robust fix + trade-offs

Prefer the fix that removes the class of bug, not the one that silences this instance. State
trade-offs honestly (e.g. "lifting state fixes the desync but re-renders the list; memoize the row"
). If there's a quick patch vs a correct fix, present both and recommend.

### 7. Verify — never claim it works without proof

Apply the fix, then **exercise the actual flow** and observe it's fixed: reproduce the original
repro and confirm the symptom is gone AND no new console/network errors appear. Use the preview
tools. If you can't verify (no repro env), say so explicitly and state what verification is
pending — do not assert success.

## Anti-patterns

- "Try this and see" without a root-cause explanation.
- Adding `key={Math.random()}`, `staleTime: 0` everywhere, or `eslint-disable
  react-hooks/exhaustive-deps` to mask a dependency bug.
- Fixing the one reported site and skipping step 5.
- Declaring victory off a type-check alone — that's not a runtime verification.

## Reference

Symptom→cause playbook with diagnosis snippets:
[references/failure-classes.md](references/failure-classes.md).
