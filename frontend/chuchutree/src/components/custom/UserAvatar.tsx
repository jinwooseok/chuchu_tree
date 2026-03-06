import Image from 'next/image';
import { User2 } from 'lucide-react';

interface UserAvatarProps {
  profileImageUrl: string | null;
  size?: number;
  className?: string;
}

export function UserAvatar({ profileImageUrl, size = 32, className = '' }: UserAvatarProps) {
  return (
    <div
      className={`bg-muted flex shrink-0 items-center justify-center overflow-hidden rounded-full border ${className}`}
      style={{ width: size, height: size }}
    >
      {profileImageUrl ? (
        <Image
          src={profileImageUrl}
          alt="프로필"
          width={size}
          height={size}
          className="h-full w-full object-cover"
          unoptimized
        />
      ) : (
        <User2 className="text-muted-foreground" style={{ width: size * 0.5, height: size * 0.5 }} />
      )}
    </div>
  );
}
