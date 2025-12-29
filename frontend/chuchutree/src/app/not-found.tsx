import GlitchText from '@/components/custom/not-found-text/NotFoundGlitchText';
import TargetCursor from '@/components/custom/not-found-text/TargetCursor';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center">
      <GlitchText speed={4} enableShadows={true} enableOnHover={false} className="cursor-target">
        404 Not Found
      </GlitchText>
      <Link aria-label="홈으로 돌아가기" title="홈으로 돌아가기" href="/" className="cursor-target bg-no2 text-foreground hover:bg-no2/50 trasition mt-10 rounded-lg px-4 py-2 duration-300">
        Come Back Home Bebe
      </Link>
      <TargetCursor spinDuration={2} hideDefaultCursor={true} />
    </div>
  );
}
