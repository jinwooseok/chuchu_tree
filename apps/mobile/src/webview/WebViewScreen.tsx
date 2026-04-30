import Constants from "expo-constants";
import * as SplashScreen from "expo-splash-screen";
import { useCallback, useRef } from "react";
import { BackHandler, Platform, StyleSheet, View } from "react-native";
import { useFocusEffect } from "expo-router";
import WebView, { type WebViewNavigation } from "react-native-webview";

const BASE_URL =
  (Constants.expoConfig?.extra?.webviewBaseUrl as string) ?? "https://chuchu-tree.duckdns.org";

export default function WebViewScreen() {
  const webViewRef = useRef<WebView>(null);
  const canGoBackRef = useRef(false);

  // Android 하드웨어 뒤로가기 처리
  useFocusEffect(
    useCallback(() => {
      if (Platform.OS !== "android") return;

      const onBackPress = () => {
        if (canGoBackRef.current) {
          webViewRef.current?.goBack();
          return true; // 기본 동작(앱 종료) 차단
        }
        return false; // 기본 동작 허용
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
        // iOS: WKWebView 쿠키 저장소 통합
        sharedCookiesEnabled={true}
        thirdPartyCookiesEnabled={true}
        // 미디어 인라인 재생 허용 (향후 카메라 등 대비)
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
