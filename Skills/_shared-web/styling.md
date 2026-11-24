# Styling — Canonical

## Tailwind v4, CSS-first (`app/globals.css`)

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  /* ...map every token var; radius scale: */
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}
```

- **Design tokens are oklch** in `:root` (light) and `.dark` (dark), covering
  `background/foreground/card/popover/primary/secondary/muted/accent/destructive/border/input/ring`,
  `chart-1..5`, `sidebar-*`, and `--radius` (default `0.625rem`).
- Base layer applies `border-border` + `bg-background text-foreground`; a thin custom scrollbar
  is themed to `--primary`.
- **Brand color is a placeholder** — the scaffold ships a neutral primary; swap the `--primary`
  oklch pair per project (e.g. amber). Everything else stays.

## Dark mode

`next-themes` via `ThemeProvider attribute="class" defaultTheme="light" enableSystem
disableTransitionOnChange`. Toggle stamps `.dark` on `<html>`; token vars flip. `sonner`'s
`<Toaster>` reads `useTheme()` so toasts follow the theme. Marketing sites may opt out of
`next-themes` and hand-roll a toggle (landing-only — do not template into product).

## shadcn config (`components.json`)

```json
{
  "style": "new-york",
  "rsc": true, "tsx": true,
  "tailwind": { "css": "app/globals.css", "baseColor": "stone", "cssVariables": true, "prefix": "" },
  "iconLibrary": "lucide",
  "aliases": { "components": "@/components", "ui": "@/components/ui", "lib": "@/lib", "utils": "@/lib/utils", "hooks": "@/hooks" }
}
```

Canonical: `new-york` / `stone`. (a project may use `radix-vega`/`stone` + extra registries; that's its
own choice, not the default.) Aliases are identical across all repos — keep them.

## Responsive & layout conventions

- Mobile-first Tailwind breakpoints; grids like `grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`.
- Content max-widths for forms/search (`max-w-sm`), centered marketing containers.
- Fonts via `next/font/google` wired to CSS vars (`--font-sans`, `--font-geist-mono`) on `<body>`.
- Prefer tokens (`bg-muted`, `text-muted-foreground`, `border-border`) over raw colors in product
  code. Raw hex is a marketing-site habit — keep it out of product components.
