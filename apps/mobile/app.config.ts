import type { ConfigContext, ExpoConfig } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => {
  const isDev = process.env.APP_ENV === "dev";

  return {
    ...config,
    name: isDev ? "ChuChuTree (dev)" : "ChuChuTree",
    slug: "chuchutree",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/images/icon.png",
    scheme: "chuchutreeapp",
    userInterfaceStyle: "automatic",
    ios: {
      supportsTablet: true,
      bundleIdentifier: isDev ? "com.chuchutree.app.dev" : "com.chuchutree.app",
    },
    android: {
      package: isDev ? "com.chuchutree.app.dev" : "com.chuchutree.app",
      adaptiveIcon: {
        backgroundColor: "#E6F4FE",
        foregroundImage: "./assets/images/android-icon-foreground.png",
        backgroundImage: "./assets/images/android-icon-background.png",
        monochromeImage: "./assets/images/android-icon-monochrome.png",
      },
      predictiveBackGestureEnabled: false,
    },
    web: {
      output: "static",
      favicon: "./assets/images/favicon.png",
    },
    plugins: [
      "expo-router",
      "expo-dev-client",
      "expo-secure-store",
      [
        "expo-splash-screen",
        {
          image: "./assets/images/splash-icon.png",
          imageWidth: 200,
          resizeMode: "contain",
          backgroundColor: "#ffffff",
          dark: {
            backgroundColor: "#000000",
          },
        },
      ],
    ],
    experiments: {
      typedRoutes: true,
      reactCompiler: true,
    },
    extra: {
      webviewBaseUrl: isDev
        ? "https://chuchu-tree-dev.duckdns.org"
        : "https://chuchu-tree.duckdns.org",
    },
  };
};
