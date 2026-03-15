import Image from 'next/image';

interface TierSvgProps {
  tier: number;
  size?: number;
  alt?: string;
  className?: string;
}

// 티어 SVG 자연 비율: width 400, height 512
const TIER_WIDTH = 400;
const TIER_HEIGHT = 512;

export function TierSvg({ tier, size = 16, alt, className }: TierSvgProps) {
  const height = Math.round(size * (TIER_HEIGHT / TIER_WIDTH));
  return <Image src={`/tiers/tier_${tier}.svg`} alt={alt ?? `Tier ${tier}`} width={size} height={height} className={className} />;
}
