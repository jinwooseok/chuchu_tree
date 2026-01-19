'use client';

import * as React from 'react';
import * as SwitchPrimitive from '@radix-ui/react-switch';

import { cn } from '@/lib/utils';

function Switch({ className, ...props }: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  const [checked, setChecked] = React.useState(props.checked || props.defaultChecked || false);

  React.useEffect(() => {
    if (props.checked !== undefined) {
      setChecked(props.checked);
    }
  }, [props.checked]);

  return (
    <SwitchPrimitive.Root
      data-slot="switch"
      className={cn(
        'peer inline-flex h-[1.15rem] w-8 shrink-0 items-center rounded-full border border-transparent shadow-xs transition-all outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
        'focus-visible:border-ring focus-visible:ring-ring/50',
        checked ? 'bg-primary/60' : 'bg-innerground-darkgray',
        className,
      )}
      {...props}
      onCheckedChange={(newChecked) => {
        setChecked(newChecked);
        props.onCheckedChange?.(newChecked);
      }}
    >
      <SwitchPrimitive.Thumb
        data-slot="switch-thumb"
        className={cn(
          'pointer-events-none block size-4 rounded-full ring-0 transition-transform',
          checked ? 'bg-innerground-white translate-x-[calc(100%-2px)]' : 'bg-innerground-white translate-x-0',
        )}
      />
    </SwitchPrimitive.Root>
  );
}

export { Switch };
