# Product motion — CSS keyframe utilities

Add to `app/globals.css` (after the token layers). Apply via className; stagger with inline
`animationDelay`. This is the product app's motion system — reach here before framer-motion.

```css
/* ── shared product animations ─────────────────────────────── */
@keyframes ly-fade-up   { from { opacity:0; transform:translateY(18px) } to { opacity:1; transform:translateY(0) } }
@keyframes ly-fade-in   { from { opacity:0 } to { opacity:1 } }
@keyframes ly-float     { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-8px) } }
@keyframes ly-glow-pulse{ 0%,100% { opacity:.2 } 50% { opacity:.55 } }
@keyframes ly-bar-grow  { from { transform:scaleY(0) } to { transform:scaleY(1) } }
@keyframes ly-progress  { from { width:0 } to { width:var(--ly-progress-w, 100%) } }
@keyframes ly-count-in  { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }

.animate-ly-fade-up    { animation: ly-fade-up    .5s ease both }
.animate-ly-fade-in    { animation: ly-fade-in    .4s ease both }
.animate-ly-float      { animation: ly-float      6s  ease-in-out infinite }
.animate-ly-glow-pulse { animation: ly-glow-pulse 3s  ease-in-out infinite }
.animate-ly-bar-grow   { animation: ly-bar-grow   .55s ease both; transform-origin: bottom }
.animate-ly-progress   { animation: ly-progress   1s  ease both }
.animate-ly-count-in   { animation: ly-count-in   .4s ease both }
```

## Usage

```tsx
// staggered header (from ResourcePageHeader)
<h1 className="animate-ly-count-in">{title}</h1>
<p className="animate-ly-count-in" style={{ animationDelay: "60ms" }}>{description}</p>

// content reveal on first render
<div className="animate-ly-fade-up">...</div>

// chart bars growing in
<rect className="animate-ly-bar-grow" style={{ animationDelay: `${i * 40}ms` }} />

// progress fill
<div className="animate-ly-progress" style={{ ["--ly-progress-w" as string]: `${pct}%` }} />
```

## Rules

- One-shot reveals use `both` fill so they don't flash pre-animation.
- Infinite animations (`ly-float`, `ly-glow-pulse`) only on decorative/ambient elements — never on
  interactive controls or anything the user reads while it moves.
- Wrap infinite/large motion in a reduced-motion guard:

```css
@media (prefers-reduced-motion: reduce) {
  .animate-ly-float, .animate-ly-glow-pulse { animation: none }
}
```
- Micro-interactions (hover, focus) use Tailwind `transition-*`, not keyframes.
