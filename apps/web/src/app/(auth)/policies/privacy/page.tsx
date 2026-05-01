import PrivacyPolicyClient from './PrivacyPolicyClient';
import { promises as fs } from 'fs';
import path from 'path';

export default async function PrivacyPolicy() {
  const filePath = path.join(process.cwd(), 'src/app/(auth)/policies/privacy/개인정보처리방침ver01.md');
  const markdownContent = await fs.readFile(filePath, 'utf8');

  return <PrivacyPolicyClient markdownContent={markdownContent} />;
}
