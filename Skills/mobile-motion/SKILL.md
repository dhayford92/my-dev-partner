---
name: mobile-motion
description: Generate mobile loading states (skeleton vs native ActivityIndicator, pull-to-refresh, FlatList pagination) and animation/gesture code matching Denzel's actual light, sparing usage — Reanimated for the ButtonSheet primitive, splash entrance, and occasional staggered list-entrance; expo-haptics for selection/confirm feedback only. Not generic "add some motion." Use when adding a loading state, a list, or any entrance/confirm animation on mobile. Do not use for the data-fetching logic itself (mobile-data) or native capability code like push/biometrics (mobile-native).
---

# mobile-motion

Loading and motion, matched to what the reference apps actually do — which is **light and
targeted**, not a rich animation system. Rules and evidence in
[`../_shared-mobile/states-and-motion.md`](../_shared-mobile/states-and-motion.md); this skill is the generation
procedure on top of it.

## Loading states — pick by context, don't over-build

Neither reference app has a shared `EmptyState`/`ErrorState` kit beyond what `mobile-scaffold`
ships (`components/ui/states.tsx`) — keep it that minimal unless a screen has a real reason for
something richer.

| Context | Pattern |
|---------|---------|
| List/card content loading | `Skeleton`, shaped like the real row/card | 
| Full-screen initial load (auth hydration) | branded splash (`Reanimated.FadeIn` on the logo) |
| Button/mutation in flight | inline label swap (`"Please wait…"`) + `disabled` |
| A blocking async op with no meaningful skeleton shape | RN's built-in `ActivityIndicator` — plain, not styled into a custom spinner |
| Empty list | `EmptyState` — icon-free is fine; don't invent an illustration system |

```tsx
import { ActivityIndicator } from "react-native";
{isPending ? <ActivityIndicator size="small" color="#1F6F8B" /> : <Text>Submit</Text>}
```

Full skeleton template: [references/loading.md](references/loading.md).

## Lists — `FlatList`, pull-to-refresh, pagination

**Neither reference app uses `@shopify/flash-list` or `RefreshControl`.** Don't add either by
default — they're legitimate per-screen additions when a specific list is large/slow or a specific
product flow wants pull-to-refresh, but they are **new ground**, not an extraction. When a screen
does need them:

```tsx
<FlatList
  data={items}
  keyExtractor={(i) => i.id}
  renderItem={renderItem}
  refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={refetch} />}
  onEndReached={fetchNextPage}
  onEndReachedThreshold={0.4}
/>
```

Full patterns: [references/loading.md](references/loading.md#pull-to-refresh--pagination).

## Motion — the confirmed real usage (match this exactly, don't expand it)

1. **`ButtonSheet`** — the one piece of "real" Reanimated work in both apps: spring transform on
   open/close (`withSpring`, damping 22 / stiffness 170) + backdrop fade (`withTiming`,
   ~150-200ms). Full source in `mobile-scaffold/assets/components/ui/button-sheet.tsx`.
2. **Splash/first-paint** — `Animated.View entering={FadeIn.duration(800)}` on the logo, in the
   auth-gate loading state (`app/index.tsx`).
3. **List entrance** (confirmed in one reference app only — optional, not mandatory) — staggered
   `Animated.View entering={FadeInDown.delay(index * 40).duration(300)}` per row. Use for short,
   glanceable lists (a reason-picker, a settings list) — not a long data table.

```tsx
import Animated, { FadeInDown } from "react-native-reanimated";
{items.map((item, i) => (
  <Animated.View key={item.id} entering={FadeInDown.delay(i * 40).duration(300)}>
    <Row item={item} />
  </Animated.View>
))}
```

Full patterns: [references/motion-and-gestures.md](references/motion-and-gestures.md).

## Gesture-handler — installed for its required role, not for custom gestures

`react-native-gesture-handler` wraps the app root (`GestureHandlerRootView`, required by
`react-navigation`/Expo Router) and is occasionally used for its `ScrollView` re-export inside a
keyboard-heavy screen. **Neither reference app has a confirmed custom swipe-to-delete, pan, or
drag gesture.** Don't generate one as if it were an established convention — a swipe action is
legitimate new UI, build it deliberately per-screen if asked, using `Swipeable` or
`react-native-reanimated`'s gesture API, not because "gesture-handler is installed so it must be
used more."

## Haptics — two functions, sparing use

```ts
import * as Haptics from "expo-haptics";
export function lightImpact() { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {}); }
export function selectionFeedback() { Haptics.selectionAsync().catch(() => {}); }
```

Always `.catch(() => {})`-guarded (can throw on simulators). Use on a confirm-tap (destructive
action) or a meaningful selection change — not on every `Pressable`. One reference app has
`expo-haptics` installed with zero real call sites; "the dependency exists" is not evidence of an
established pattern to expand.

## Deliberately static

Forms, settings screens, dense data views, list row content itself (data changes, not animated
reflow). Motion is for first-paint delight and the one `ButtonSheet` primitive.

## Dark mode — not in scope for this skill by default

Per the owner's decision, `mobile-scaffold` ships light-mode only; this skill doesn't add
`useColorScheme`-driven styling unless the project has explicitly opted in (see
`../_shared-mobile/states-and-motion.md#dark-mode--not-scaffolded-by-default`).

## Verify

If a dev build/Expo Go is available: confirm a `ButtonSheet` opens/closes smoothly, a skeleton
matches the loaded layout (no shift), and any staggered list entrance doesn't re-trigger on
re-render (should be keyed correctly, not replaying on every parent update).
