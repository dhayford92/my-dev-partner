# Motion & gesture templates (mobile) — generate exactly this much, no more

## `ButtonSheet` spring (the confirmed real Reanimated usage)

Full component: `../../mobile-scaffold/assets/components/ui/button-sheet.tsx`. Key values worth
preserving exactly (confirmed in both reference apps):

```ts
const SPRING_CONFIG = { damping: 22, stiffness: 170 } as const;
// open: translateY.value = withSpring(screenHeight - measuredHeight, SPRING_CONFIG);
//       overlayOpacity.value = withTiming(1, { duration: 200 });
// close: translateY.value = withSpring(screenHeight, SPRING_CONFIG);
//        overlayOpacity.value = withTiming(0, { duration: 150 }, (finished) => finished && runOnJS(onClose)());
```

The sheet self-measures via `onLayout` rather than a fixed height — don't hardcode a sheet height.

## Splash / first-paint entrance

```tsx
<Animated.View entering={FadeIn.duration(800)} className="items-center">
  <Image source={logo} style={{ width: 200, height: 200 }} resizeMode="contain" />
</Animated.View>
```

Optional subtitle, delayed slightly behind the logo (confirmed in one reference app):

```tsx
<Animated.Text entering={FadeInDown.delay(400).duration(600)} className="mt-2 text-white/60">
  Your tagline here
</Animated.Text>
```

## Staggered list entrance (optional — confirmed in one app, not mandatory)

```tsx
{reasons.map((reason, index) => (
  <Animated.View key={reason} entering={FadeInDown.delay(index * 40).duration(300)}>
    <ReasonRow reason={reason} />
  </Animated.View>
))}
```

Use for short, glanceable lists rendered once (a picker, a settings screen) — not for a `FlatList`
of dozens/hundreds of rows (Reanimated `entering` animations on every `FlatList` item re-mount can
hurt scroll performance; `FlatList` already virtualizes, don't fight that with per-item mount
animations on a long list).

## Haptics call sites

```ts
// on a destructive confirm tap:
onPress={() => { selectionFeedback(); deleteMutation.mutate(); }}

// on a meaningful toggle/selection (e.g. picking a reason, selecting a tab):
onPress={() => { selectionFeedback(); setSelected(option); }}
```

Do not add haptics to: form field focus, generic button presses, navigation taps. That's not the
confirmed pattern — it's over-application.

## Gesture-handler — what's actually confirmed

```tsx
// app/_layout.tsx — required root wrapper, not itself a "gesture" in the animation sense:
<GestureHandlerRootView style={{ flex: 1 }}>
  <Stack ... />
</GestureHandlerRootView>
```

```tsx
// occasional re-export usage inside a keyboard-heavy screen (confirmed in one reference app):
import { ScrollView } from "react-native-gesture-handler";
```

**No confirmed custom `PanGestureHandler`, `Swipeable`, or drag-to-dismiss gesture in either
reference app.** If a product need calls for swipe-to-delete or a draggable sheet, build it
deliberately (e.g. `react-native-gesture-handler`'s `Swipeable` wrapping a `FlatList` row, or
Reanimated's `Gesture.Pan()` API) and document it as new, not as "the existing gesture pattern."
