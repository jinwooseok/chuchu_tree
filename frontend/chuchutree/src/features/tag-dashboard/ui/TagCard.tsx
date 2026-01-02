import { BadgeCheck } from 'lucide-react';

const nowLevel: string = 'Imediated';
const nextLevel: string = 'Advanced';
const nowRatio: number = 20;
const nextRatio: number = 80;
const nowPeekRatio: number = nowRatio > 90 ? 90 : nowRatio < 10 ? 10 : nowRatio;
const nextPeekRatio: number = nextRatio > 90 ? 90 : nextRatio < 10 ? 10 : nextRatio;
const nowBoxRatio: number = nowRatio > 75 ? 75 : nowRatio < 25 ? 25 : nowRatio;
const nextBoxRatio: number = nextRatio > 75 ? 75 : nextRatio < 25 ? 25 : nextRatio;

export default function TagCard() {
  return (
    <div className="bg-background flex h-40 flex-col gap-2 rounded-lg p-4 text-xs">
      {/* 카드 헤더 */}
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">tagname</div>
        <div className="flex h-full items-center justify-center gap-2">
          <div className="text-muted-foreground flex flex-col gap-0.5">
            <div className="border-innerground-darkgray rounded border text-center">추천 포함됨</div>
            <div className="flex gap-0.5">
              <p>마지막 풀이</p>
              <p className={`text-primary font-semibold`}>12</p>
              <p>일 전</p>
            </div>
          </div>
          <div className={`bg-advanced-bg text-advanced-text flex h-full items-center rounded px-2`}>Advanced</div>
        </div>
      </div>
      {/* 카드 바디 */}
      <div className="flex flex-1 gap-2">
        {/* 게이지 */}
        <div className="flex flex-1 items-center justify-center rounded border-2 border-dashed p-2">
          <div className="bg-innerground-darkgray relative h-4 w-full rounded-sm">
            <div className="bg-imediated-bg text-imediated-text absolute -top-6 -translate-x-1/2 rounded px-4" style={{ left: `${nowBoxRatio}%` }}>
              {nowLevel}
            </div>
            <div
              className="border-t-imediated-bg absolute bottom-full h-0 w-0 border-t-8 border-r-8 border-l-8 border-r-transparent border-l-transparent"
              style={{ left: `${nowPeekRatio - 5}%` }}
            ></div>
            <div className="bg-muted-foreground text-innerground-white absolute -bottom-6 -translate-x-1/2 rounded px-4" style={{ left: `${nextBoxRatio}%` }}>
              {nextLevel}
            </div>
            <div
              className="border-b-muted-foreground absolute top-full h-0 w-0 border-r-8 border-b-8 border-l-8 border-r-transparent border-l-transparent"
              style={{ left: `${nextPeekRatio - 5}%` }}
            ></div>

            <div className={`bg-imediated-bg h-4 rounded`} style={{ width: `${nowRatio}%` }}></div>
          </div>
        </div>
        {/* 스탯 */}
        <div className="flex flex-col gap-2 rounded border-2 border-dashed px-1 py-2">
          <div className="flex items-center justify-between gap-4">
            <div>Clear</div>
            <div className="text-muted-foreground flex items-center justify-center">
              <p>{2}</p>
              <p>/</p>
              <p>{15}</p>
              <div className="ml-2">
                <BadgeCheck height={12} width={12} />
              </div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-4">
            <div>Tier</div>
            <div className="text-muted-foreground flex items-center justify-center">
              <p className={``}>{'P5'}</p>
              <div className="ml-2">
                <BadgeCheck height={12} width={12} />
              </div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-4">
            <div>Best</div>
            <div className="text-advanced-bg flex items-center justify-center">
              <p className={``}>{'P3'}</p>
              <div className="ml-2">
                <BadgeCheck height={12} width={12} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
