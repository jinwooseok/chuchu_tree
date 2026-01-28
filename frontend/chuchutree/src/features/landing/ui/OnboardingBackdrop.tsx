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

export function OnboardingBackdrop({ opacity = 0.7, spotlightTarget }: OnboardingBackdropProps) {
  // Spotlight가 없으면 전체 어둡게
  if (!spotlightTarget) {
    return (
      <div
        className="pointer-events-none fixed inset-0 z-40 backdrop-blur-sm"
        style={{
          backgroundColor: `rgba(0, 0, 0, ${opacity})`,
        }}
      />
    );
  }

  // Spotlight가 있으면 해당 영역만 밝게 (향후 구현)
  return (
    <div
      className="pointer-events-none fixed inset-0 z-40 backdrop-blur-sm"
      style={{
        backgroundColor: `rgba(0, 0, 0, ${opacity})`,
      }}
    />
  );
}
