# Interview guide

Ask these **grouped**, not one at a time. State the stack defaults up front and only probe where
the product diverges. Don't design until the answers are in. Don't invent product facts.

## Group 1 — Product & users
- What does the product do, in one sentence? What's the most important thing it must do well?
- Who uses it? List each persona and what they can do.
- Is this B2C, B2B, or multi-tenant SaaS? (Drives the **authz model**.)
- What's explicitly out of scope for v1?

## Group 2 — Core flows
- Walk me through the 3–7 flows that define the product (trigger → actors → happy path →
  failure). These become endpoints + background jobs.
- Which flows are real-time vs. can be async/deferred?
- Any flow involving money, KYC, or irreversible actions? (Needs idempotency + extra care.)

## Group 3 — Data
- What are the main entities and how do they relate?
- Anything expected to grow unbounded (events, logs, messages)?
- Any data that must be tenant-isolated at the DB level? (→ team + RLS.)
- Read-heavy or write-heavy? Any obvious hot query?

## Group 4 — Auth & access
- Login method(s): email+password, phone+OTP, OAuth?
- Do customers configure their own roles/permissions? (→ JSON RBAC.) Or fixed personas? (→
  persona guards.)
- Is there an admin portal separate from the app? (→ portal JWT.)
- Email verification / password reset required for v1?

## Group 5 — Integrations & jobs
- Third parties: payments? SMS? push? AI? KYC? file storage beyond Spaces?
- What must run on a schedule or in the background? (→ APScheduler jobs.)
- Which integrations are on the critical request path vs. fire-and-forget?

## Group 6 — Non-functional
- Expected scale (users, requests, data volume) now and at 10×?
- What does "production-ready" mean here — deployment target, uptime expectations?
- Any compliance/PII constraints (what data is sensitive, retention)?
- Caching needs / tolerances for staleness?

## Group 7 — Constraints & unknowns
- Frontend stack (shapes the API contract; default snake_case JSON).
- Any hard deadlines or fixed decisions already made?
- Anything about the product you're unsure of that I shouldn't assume?

## After the interview
Map answers onto the template sections, choose the authz + tenancy model deliberately (state the
trade-off), and list every unresolved item under **Open Questions**. Present the draft and walk
the owner through the API surface, schema, and auth model before it's considered done.
