import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { HelpCircle } from 'lucide-react';
import { ReactNode } from 'react';

interface HelpPopoverProps {
  children: ReactNode;
  width?: string;
}

export default function HelpPopover({ children, width = 'w-80' }: HelpPopoverProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="h-5 w-5 shrink-0">
          <HelpCircle className="text-muted-foreground h-5 w-5" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className={width}>{children}</PopoverContent>
    </Popover>
  );
}
