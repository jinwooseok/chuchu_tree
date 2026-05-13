import { router } from "expo-router";
import { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { startMobileAuth, type OAuthProvider } from "@/src/auth";

const PROVIDERS: { id: OAuthProvider; label: string; color: string }[] = [
  { id: "naver", label: "네이버로 로그인", color: "#03C75A" },
  { id: "kakao", label: "카카오로 로그인", color: "#FEE500" },
  { id: "google", label: "Google로 로그인", color: "#4285F4" },
  { id: "github", label: "GitHub로 로그인", color: "#24292E" },
];

export default function LoginScreen() {
  const [loading, setLoading] = useState<OAuthProvider | null>(null);

  const handleLogin = async (provider: OAuthProvider) => {
    setLoading(provider);
    try {
      const result = await startMobileAuth(provider);
      if (result.success) {
        router.replace("/");
      } else {
        Alert.alert("로그인 실패", result.error ?? "다시 시도해 주세요.");
      }
    } finally {
      setLoading(null);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ChuChuTree</Text>
      <Text style={styles.subtitle}>알고리즘 문제 풀이 학습</Text>

      <View style={styles.buttonGroup}>
        {PROVIDERS.map(({ id, label, color }) => (
          <TouchableOpacity
            key={id}
            style={[styles.button, { backgroundColor: color }]}
            onPress={() => handleLogin(id)}
            disabled={loading !== null}
          >
            {loading === id ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={[styles.buttonText, id === "kakao" && styles.kakaoText]}>
                {label}
              </Text>
            )}
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#ffffff",
    padding: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    marginBottom: 8,
    color: "#1a1a1a",
  },
  subtitle: {
    fontSize: 16,
    color: "#666666",
    marginBottom: 48,
  },
  buttonGroup: {
    width: "100%",
    gap: 12,
  },
  button: {
    height: 52,
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
  },
  buttonText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#ffffff",
  },
  kakaoText: {
    color: "#1a1a1a",
  },
});
