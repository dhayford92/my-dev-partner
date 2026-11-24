# Marketing motion — framer-motion

Landing/marketing only. `"use client"` on any component using `motion`. Shared easing constant at
the top of the file.

```tsx
"use client";
import { motion, AnimatePresence } from "framer-motion";
const ease = [0.22, 0.61, 0.36, 1] as const;
```

## Entrance on mount (staggered)

```tsx
<motion.span initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease }}>badge</motion.span>
<motion.h1   initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.08, ease }}>heading</motion.h1>
<motion.p    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.18, ease }}>sub</motion.p>
```
Increase `delay` per element (~0.08–0.1 steps) for the cascade.

## Scroll-triggered (reveal once)

```tsx
<motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }} transition={{ duration: 0.6, ease }}>
  section content
</motion.div>
```

## Stagger children

```tsx
const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.5, ease } } };
<motion.ul variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}>
  {features.map((f) => <motion.li key={f.id} variants={item}>{f.title}</motion.li>)}
</motion.ul>
```

## Continuous "bob" (ambient float, after entrance)

```tsx
<motion.div animate={{ y: [0, -9, 0] }} transition={{ duration: 5, delay: 1.4, repeat: Infinity, ease: "easeInOut" }}>
  <FloatingCard />
</motion.div>
```

## Exit animation

```tsx
<AnimatePresence>
  {open && (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
      overlay
    </motion.div>
  )}
</AnimatePresence>
```

## Layout animation (reflow)

```tsx
<motion.div layout transition={{ duration: 0.25, ease }}>reorderable card</motion.div>
```

## Rules

- Hover/tap: prefer Tailwind (`hover:-translate-y-0.5 transition-all duration-200`); use
  `whileHover`/`whileTap` only when you need spring physics.
- `viewport={{ once: true }}` so scroll reveals don't replay.
- Respect reduced motion: gate large/infinite motion on
  `const reduce = useReducedMotion()` and fall back to opacity-only or static.
- Keep durations 0.5–0.8s for entrance, ≤0.25s for exits/layout. No motion on body text blocks.
