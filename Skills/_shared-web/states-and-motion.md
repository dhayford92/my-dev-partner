# Loading States, Empty/Error States & Motion — Canonical

## The shared state kit — `components/ui/states.tsx`

One file, named exports, used everywhere. Do not reinvent per feature.

- `LoadingState` — `variant: "spinner" | "skeleton" | "dots"`, `skeletonCount`, `message`.
- `EmptyState` — icon + title + description + optional `action`.
- `ErrorState` — title + `error` (Error|string) + optional `retry`.
- `NotFoundState` — EmptyState preset for missing resources.
- `CardSkeleton`, `TableRowSkeleton`, `ListSkeleton` — shaped placeholders.

All built on shadcn `Skeleton` + `Button` + lucide icons + `cn()`. (Full implementation:
`app/components/ui/states.tsx` — regenerate verbatim; it is stable.)

## Which loading pattern where (the rule)

| Context | Pattern |
|---------|---------|
| List / grid / detail content loading | **Skeleton** matching the final layout (`CardSkeleton`, `ListSkeleton`, or a bespoke `*-loading-screen.tsx`) |
| Full-screen / route-blocking load | **Spinner** (`LoadingState variant="spinner"`) |
| Button / form / mutation in flight | **Inline** — swap button label ("Saving…") + `disabled`, no spinner overlay |
| Small inline async (badge, count) | `dots` or a tiny spinner |

- Query gating: `query.isLoading` → skeleton; `query.isError` → `ErrorState`/error screen with
  `retry`; empty data → `EmptyState`; else content. Mutations add `isPending` to the busy check.
- **No App Router `loading.tsx` / Suspense boundaries** — loading is handled in-component off
  `isLoading`/`isPending`. (Route-level `error.tsx`/`not-found.tsx` DO exist per scaffold.)

## Motion — context-scoped

Motion is **deliberately scoped by surface**. Do not add motion generically.

### Marketing surfaces → framer-motion

Entrance + scroll choreography only. Shared easing constant, staggered delays, optional infinite
"bob" loops; hover via Tailwind. Example (`app/components/Hero.tsx`):

```tsx
const ease = [0.22, 0.61, 0.36, 1] as const;
<motion.h1 initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 0.7, delay: 0.08, ease }}>...</motion.h1>
// hover: className="hover:-translate-y-0.5 transition-all duration-200"
```

Only `framer-motion` here; product apps do NOT install it.

### Product surfaces → CSS keyframes

Subtle product motion uses **CSS keyframe utilities** in `globals.css`, not framer-motion
(a product app may use framer in exactly one file). Reusable `@keyframes` + `.animate-*` utilities:

```css
@keyframes ly-fade-up { from { opacity:0; transform:translateY(18px) } to { opacity:1; transform:translateY(0) } }
@keyframes ly-float   { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-8px) } }
.animate-ly-fade-up { animation: ly-fade-up .5s ease both }
.animate-ly-float   { animation: ly-float 6s ease-in-out infinite }
```

Plus `tw-animate-css` for utility transitions, and the built-in `animate-spin`/`animate-bounce`
used by `states.tsx`.

### Admin surfaces → essentially static

An admin console may install no motion library. Tables, filters, dialogs, forms animate only
via default Radix open/close transitions + `tw-animate-css`.

### Deliberately static everywhere

Tables, data grids, form fields, dialogs' inner content, navigation. Motion is for first-paint
delight on marketing and small product micro-interactions — never on data-dense interaction.
