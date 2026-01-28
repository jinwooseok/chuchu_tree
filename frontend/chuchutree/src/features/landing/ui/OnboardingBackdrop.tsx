'use client';

interface OnboardingBackdropProps {
  opacity?: number;
  spotlightTarget?: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
}

export function OnboardingBackdrop({ opacity = 0.2, spotlightTarget }: OnboardingBackdropProps) {
  // Spotlight가 없으면 전체 어둡게
  if (!spotlightTarget) {
    return (
      <div
        className="pointer-events-none fixed inset-0 z-40"
        style={{
          backgroundColor: `rgba(0, 0, 0, ${opacity})`,
        }}
      />
    );
  }

  // Spotlight가 있으면 해당 영역만 밝게 (CSS mask 사용)
  const { x, y, width, height } = spotlightTarget;
  const padding = 8; // spotlight 주변 여백

  return (
    <>
      {/* 상단 영역 */}
      <div className="pointer-events-none fixed z-40" style={{ left: 0, top: 0, right: 0, height: `${y - padding}px`, backgroundColor: `rgba(0, 0, 0, ${opacity})` }} />

      {/* 중간 영역 (좌/spotlight/우) */}
      <div className="pointer-events-none fixed z-40" style={{ left: 0, top: `${y - padding}px`, right: 0, height: `${height + padding * 2}px` }}>
        {/* 좌측 */}
        <div className="absolute" style={{ left: 0, top: 0, bottom: 0, width: `${x - padding}px`, backgroundColor: `rgba(0, 0, 0, ${opacity})` }} />

        {/* Spotlight hole (투명) */}
        <div className="absolute" style={{ left: `${x - padding}px`, top: 0, width: `${width + padding * 2}px`, height: `${height + padding * 2}px` }} />

        {/* 우측 */}
        <div className="absolute" style={{ left: `${x + width + padding}px`, top: 0, bottom: 0, right: 0, backgroundColor: `rgba(0, 0, 0, ${opacity})` }} />
      </div>

      {/* 하단 영역 */}
      <div className="pointer-events-none fixed z-40" style={{ left: 0, top: `${y + height + padding}px`, right: 0, bottom: 0, backgroundColor: `rgba(0, 0, 0, ${opacity})` }} />
    </>
  );
}
