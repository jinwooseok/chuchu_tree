import { useLandingUser } from '@/features/landing/hooks/useLandingUser';
// import NextTier from '@/features/top-tierbar/ui/NextTier';
import Tierbar from '@/features/top-tierbar/ui/Tierbar';

export default function LandingTopTierbar() {
  const user = useLandingUser();

  if (!user) return null;

  return (
    <div className="bg-innerground-white flex h-full w-full flex-col gap-4 p-6">
      <Tierbar user={user} />
      {/* <NextTier user={user} /> */}
    </div>
  );
}
