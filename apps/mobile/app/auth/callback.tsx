import { useEffect } from "react";
import { useRouter } from "expo-router";

/**
 * chuchutreeapp://auth/callback 딥링크 처리용 라우트.
 * 실제 콜백 처리는 openAuthSessionAsync 가 가로채므로,
 * 만약 이 화면이 활성화되면 루트로 리다이렉트한다.
 */
export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/");
  }, []);

  return null;
}
