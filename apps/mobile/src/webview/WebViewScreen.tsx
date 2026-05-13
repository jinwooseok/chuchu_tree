import Constants from "expo-constants";
import * as SplashScreen from "expo-splash-screen";
import { useCallback, useEffect, useRef, useState } from "react";
import { BackHandler, Platform, StyleSheet, View } from "react-native";
import { useFocusEffect } from "expo-router";
import WebView, { type WebViewNavigation } from "react-native-webview";
import { consumePendingTokens } from "../lib/tokenStore";

const BASE_URL =
  (Constants.expoConfig?.extra?.webviewBaseUrl as string) ?? "https://chuchu-tree.duckdns.org";

/**
 * 토큰을 document.cookie 에 주입하는 JS 스크립트를 생성한다.
 *
 * [Phase 1 임시 구현] — HttpOnly 불가 (JS 주입 방식의 한계)
 * Phase 3에서 BE Set-Cookie 방식으로 교체 예정.
 */
function buildCookieScript(access: string, refresh: string): string {
  const domain = new URL(BASE_URL).hostname;
  // JSON.stringify로 토큰 값 이스케이프 처리
  return `
    (function() {
      var a = ${JSON.stringify(access)};
      var r = ${JSON.stringify(refresh)};
      var d = ${JSON.stringify(domain)};
      var opts = '; path=/; domain=' + d + '; SameSite=Strict';
      document.cookie = 'access_token='  + a + opts;
      document.cookie = 'refresh_token=' + r + opts;
    })();
    true;
  `;
}

export default function WebViewScreen() {
  const webViewRef = useRef<WebView>(null);
  const canGoBackRef = useRef(false);
  const [cookieScript, setCookieScript] = useState<string | undefined>();

  // 로그인/세션 복원 후 저장된 토큰을 1회 소비해 쿠키 주입 스크립트 준비
  useEffect(() => {
    const tokens = consumePendingTokens();
    if (tokens) {
      setCookieScript(buildCookieScript(tokens.access, tokens.refresh));
    }
  }, []);

  // Android 하드웨어 뒤로가기 처리
  useFocusEffect(
    useCallback(() => {
      if (Platform.OS !== "android") return;

      const onBackPress = () => {
        if (canGoBackRef.current) {
          webViewRef.current?.goBack();
          return true;
        }
        return false;
      };

      const subscription = BackHandler.addEventListener("hardwareBackPress", onBackPress);
      return () => subscription.remove();
    }, []),
  );

  const handleNavigationStateChange = (navState: WebViewNavigation) => {
    canGoBackRef.current = navState.canGoBack;
  };

  const handleLoadEnd = () => {
    SplashScreen.hideAsync();
  };

  return (
    <View style={styles.container}>
      <WebView
        ref={webViewRef}
        source={{ uri: BASE_URL }}
        style={styles.webview}
        onNavigationStateChange={handleNavigationStateChange}
        onLoadEnd={handleLoadEnd}
        injectedJavaScriptBeforeContentLoaded={cookieScript}
        sharedCookiesEnabled={true}
        thirdPartyCookiesEnabled={true}
        allowsInlineMediaPlayback={true}
        mediaPlaybackRequiresUserAction={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
  },
  webview: {
    flex: 1,
  },
});
