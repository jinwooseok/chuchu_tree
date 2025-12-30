import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Image from 'next/image';

const MockProblemsList = [
  {
    problemId: 1100,
    problemTitle: '내 생각에 A번인 단순 dfs 문제가 이 대회에서 E번이 되어버린 건에 관하여 (Easy)',
    problemTierLevel: 1,
    problemTierName: 'B1', // B1, S1, G1, P1, D1, R1, C1
    problemClassLevel: 7,
    recommandReasons: [
      {
        reason: 'IM_LEVEL',
        additionalData: null,
      },
      {
        reason: 'LEVEL_UP_SOON',
        additionalData: { nextLevel: 'AD', remainedProblemCount: 2 },
      },
      {
        reason: 'LAST_SOLVED_DATE',
        additionalData: { lastSolvedDate: '2025-05-07' },
      },
    ],
    tags: [
      {
        tagId: 1,
        tagCode: 'TAG_CODE',
        tagDisplayName: '세그먼트트리',
        tagTarget: [
          {
            targetId: 1,
            targetCode: 'CT',
            targetDisplayName: '뭐시기',
          },
        ],
        tagAliases: [{ alias: 'asdf' }, { alias: 'asdf' }],
      },
    ],
  },
  {
    problemId: 12000,
    problemTitle: '도시 왕복하기 1',
    problemTierLevel: 22,
    problemTierName: 'B1', // B1, S1, G1, P1, D1, R1, C1
    problemClassLevel: 7,
    recommandReasons: [
      {
        reason: 'IM_LEVEL',
        additionalData: null,
      },
      {
        reason: 'LEVEL_UP_SOON',
        additionalData: { nextLevel: 'AD', remainedProblemCount: 2 },
      },
      {
        reason: 'LAST_SOLVED_DATE',
        additionalData: { lastSolvedDate: '2025-05-07' },
      },
    ],
    tags: [
      {
        tagId: 1,
        tagCode: 'TAG_CODE',
        tagDisplayName: '트리 맵',
        tagTarget: [
          {
            targetId: 1,
            targetCode: 'CT',
            targetDisplayName: '뭐시기',
          },
        ],
        tagAliases: [{ alias: 'asdf' }, { alias: 'asdf' }],
      },
    ],
  },
  {
    problemId: 1582,
    problemTitle: '분산처리',
    problemTierLevel: 17,
    problemTierName: 'B1', // B1, S1, G1, P1, D1, R1, C1
    problemClassLevel: 7,
    recommandReasons: [
      {
        reason: 'IM_LEVEL',
        additionalData: null,
      },
      {
        reason: 'LEVEL_UP_SOON',
        additionalData: { nextLevel: 'AD', remainedProblemCount: 2 },
      },
      {
        reason: 'LAST_SOLVED_DATE',
        additionalData: { lastSolvedDate: '2025-05-07' },
      },
    ],
    tags: [
      {
        tagId: 1,
        tagCode: 'TAG_CODE',
        tagDisplayName: '에라토스테네스의체',
        tagTarget: [
          {
            targetId: 1,
            targetCode: 'CT',
            targetDisplayName: '뭐시기',
          },
        ],
        tagAliases: [{ alias: 'asdf' }, { alias: 'asdf' }],
      },
    ],
  },
];

export default function BottomRecommend() {
  return (
    <div className="bg-innerground-white flex h-full items-center justify-between p-4">
      {/* 왼쪽 추천받기 인터페이스 */}
      <div className="flex h-full flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        <Button className="flex-1">추천 받기</Button>
        <div className="flex justify-between gap-2">
          <Button className="h-6 px-2 py-0 text-[10px]">easy</Button>
          <Button className="h-6 px-2 py-0 text-[10px]">normal</Button>
          <Button className="h-6 px-2 py-0 text-[10px]">hard</Button>
          <Button className="h-6 px-2 py-0 text-[10px]">extreme</Button>
        </div>

        <div className="flex items-center gap-2 rounded-lg border px-2">
          <p className="text-xs">TAG</p>
          <Input className="border-none" placeholder="All" />
        </div>
        <div className="flex justify-between gap-1">
          <Button className="h-6 px-2 py-0 text-[10px]">문제번호</Button>
          <Button className="h-6 px-2 py-0 text-[10px]">문제티어</Button>
          <Button className="h-6 px-2 py-0 text-[10px]">추천이유</Button>
          <Button className="h-6 px-2 py-0 text-[10px]">알고리즘</Button>
        </div>
      </div>
      {/* 오른쪽 추천 문제들 */}
      <div className="flex h-full flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        {MockProblemsList.map((c, i) => (
          <div key={c.problemId} className="flex flex-1/3">
            <Button className="bg-muted-foreground h-full flex-col items-center justify-center rounded-l-lg rounded-r-none text-xs">
              <p>문제</p>
              <p>등록</p>
            </Button>
            <div className="bg-background text-foreground flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
              <div className="flex items-center">
                <div className="flex min-w-20 items-center">
                  <Image src={`/tiers/tier_${MockProblemsList[i].problemTierLevel}.svg`} alt={`Tier ${MockProblemsList[i].problemTierLevel}`} width={24} height={24} className="h-6 w-6" />
                  <p>{MockProblemsList[i].problemId}</p>
                </div>
                <p>{MockProblemsList[i].problemTitle}</p>
              </div>
              <div className="flex min-w-30 flex-col items-end">
                <p>{MockProblemsList[i].tags[0].tagDisplayName}</p>
                <p className="text-muted-foreground">{MockProblemsList[i].recommandReasons[0].reason}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
