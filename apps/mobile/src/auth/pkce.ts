import * as Crypto from "expo-crypto";

/** base64url 인코딩 (RFC 4648) */
const toBase64Url = (base64: string) =>
  base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");

/** PKCE code_verifier / code_challenge 생성 */
export async function generatePkce(): Promise<{
  codeVerifier: string;
  codeChallenge: string;
}> {
  // code_verifier: 32바이트 랜덤 → base64url (43자 이상)
  const randomBytes = Crypto.getRandomBytes(32);
  const codeVerifier = toBase64Url(
    btoa(String.fromCharCode(...randomBytes)),
  );

  // code_challenge: SHA-256(verifier) → base64url
  const digest = await Crypto.digestStringAsync(
    Crypto.CryptoDigestAlgorithm.SHA256,
    codeVerifier,
    { encoding: Crypto.CryptoEncoding.BASE64 },
  );
  const codeChallenge = toBase64Url(digest);

  return { codeVerifier, codeChallenge };
}
