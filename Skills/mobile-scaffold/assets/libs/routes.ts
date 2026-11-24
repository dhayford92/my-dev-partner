// Central place for route strings; typed routes are enabled (experiments.typedRoutes in app.json).
export const ROUTES = {
  AUTH: {
    WELCOME: "/(auth)/welcome",
    OTP: "/(auth)/otp",
  },
  HOME: {
    ROOT: "/(tabs)/home",
  },
} as const;
