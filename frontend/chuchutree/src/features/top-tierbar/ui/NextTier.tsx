import { User } from '@/entities/user';
import { getTierDetail } from '@/features/top-tierbar/lib/utils';
import { TierNumKey } from '@/shared/constants/tierSystem';

type UserClassInfo = {
  userClass: number | null;
  classDetail: { class: number; totalSolved: number }[];
};
type Top100Problem = {
  problemId: number; // 문제번호
  problemTitle: string; // 문제이름
  problemTierLevel: TierNumKey; // 문제티어
  isNew: boolean; // 시작일 이후 추가된 문제
};
const weeklyProblemCnt: number = 5; // 주간 목표 문제 풀이 수
const startDate = '2026-01-01' as string; // 다음티어달성예측 시작일
const nowClass = 6 as number | null; // 현재 CLASS 등급
const targetClass = 7 as number | null; // 목표 CLASS 등급
const top100: Top100Problem[] = [
  {
    problemId: 1000,
    problemTitle: 'asd',
    problemTierLevel: 3,
    isNew: true,
  },
  {
    problemId: 1001,
    problemTitle: 'efg',
    problemTierLevel: 12,
    isNew: false,
  },
  {
    problemId: 1002,
    problemTitle: 'hih',
    problemTierLevel: 16,
    isNew: true,
  },
]; // top 100 문제들

export default function NextTier({ user }: { user: User }) {
  const tierDetail = getTierDetail(user);
  return (
    <div className="flex w-full items-center justify-between text-sm">
      {/* 좌측 인터페이스 */}
      <div className="flex flex-col gap-1">
        <div className="flex">
          <div className="w-26">시작날짜</div>
          {startDate}
        </div>
        <div className="flex">
          <div className="w-26">주간목표</div>
          {weeklyProblemCnt}문제
        </div>
        <div className="flex">
          <div className="w-26">CLASS목표</div>
          {targetClass}
        </div>
      </div>
      {/* 우측 하트정보 */}
      <div className="flex flex-col gap-1">
        <div className="flex">
          <div className="">어려운문제 위주로 풀거야 ✅</div>
          <div>P5</div>
          <div>🩵🩵🩵🩶🩶 🩶🩶🩶🩶🩶 🩶🩶🩶</div>
        </div>
        <div className="flex">
          <div className="">적당한문제 위주로 풀거야</div>
          <div>G1</div>
          <div>💛💛🩶🩶🩶 🩶🩶🩶🩶</div>
        </div>
        <div className="flex">
          <div className="">쉬운문제 위주로 풀거야</div>
          <div>G2</div>
          <div>💛💛💛</div>
        </div>
      </div>
    </div>
  );
}
