import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface AppTooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  side?: 'top' | 'right' | 'bottom' | 'left';
  delayDuration?: number;
  contentClassName?: string;
  shortCut1?: string;
  shortCut2?: string;
}

export function AppTooltip({ content, children, side = 'bottom', delayDuration = 100, contentClassName = 'bg-foreground', shortCut1, shortCut2 }: AppTooltipProps) {
  return (
    <TooltipProvider>
      <Tooltip delayDuration={delayDuration}>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent side={side} className={contentClassName}>
          <div className={`flex items-center gap-1 ${side === 'bottom' ? 'mt-0.5' : ''}`}>
            <div className="mr-1">{content}</div>
            {shortCut1 && <div className="bg-only-gray rounded-xs px-1 py-0.5 text-center text-[10px] text-white">{shortCut1}</div>}
            {shortCut2 && <div className="bg-only-gray rounded-xs px-1 py-0.5 text-center text-[10px] text-white">{shortCut2}</div>}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
