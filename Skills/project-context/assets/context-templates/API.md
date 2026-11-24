# API — {{PROJECT_NAME}}

> Endpoint inventory, contracts, and auth requirements. Must match the routers exactly.
> Update in the same task as any route change. `verify` mode diffs this against the routers.

## Conventions (canonical)
- URL: `/{domain}/api/v1/{persona}/{feature}`.
- Success `{message, data?}`; list `{data, current_page, page_limit, total_count}`; errors via
  `HTTPException` → `{detail}` + `X-Error-Code` header; snake_case, ISO-8601 UTC.

## Endpoints
<!-- Group by domain. Mark auth (public / client / admin / super_admin / portal*) + rate limit.
     "Consumed by" = the web page/hook and/or mobile screen/action that calls it, + the response
     type it maps to on each surface (leave blank if that surface doesn't exist for this project,
     or "—" if unused by a surface that does exist). Flag mismatches between what the backend
     returns and what a consuming surface expects — including a web-vs-mobile handling difference. -->

### users
| Method | Path | Auth | Rate limit | Purpose | Consumed by (web) | Consumed by (mobile) |
|--------|------|------|------------|---------|--------------------|------------------------|
| POST | `/users/api/v1/client/auth/login` | public | LOGIN | authenticate client | `loginAction` → login-form | `requestOTP` → welcome screen |
| | | | | | | |

### core
| Method | Path | Auth | Rate limit | Purpose | Consumed by (web) | Consumed by (mobile) |
|--------|------|------|------------|---------|--------------------|------------------------|
| | | | | | | |

### utils
| Method | Path | Auth | Rate limit | Purpose | Consumed by (web) | Consumed by (mobile) |
|--------|------|------|------------|---------|--------------------|------------------------|
| | | | | | | |

_Last updated: {{DATE}}_
