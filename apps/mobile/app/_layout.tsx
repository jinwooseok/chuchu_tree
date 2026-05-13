import * as SplashScreen from "expo-splash-screen";
import { router, Stack } from "expo-router";
import { useEffect } from "react";
import { bootstrapSession } from "@/src/auth";

// WebView 첫 로드 완료 전까지 스플래시 유지
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  useEffect(() => {
    const init = async () => {
      try {
        const { authenticated } = await bootstrapSession();
        if (authenticated) {
          router.replace("/");       // WebView 화면
        } else {
          router.replace("/login");  // 로그인 게이트
        }
      } catch {
        router.replace("/login");
      } finally {
        // bootstrapSession 도중 WebView 가 먼저 뜰 경우를 대비한 fallback
        const timer = setTimeout(() => SplashScreen.hideAsync(), 5000);
        return () => clearTimeout(timer);
      }
    };

    init();
  }, []);

  return (
    <Stack screenOptions={{ headerShown: false }} />
  );
}
