import { User } from '@/entities/user';
import { TierNumKey } from '@/shared/constants/tierSystem';

type UserClassInfo = {
  userClass: number | null;
  classDetail: { class: number; totalSolved: number }[];
};
type Top100Problem = {
  problemId: number;
  problemTitle: string;
  problemTierLevel: TierNumKey;
};
const weeklyProblemCnt: number = 5;
const startDate = '2026-01-01' as string;
const targetClass = 6 as number | null;
const userClassInfo: UserClassInfo = {
  userClass: 6,
  classDetail: [
    {
      class: 1,
      totalSolved: 26,
    },
    {
      class: 2,
      totalSolved: 30,
    },
    {
      class: 3,
      totalSolved: 26,
    },
    {
      class: 4,
      totalSolved: 16,
    },
    {
      class: 5,
      totalSolved: 19,
    },
    {
      class: 6,
      totalSolved: 26,
    },
    {
      class: 7,
      totalSolved: 9,
    },
    {
      class: 8,
      totalSolved: 0,
    },
    {
      class: 9,
      totalSolved: 0,
    },
    {
      class: 10,
      totalSolved: 0,
    },
  ],
};
const top100: Top100Problem[] = [
  {
    problemId: 1000,
    problemTitle: 'asd',
    problemTierLevel: 3,
  },
  {
    problemId: 1001,
    problemTitle: 'efg',
    problemTierLevel: 12,
  },
  {
    problemId: 1002,
    problemTitle: 'hih',
    problemTierLevel: 16,
  },
];

export default function NextTier({ user }: { user: User }) {
  return (
    <div className="flex w-full items-center justify-between text-sm">
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
      <div className="flex flex-col gap-1">
        <div className="flex">
          <div className=''>어려운문제 위주로 풀거야 ✅</div>
          <div>P5</div>
          <div>🩵🩵🩵🩶🩶 🩶🩶🩶🩶🩶 🩶🩶🩶</div>
        </div>
        <div className="flex">
          <div className=''>적당한문제 위주로 풀거야</div>
          <div>G1</div>
          <div>💛💛🩶🩶🩶 🩶🩶🩶🩶</div>
        </div>
        <div className="flex">
          <div className=''>쉬운문제 위주로 풀거야</div>
          <div>G2</div>
          <div>💛💛💛</div>
        </div>
      </div>
    </div>
  );
}
