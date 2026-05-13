import TermsOfServiceClient from './TermsOfServiceClient';
import { promises as fs } from 'fs';
import path from 'path';

export default async function TermsOfService() {
  const filePath = path.join(process.cwd(), 'src/app/(auth)/policies/terms-of-service/이용약관ver01.md');
  const markdownContent = await fs.readFile(filePath, 'utf8');

  return <TermsOfServiceClient markdownContent={markdownContent} />;
}
