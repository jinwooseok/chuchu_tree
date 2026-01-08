import { TargetCode } from './tagSystem';

export const TARGET_OPTIONS = [
  {
    code: 'BEGINNER' as TargetCode,
    label: '입문자',
    description: '알고리즘을 이제 막 시작한 초보자',
  },
  {
    code: 'DAILY' as TargetCode,
    label: '데일리',
    description: '1일 1알고리즘, 점수 올리기, 취미 등',
  },
  {
    code: 'CT' as TargetCode,
    label: '코테 준비',
    description: '코딩테스트를 준비하는 취준생',
  },
] as const;
