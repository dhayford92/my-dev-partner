import React, { createContext, useContext, useRef, useState } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import Animated, { FadeIn, FadeOut, SlideInLeft, SlideOutRight } from "react-native-reanimated";
import { CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon, XMarkIcon } from "react-native-heroicons/solid";

type ToastType = "success" | "error" | "info";
type ToastAnimation = "fade" | "slide";

interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  animation?: ToastAnimation;
}

interface TosterContextValue {
  show: (msg: Omit<ToastMessage, "id">) => void;
}

const TosterContext = createContext<TosterContextValue | null>(null);

export function useToster(): TosterContextValue {
  const ctx = useContext(TosterContext);
  if (!ctx) throw new Error("useToster must be used within TosterProvider");
  return ctx;
}

const TYPE_STYLE: Record<ToastType, { bg: string; text: string; icon: string }> = {
  success: { bg: "#d1fae5", text: "#065f46", icon: "#10b981" },
  error: { bg: "#fee2e2", text: "#991b1b", icon: "#ef4444" },
  info: { bg: "#dbeafe", text: "#1e40af", icon: "#3b82f6" },
};

const ICON: Record<ToastType, React.ComponentType<{ color: string; size: number }>> = {
  success: ({ color, size }) => <CheckCircleIcon color={color} size={size} />,
  error: ({ color, size }) => <ExclamationCircleIcon color={color} size={size} />,
  info: ({ color, size }) => <InformationCircleIcon color={color} size={size} />,
};

export default function TosterProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<ToastMessage[]>([]);
  const timers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  const remove = (id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
    clearTimeout(timers.current[id]);
    delete timers.current[id];
  };

  const show = (msg: Omit<ToastMessage, "id">) => {
    const id = Math.random().toString(36).slice(2);
    setMessages((prev) => [{ ...msg, id }, ...prev]);
    timers.current[id] = setTimeout(() => remove(id), msg.duration ?? 3000);
  };

  return (
    <TosterContext.Provider value={{ show }}>
      {children}
      <View pointerEvents="box-none" style={StyleSheet.absoluteFill}>
        <View style={styles.stack}>
          {messages.map((msg) => {
            const style = TYPE_STYLE[msg.type];
            const Icon = ICON[msg.type];
            const anim = msg.animation === "slide"
              ? { entering: SlideInLeft, exiting: SlideOutRight }
              : { entering: FadeIn, exiting: FadeOut };
            return (
              <Animated.View
                key={msg.id}
                entering={anim.entering}
                exiting={anim.exiting}
                style={[styles.toast, { backgroundColor: style.bg }]}
              >
                <Icon color={style.icon} size={20} />
                <Text style={[styles.text, { color: style.text }]}>{msg.message}</Text>
                <TouchableOpacity onPress={() => remove(msg.id)} style={styles.closeBtn}>
                  <XMarkIcon color={style.text} size={18} />
                </TouchableOpacity>
              </Animated.View>
            );
          })}
        </View>
      </View>
    </TosterContext.Provider>
  );
}

const styles = StyleSheet.create({
  stack: { position: "absolute", top: 56, width: "100%", zIndex: 9999, alignItems: "center" },
  toast: {
    minWidth: "70%",
    maxWidth: "92%",
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    borderRadius: 10,
    padding: 12,
    margin: 8,
    elevation: 4,
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  text: { flex: 1, fontSize: 13, fontWeight: "500" },
  closeBtn: { padding: 4 },
});
