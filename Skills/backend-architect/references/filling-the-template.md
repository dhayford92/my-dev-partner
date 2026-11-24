# Filling the template

How to complete each section of `../assets/ARCHITECTURE_TEMPLATE.md`. Keep the pre-filled defaults
unless the product needs otherwise; record any deviation under Open Questions (→ future ADR).

| § | Section | What good looks like | Default to keep |
|---|---------|----------------------|-----------------|
| 0 | Snapshot | one-paragraph "what + who + the one thing" | — |
| 1 | Problem statement | the problem, why now, explicit non-goals | — |
| 2 | Users & roles | persona table → `user_type` + **authz model chosen** | persona guards |
| 3 | Core flows | 3–7 flows: trigger/actors/happy/failure | — |
| 4 | Components | in-process (3 sub-apps + services) vs external | 1 app, `/users`+`/core`+`/utils` |
| 5 | Data flow | trace the primary flow incl. async side-effects | — |
| 6 | API surface | endpoint table, `/{domain}/api/v1/{persona}/{feature}` | canonical envelopes |
| 7 | Database schema | tables/columns/relations/indexes (described, not coded) | UUID PK, soft delete, timestamps |
| 8 | Auth model | tokens/lifetime, flows, persona/permission model | JWT 60m + 30d refresh + denylist |
| 9 | Caching | what/where/TTL/invalidation (Redis) | denylist + rate-limit only |
| 10 | Background jobs | job table: trigger/cadence/does/failure | APScheduler |
| 11 | Integrations | provider/purpose/secrets/critical-path/failure | Resend + Spaces |
| 12 | Error & logging | ErrorCodes needed, activity events, PII to redact | HTTPException `{detail}`+X-Error-Code |
| 13 | Scaling | the likely first bottleneck + first mitigation | — |
| 14 | Security | auth boundaries, injection, secrets, PII, webhooks | rate-limit auth, validate input |
| 15 | Deployment | environments, process model, migrations, secrets | bare-metal uvicorn |
| 16 | Open questions | everything undecided/assumed = risks | — |

## Depth guidance
- **API surface (§6):** list every endpoint you can foresee with method, path, persona/auth,
  and purpose. Don't write handler code — this is the contract, not the implementation.
- **Schema (§7):** describe columns, types, relations, indexes, and unique constraints in prose
  or tables. UUID PK, snake_case plural tables, timestamps + soft delete are assumed.
- **Auth model (§8):** commit to persona guards / JSON RBAC / team+RLS and say why (§2 signal).
  Note any second token type (OTP, portal, invite).
- **Caching (§9) & jobs (§10):** for each, name the invalidation trigger / failure behaviour —
  a cache with no invalidation plan or a job with no failure plan is a bug in waiting.
- **Scaling (§13):** one honest bottleneck beats a generic list. Usually: DB connections, an
  unbounded table (activity/events), a synchronous external call, or the single-process
  scheduler.

## The doc is a contract, not code
Reviewers should be able to build from it. If a section can't be filled without inventing a
product fact, that's an interview gap — go back and ask, don't guess. Unresolved items live in
§16 and block the build until answered.

## Hand-off
When the doc is approved:
- `backend-scaffold` reads §4/§8/§11/§15 to bootstrap.
- `backend-database` reads §7.
- `backend-api-design` reads §6.
- `project-context` copies the settled design into `.claude/context/ARCHITECTURE.md` and the key
  choices into `DECISIONS.md`.
