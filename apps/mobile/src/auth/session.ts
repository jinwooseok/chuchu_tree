import Constants from "expo-constants";
import * as SecureStore from "expo-secure-store";
import CookieManager from "@react-native-cookies/cookies";

const BASE_URL =
  (Constants.expoConfig?.extra?.webviewBaseUrl as string) ??
  "https://chuchu-tree.duckdns.org";

const SECURE_STORE_KEY = "chuchutree_refresh_token";

// ─────────────────────────────────────────────
// 쿠키 심기
// ─────────────────────────────────────────────

/** access / refresh 토큰을 WebView 쿠키 저장소에 주입 */
export async function seedCookies(access: string, refresh: string) {
  const domain = new URL(BASE_URL).hostname;
  const isSecure = BASE_URL.startsWith("https");
  const expires = new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toUTCString(); // 7일

  await CookieManager.set(BASE_URL, {
    name: "access_token",
    value: access,
    domain,
    path: "/",
    secure: isSecure,
    httpOnly: true,
    expires,
  });

  await CookieManager.set(BASE_URL, {
    name: "refresh_token",
    value: refresh,
    domain,
    path: "/",
    secure: isSecure,
    httpOnly: true,
    expires,
  });
}

// ─────────────────────────────────────────────
// 토큰 교환
// ─────────────────────────────────────────────

interface ExchangeResult {
  access: string;
  refresh: string;
  expires_in: number;
}

/** /api/auth/mobile/exchange 호출 → 토큰 수신 */
export async function exchange(
  code: string,
  codeVerifier: string,
): Promise<ExchangeResult> {
  const res = await fetch(`${BASE_URL}/api/auth/mobile/exchange`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, code_verifier: codeVerifier }),
  });

  if (!res.ok) {
    throw new Error(`exchange 실패: ${res.status}`);
  }

  return res.json() as Promise<ExchangeResult>;
}

// ─────────────────────────────────────────────
// SecureStore — refresh 토큰 관리
// ─────────────────────────────────────────────

export async function saveRefreshToken(token: string) {
  await SecureStore.setItemAsync(SECURE_STORE_KEY, token);
}

export async function loadRefreshToken(): Promise<string | null> {
  return SecureStore.getItemAsync(SECURE_STORE_KEY);
}

export async function clearRefreshToken() {
  await SecureStore.deleteItemAsync(SECURE_STORE_KEY);
}

// ─────────────────────────────────────────────
// Cold Start 부트스트랩
// ─────────────────────────────────────────────

interface BootstrapResult {
  /** true → 세션 복원 성공, WebView로 진입 가능 */
  authenticated: boolean;
}

/**
 * 앱 시작 시 SecureStore 의 refresh 토큰으로 세션을 복원한다.
 * - refresh 없음 → { authenticated: false } → 로그인 화면으로
 * - refresh 있음 → POST /api/refresh → 쿠키 재시드 → { authenticated: true }
 * - refresh 만료(401) → 토큰 삭제 → { authenticated: false }
 */
export async function bootstrapSession(): Promise<BootstrapResult> {
  const refresh = await loadRefreshToken();
  if (!refresh) return { authenticated: false };

  try {
    const res = await fetch(`${BASE_URL}/api/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (res.status === 401) {
      await clearRefreshToken();
      return { authenticated: false };
    }

    if (!res.ok) {
      // 네트워크 오류 등 — 일단 WebView 진입 시도 (쿠키가 살아있을 수도 있음)
      return { authenticated: true };
    }

    const data = (await res.json()) as {
      access: string;
      refresh: string;
      expires_in: number;
    };

    await saveRefreshToken(data.refresh);
    await seedCookies(data.access, data.refresh);

    return { authenticated: true };
  } catch {
    // 오프라인 등 — WebView 진입 시도
    return { authenticated: true };
  }
}
