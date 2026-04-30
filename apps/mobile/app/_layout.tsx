import * as SplashScreen from "expo-splash-screen";
import { Stack } from "expo-router";
import { useEffect } from "react";

// WebView 첫 로드 완료 전까지 스플래시 유지
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  useEffect(() => {
    // 혹시 WebView onLoadEnd 가 늦는 경우를 대비한 최대 대기 (5초)
    const timer = setTimeout(() => SplashScreen.hideAsync(), 5000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Stack screenOptions={{ headerShown: false }} />
  );
}
