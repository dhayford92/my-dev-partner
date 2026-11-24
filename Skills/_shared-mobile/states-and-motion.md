# Loading States, Lists & Motion — Canonical (Mobile)

## Loading states — no shared kit exists today; build a minimal one

Unlike the web suite's `states.tsx`, **neither reference app has a shared `EmptyState`/`ErrorState`
kit** — loading/empty/error handling is ad hoc per screen (a `Skeleton` primitive exists in both,
feature-specific skeleton screens are hand-built per domain). The scaffold ships a minimal
`components/ui/states.tsx` (skeleton/empty/error) so new screens don't reinvent it, but don't
over-build — match the actual light-touch usage in the reference apps.

### `Skeleton` — confirmed identical shape in both apps

```tsx
function Skeleton({ className, ...props }: { className?: string } & ComponentPropsWithoutRef<typeof View>) {
  const fadeAnim = useRef(new Animated.Value(0.5)).current;
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(fadeAnim, { toValue: 1, duration: 1000, useNativeDriver: true }),
        Animated.timing(fadeAnim, { toValue: 0.5, duration: 1000, useNativeDriver: true }),
      ]),
    ).start();
  }, [fadeAnim]);
  return <Animated.View className={`rounded-md bg-gray-200 ${className ?? ""}`} style={{ opacity: fadeAnim }} {...props} />;
}
```

Feature-specific skeletons (e.g. `transaction-card-skeleton.tsx`) compose this primitive into the
real card's exact layout — same "match the loaded shape" rule as web.

### Which pattern where

| Context | Pattern |
|---------|---------|
| List/card content loading | `Skeleton`-based, shaped like the real row/card |
| Full-screen initial load (auth hydration, splash) | branded splash screen (logo + radial glow, `Reanimated.FadeIn`) — confirmed identical pattern in both apps' `app/index.tsx` |
| Button/mutation in flight | inline label swap (`loading ? "Please wait…" : label`) + `disabled` |
| Empty list | simple centered icon + text + optional action — build minimal, don't over-engineer |

No pull-to-refresh (`RefreshControl`) confirmed in either reference app — if a screen needs it, it's
new ground, not an extraction; add it deliberately per-screen rather than assuming it's standard.

## Lists — plain `FlatList`, not FlashList

**Neither app uses `@shopify/flash-list`.** Canonical is RN's built-in `FlatList` with standard
`keyExtractor`/`renderItem`; pagination via `onEndReached`/`onEndReachedThreshold` where a screen
needs infinite scroll. Don't introduce FlashList as a default dependency unless a specific screen's
list performance genuinely needs it — that's a deliberate per-screen call, not a blanket default.

## Motion — light and sparing, not a rich animation system

**The confirmed real convention is minimal, targeted use of Reanimated** — not pervasive motion.
Match this; don't invent a richer system than what's actually used:

- **`ButtonSheet`**: spring transform on open/close (`withSpring`, damping 22 / stiffness 170) +
  backdrop fade (`withTiming`, ~150-200ms). This is the one piece of "real" Reanimated work in
  both apps.
- **Splash/first-paint**: `Animated.View entering={FadeIn.duration(800)}` on the logo.
- **List entrance** (confirmed in one app, not the other — optional, not mandatory): staggered
  `Animated.View entering={FadeInDown.delay(index * 40).duration(300)}` on list rows for a
  reveal-on-mount feel. Use sparingly — a settings list or reason-picker, not a data table.

```tsx
import Animated, { FadeInDown } from "react-native-reanimated";
<Animated.View entering={FadeInDown.delay(index * 40).duration(300)}>{row}</Animated.View>
```

### Haptics — confirmed light touch, easy to over-build

```ts
import * as Haptics from "expo-haptics";
export function lightImpact() { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {}); }
export function selectionFeedback() { Haptics.selectionAsync().catch(() => {}); }
```

Two functions, used sparingly (selection/light-impact only), always `.catch(() => {})`-guarded
(haptics can throw on simulators/unsupported devices). One reference app has `expo-haptics`
installed with **zero real call sites** — don't treat "the dependency is present" as "haptics are
used everywhere." Add haptic feedback deliberately per-interaction (a toggle, a swipe-confirm), not
globally.

### Deliberately static

Forms, list content itself (rows appear via data change, not animated reflow), settings screens,
dense data views. Motion is for first-paint delight and the one bottom-sheet primitive — not
applied to data-dense interaction.

## Dark mode — not scaffolded by default

Per the owner's decision, `mobile-scaffold` ships **light-mode only**. Don't wire `useColorScheme`,
don't add a `dark-*` token scale, don't branch styling on color scheme, unless a specific project
asks for it (in which case follow the confirmed-mature pattern: `const { colorScheme } =
useColorScheme(); const isDark = colorScheme === "dark";` + a light/dark token pair in
`tailwind.config.js`, and set `darkMode: "class"`).
