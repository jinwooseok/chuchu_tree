'use client';

import { useUser } from '@/entities/user/model/queries';
// import NextTier from '@/features/top-tierbar/ui/NextTier';
import Tierbar from '@/features/top-tierbar/ui/Tierbar';

export default function TopTierbar() {
  const { data: user } = useUser();

  if (!user) return null;

  return (
    <div className="bg-innerground-white flex h-full w-full flex-col gap-4 p-6">
      <Tierbar user={user} />
      {/* <NextTier user={user} /> */}
    </div>
  );
}
