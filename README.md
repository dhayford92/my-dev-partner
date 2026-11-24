# my-dev-partner

A set of [Claude Code](https://claude.com/claude-code) skills for **full-stack developers**. They cover the backend API, the web frontend and the mobile app, plus a collaboration contract that makes Claude act like a careful engineering partner instead of a yes-machine.

The skills are opinionated. They encode one concrete stack and one set of conventions, so the code Claude generates is consistent from the first file to the last.

| Surface | Stack |
|---|---|
| Backend | FastAPI, Tortoise ORM, PostgreSQL, Aerich, JWT auth |
| Web | Next.js App Router, React 19, Tailwind v4, shadcn/ui, TanStack Query |
| Mobile | Expo Router, React Native, NativeWind, TanStack Query |

If your stack is different, treat these as a template to fork and adapt.

## What's inside

```
Skills/
├── dev-partner/          # How Claude collaborates + routes to the right skill
├── project-context/      # Keeps a living project PRD in .claude/context/
├── backend-*/            # 9 backend skills
├── frontend-*/           # 8 web skills
├── mobile-*/             # 9 mobile skills
├── _shared-backend/      # Backend conventions (read by the backend skills)
├── _shared-web/          # Web conventions
└── _shared-mobile/       # Mobile conventions
```

### Core

| Skill | What it does |
|---|---|
| `dev-partner` | The working agreement. Claude challenges wrong approaches, states assumptions, asks before structural decisions, weighs trade-offs and says "I don't know" instead of guessing. It also routes each task to the right skill below. |
| `project-context` | Creates and maintains `OVERVIEW`, `ARCHITECTURE`, `SCHEMA`, `API`, `DECISIONS` and `CHANGELOG` files under `.claude/context/`. It updates them in the same task that changes the code, and has a verify mode that audits them for drift. |

### Backend

| Skill | Use it to |
|---|---|
| `backend-architect` | Plan a system before any code is written. It interviews you and fills in the architecture template. |
| `backend-scaffold` | Bootstrap a new API project that boots and passes `/health` on first run. |
| `backend-api-design` | Design endpoints and generate route, controller, schema and service stubs. |
| `backend-database` | Design models and run safe migrations. |
| `backend-auth` | Build JWT auth, email verification, password reset and RBAC. |
| `backend-debug` | Find the root cause of a bug instead of patching the symptom. |
| `backend-review` | Review changes before you commit. Findings are grouped as blocking, should-fix or nitpick. |
| `backend-security` | Audit auth, permissions, injection surfaces and secrets handling. |
| `backend-reverse-engineer` | Map an inherited codebase as it was actually built, then plan a staged refactor. |

### Web frontend

| Skill | Use it to |
|---|---|
| `frontend-architect` | Plan pages, the component tree and data boundaries. |
| `frontend-scaffold` | Bootstrap a Next.js app with an authenticated shell. |
| `frontend-components` | Build components and forms in a consistent three-tier structure. |
| `frontend-data` | Build server actions, query and mutation hooks, and delete flows. |
| `frontend-motion` | Add loading states and animation appropriate to each surface. |
| `frontend-debug` | Root-cause UI, state and cache bugs. |
| `frontend-review` | Pre-commit review covering accessibility, performance and API-contract fit. |
| `frontend-reverse-engineer` | Audit an existing frontend and plan a refactor. |

### Mobile

| Skill | Use it to |
|---|---|
| `mobile-architect` | Plan screens, navigation, offline behavior and push notifications. |
| `mobile-scaffold` | Bootstrap an Expo Router app with auth, providers and EAS config. |
| `mobile-components` | Build screens, forms and reusable components. |
| `mobile-data` | Build service actions and query hooks that match the backend contract. |
| `mobile-native` | Handle push, biometrics, permissions, deep links and EAS Build and Update. |
| `mobile-motion` | Add loading states, Reanimated animation and haptics. |
| `mobile-debug` | Root-cause JS, native and platform-specific bugs. |
| `mobile-review` | Pre-commit review of mobile changes. |
| `mobile-reverse-engineer` | Audit an existing Expo app and plan a refactor. |

### Shared reference docs

Each area has a `_shared-*` folder holding the conventions the skills read from, such as the response contract, the database rules and the data-layer patterns. These are the single source of truth. Change a convention there and every skill picks it up.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Python 3.9+ for the scaffold, review, security and context scripts
- Git

## Installation

Claude Code loads skills from `~/.claude/skills/` (available in every project) or `<your-project>/.claude/skills/` (that project only).

**1. Clone the repo**

```bash
git clone https://github.com/dhayford92/my-dev-partner.git
cd my-dev-partner
```

**2. Copy the skills**

Copy everything inside `Skills/`, including the `_shared-*` folders. The skills link to them with relative paths, so they must sit beside the skills.

macOS / Linux / Git Bash:

```bash
mkdir -p ~/.claude/skills
cp -r Skills/* ~/.claude/skills/
```

Windows PowerShell:

```powershell
$dest = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item Skills\* $dest -Recurse -Force
```

To install into a single project instead, use `<your-project>/.claude/skills` as the destination.

**3. Restart Claude Code.** Run `/skills` to confirm they are listed.

You can skip the surfaces you don't use, for example the `mobile-*` skills and `_shared-mobile`. Always keep `dev-partner`, because it is the router.

## Usage

Most of the time you don't invoke skills by hand. `dev-partner` reads your request and picks the right one. You can also ask for one by name.

```text
> Plan the backend for an invoicing app            → backend-architect
> Scaffold the API project                         → backend-scaffold
> Add a /clients endpoint with pagination          → backend-api-design
> Add a "status" column to orders, safely          → backend-database
> The login flow returns 500 sometimes             → backend-debug
> Review my changes before I commit                → backend-review
> Build the customer list page with a create form  → frontend-components
> Add push notifications                           → mobile-native
```

### A typical new-project flow

1. **Plan:** `backend-architect`, then `frontend-architect` and `mobile-architect` as needed. The plan is written against one shared API surface.
2. **Scaffold:** `backend-scaffold`, `frontend-scaffold`, `mobile-scaffold`.
3. **Build:** `backend-api-design`, `backend-database` and `backend-auth` on the server, then `*-data` and `*-components` on the clients.
4. **Ship:** `*-review`, then `backend-security`.
5. **Throughout:** `project-context` keeps `.claude/context/` in sync with the code.

## Customizing

The conventions live in plain Markdown, so you can edit them to match your own stack.

- Edit the `_shared-*` docs to change the conventions.
- Edit a skill's `SKILL.md` to change when it triggers or how it behaves.
- Edit `assets/` templates to change the code that scaffolds and generators produce.
- Edit `Skills/backend-architect/assets/ARCHITECTURE_TEMPLATE.md` to change the architecture interview defaults.

## License

Add a license before publishing. [MIT](https://choosealicense.com/licenses/mit/) is a common choice for a project like this.
