import Image from 'next/image';

interface LogoSvgProps {
  size?: number;
  className?: string;
}

// 로고 SVG 자연 비율: width 47, height 70
const LOGO_WIDTH = 47;
const LOGO_HEIGHT = 70;

export function LogoSvg({ size = 24, className }: LogoSvgProps) {
  const height = Math.round(size * (LOGO_HEIGHT / LOGO_WIDTH));
  return <Image src="/logo/logo.svg" alt="logo" width={size} height={height} className={className} unoptimized/>;
}
