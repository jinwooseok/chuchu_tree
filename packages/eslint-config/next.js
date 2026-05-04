import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import base from "./base.js";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  ...base,
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);
