import { TargetCode } from './tagSystem';

export const TARGET_OPTIONS = [
  {
    code: 'BEGINNER' as TargetCode,
    label: '입문자',
    description: '알고리즘을 이제 막 시작한 초보자',
    description2: '기초적인 유형이 더 자주 추천됩니다.',
  },
  {
    code: 'CT' as TargetCode,
    label: '코테 준비',
    description: '코딩테스트를 준비하는 취준생',
    description2: '코테에 적당한 유형이 더 자주 추천됩니다.',
  },
  {
    code: 'DAILY' as TargetCode,
    label: '데일리',
    description: '1일 1알고리즘, 점수 올리기, 취미 등',
    description2: '쉬운 유형부터 어려운 유형까지 모든 유형이 추천됩니다.',
  },
] as const;
