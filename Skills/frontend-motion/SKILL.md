---
name: frontend-motion
description: Generate loading-state and animation code that matches Denzel's actual usage — the right loading pattern per context (skeleton vs spinner vs inline vs suspense) and motion scoped by surface (framer-motion for marketing entrance/scroll, CSS keyframe utilities for subtle product motion, essentially static for admin/data-dense UI), including what to deliberately leave static. Use when adding loading states, skeletons, entrance/hover/layout animation, or a marketing section with motion. Not generic "add some motion" — every output follows the existing per-surface rules.
---

# frontend-motion

Loading and motion, done the way this codebase actually does it. The rules and rationale are in
[`../_shared-web/states-and-motion.md`](../_shared-web/states-and-motion.md) — read it; this skill is the
generation procedure.

## First: which surface are you on?

Motion is **scoped by surface**. Decide this before writing anything.

| Surface | Motion approach | Library |
|---------|-----------------|---------|
| Marketing / landing | entrance + scroll choreography, hover lift | **framer-motion** |
| Product (portal) | subtle fades/floats via reusable CSS utilities | **CSS keyframes** (`ly-*`) + `tw-animate-css` |
| Admin / data-dense | essentially static; Radix open/close only | none |

Do not install framer-motion into a product/admin app. Do not add framer choreography to tables,
forms, or data views anywhere.

## Loading states — pick by context

Use `components/ui/states.tsx` (never reinvent). Rule:

| Context | Pattern | Code |
|---------|---------|------|
| List/grid/detail content | **skeleton** matching final layout | `<LoadingState variant="skeleton" />`, `CardSkeleton`, `ListSkeleton`, or bespoke `*-loading-screen.tsx` |
| Full-screen / route-blocking | **spinner** | `<LoadingState variant="spinner" />` |
| Button / form / mutation | **inline** label swap + disabled | `{isPending ? "Saving..." : "Save"}` |
| Tiny inline async | dots | `<LoadingState variant="dots" />` |

Gate off the query: `isLoading` → skeleton, `isError` → `ErrorState` (retry), empty → `EmptyState`.
No App Router `loading.tsx`/Suspense — handle in-component. Build skeletons that mirror the real
layout (same grid, same rough sizes) so there's no layout shift. Templates:
[references/loading.md](references/loading.md).

## Product motion — CSS keyframe utilities

Add reusable `@keyframes` + `.animate-*` classes to `globals.css`; apply via className. This is
how the product app animates (framer appears in ~1 file). Standard set:

```css
@keyframes ly-fade-up { from { opacity:0; transform:translateY(18px) } to { opacity:1; transform:translateY(0) } }
@keyframes ly-fade-in { from { opacity:0 } to { opacity:1 } }
@keyframes ly-float   { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-8px) } }
@keyframes ly-count-in{ from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
.animate-ly-fade-up  { animation: ly-fade-up  .5s ease both }
.animate-ly-fade-in  { animation: ly-fade-in  .4s ease both }
.animate-ly-float    { animation: ly-float    6s ease-in-out infinite }
.animate-ly-count-in { animation: ly-count-in .4s ease both }
```

Stagger with inline `style={{ animationDelay: "60ms" }}`. Used e.g. in `ResourcePageHeader`
(title `animate-ly-count-in`, description delayed 60ms). Full set:
[references/product-motion.md](references/product-motion.md).

## Marketing motion — framer-motion

Entrance on mount, staggered by `delay`, shared easing constant; optional infinite "bob"; hover
via Tailwind. Example (`app/components/Hero.tsx`):

```tsx
"use client";
import { motion } from "framer-motion";
const ease = [0.22, 0.61, 0.36, 1] as const;

<motion.h1 initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 0.7, delay: 0.08, ease }}>...</motion.h1>

// continuous bob after entrance:
<motion.div animate={{ y: [0, -9, 0] }} transition={{ duration: 5, delay: 1.4, repeat: Infinity, ease: "easeInOut" }}>...</motion.div>

// hover: Tailwind, not framer
className="hover:-translate-y-0.5 transition-all duration-200"
```

Scroll-triggered: `whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}`. Full patterns
(entrance, exit via `AnimatePresence`, layout, stagger children):
[references/marketing-motion.md](references/marketing-motion.md).

## Deliberately static — do NOT animate

Tables, data grids, form fields, dialog inner content, nav items, list rows on data change.
Motion here reads as jank on data-dense interaction. Loading uses skeletons, not animated
entrances. Respect `prefers-reduced-motion` for any infinite/large motion.

## Verify

If previewable, confirm: skeletons match the loaded layout (no shift), entrance animations play
once and don't re-trigger on re-render, infinite loops don't thrash, and reduced-motion is
honored. Screenshot marketing motion mid- and post-entrance.
