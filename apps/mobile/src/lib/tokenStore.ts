/**
 * WebView 쿠키 주입을 위한 in-memory 토큰 임시 저장소.
 *
 * Phase 1 구현 방식:
 *   로그인/세션 복원 후 seedCookies()가 여기에 토큰을 저장 →
 *   WebViewScreen이 injectedJavaScriptBeforeContentLoaded 로 document.cookie 에 주입.
 *
 * Phase 3 이후 교체 예정:
 *   BE의 /api/auth/mobile/exchange 가 Set-Cookie 헤더를 내려주면
 *   WebView를 그 엔드포인트로 이동시켜 서버 측에서 HttpOnly 쿠키를 심는 방식으로 변경.
 */

interface PendingTokens {
  access: string;
  refresh: string;
}

let pendingTokens: PendingTokens | null = null;

/** 로그인/세션 복원 후 WebView에 심을 토큰을 저장 */
export function setPendingTokens(access: string, refresh: string): void {
  pendingTokens = { access, refresh };
}

/** WebViewScreen이 1회 읽고 소비 (읽은 뒤 null 로 초기화) */
export function consumePendingTokens(): PendingTokens | null {
  const tokens = pendingTokens;
  pendingTokens = null;
  return tokens;
}
