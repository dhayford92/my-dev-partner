import React, { useCallback, useState } from "react";
import {
  Dimensions,
  type LayoutChangeEvent,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import Animated, {
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from "react-native-reanimated";

interface ButtonSheetProps {
  onClose?: () => void;
  title?: string;
  children?: React.ReactNode;
}

const SPRING_CONFIG = { damping: 22, stiffness: 170 } as const;

/** The canonical modal/confirm primitive — mobile's equivalent of the web suite's Dialog. */
export function ButtonSheet({ onClose, title, children }: ButtonSheetProps) {
  const screenHeight = Dimensions.get("window").height;
  const translateY = useSharedValue(screenHeight);
  const overlayOpacity = useSharedValue(0);
  const [measured, setMeasured] = useState(false);

  const sheetStyle = useAnimatedStyle(() => ({ transform: [{ translateY: translateY.value }] }));
  const overlayStyle = useAnimatedStyle(() => ({ opacity: overlayOpacity.value }));

  const onContentLayout = useCallback(
    (e: LayoutChangeEvent) => {
      const h = e.nativeEvent.layout.height;
      if (!measured && h > 0) {
        setMeasured(true);
        translateY.value = withSpring(screenHeight - h, SPRING_CONFIG);
        overlayOpacity.value = withTiming(1, { duration: 200 });
      }
    },
    [measured, screenHeight, translateY, overlayOpacity],
  );

  const dismiss = useCallback(() => {
    translateY.value = withSpring(screenHeight, SPRING_CONFIG);
    overlayOpacity.value = withTiming(0, { duration: 150 }, (finished) => {
      if (finished && onClose) runOnJS(onClose)();
    });
  }, [screenHeight, translateY, overlayOpacity, onClose]);

  return (
    <>
      <Animated.View style={[styles.overlay, overlayStyle]}>
        <Pressable style={styles.flex} onPress={dismiss} />
      </Animated.View>
      <Animated.View style={[styles.sheet, sheetStyle]} onLayout={onContentLayout}>
        {title || onClose ? (
          <View className="flex-row items-center justify-between px-5 pt-5 pb-2">
            {title ? <Text className="text-[16px] font-semibold text-ink-900">{title}</Text> : <View />}
            {onClose ? (
              <Pressable onPress={dismiss} className="ml-auto rounded-full p-2">
                <Text className="text-[13px] font-semibold text-brandBlue-500">Close</Text>
              </Pressable>
            ) : null}
          </View>
        ) : null}
        <View className="px-5 pb-[80px] pt-2">{children}</View>
      </Animated.View>
    </>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 20,
    backgroundColor: "rgba(0,0,0,0.5)",
  },
  sheet: {
    position: "absolute",
    left: 0,
    right: 0,
    zIndex: 30,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    backgroundColor: "#F9FAFB",
  },
  flex: { flex: 1 },
});
