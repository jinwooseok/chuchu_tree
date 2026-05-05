import Constants from "expo-constants";
import * as WebBrowser from "expo-web-browser";
import { generatePkce } from "./pkce";
import { exchange, saveRefreshToken, seedCookies } from "./session";

const BASE_URL =
  (Constants.expoConfig?.extra?.webviewBaseUrl as string) ??
  "https://chuchu-tree.duckdns.org";

export type OAuthProvider = "naver" | "kakao" | "google" | "github";

export interface AuthResult {
  success: boolean;
  error?: string;
}

/**
 * 소셜 OAuth 로그인 전체 흐름:
 * 1. PKCE 생성
 * 2. GET /api/auth/mobile/start/{provider} → 소셜 OAuth 페이지 URL 획득
 * 3. 인앱 브라우저(ASWebAuthSession / Chrome Custom Tabs) 로 열기
 * 4. chuchutreeapp://auth/callback?code=... 콜백 수신
 * 5. POST /api/auth/mobile/exchange → 토큰 수신
 * 6. SecureStore + 쿠키 저장
 */
export async function startMobileAuth(provider: OAuthProvider): Promise<AuthResult> {
  try {
    const { codeVerifier, codeChallenge } = await generatePkce();

    // ── 1. 서버에서 소셜 OAuth URL 받기 ──────────────────────────────
    const startUrl =
      `${BASE_URL}/api/v1/auth/mobile/start/${provider.toUpperCase()}` +
      `?code_challenge=${encodeURIComponent(codeChallenge)}` +
      `&code_challenge_method=S256`;

    const startRes = await fetch(startUrl, { method: "GET" });
    if (!startRes.ok) {
      throw new Error(`OAuth 시작 실패: ${startRes.status}`);
    }

    // 서버가 302 리다이렉트 → fetch 가 따라감. 최종 URL 이 소셜 인증 페이지.
    const authUrl = startRes.url;

    // ── 2. 인앱 브라우저 열기 ────────────────────────────────────────
    // redirectUrl: 앱 스킴 chuchutreeapp://auth/callback
    const redirectUrl = "chuchutreeapp://auth/callback";

    const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);

    if (result.type !== "success" || !result.url) {
      return { success: false, error: "사용자가 로그인을 취소했습니다." };
    }

    // ── 3. 콜백 URL 에서 code 파싱 ──────────────────────────────────
    const callbackUrl = new URL(result.url);
    const appCode = callbackUrl.searchParams.get("code");
    if (!appCode) {
      return { success: false, error: "콜백 code 가 없습니다." };
    }

    // ── 4. 토큰 교환 ────────────────────────────────────────────────
    const tokens = await exchange(appCode, codeVerifier);

    // ── 5. 저장 ─────────────────────────────────────────────────────
    await saveRefreshToken(tokens.refresh);
    await seedCookies(tokens.access, tokens.refresh);

    return { success: true };
  } catch (err) {
    const message = err instanceof Error ? err.message : "알 수 없는 오류";
    return { success: false, error: message };
  }
}
