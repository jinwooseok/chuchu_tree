'use client';

import { cn } from '@/lib/utils';

export interface ResizeHandleProps {
  direction: 'horizontal' | 'vertical';
  onMouseDown: (e: React.MouseEvent) => void;
  className?: string;
}

/**
 * ResizeHandle Component
 *
 * A hover-activated drag handle for resizing panels
 * - Default: Subtle border appearance
 * - Hover: Emphasized with primary color and cursor change
 * - Active (dragging): Visual feedback with accent
 */
export function ResizeHandle({ direction, onMouseDown, className }: ResizeHandleProps) {
  const isHorizontal = direction === 'horizontal';

  return (
    <div
      role="separator"
      aria-label={isHorizontal ? 'Resize sidebar' : 'Resize section'}
      aria-orientation={isHorizontal ? 'vertical' : 'horizontal'}
      tabIndex={0}
      onMouseDown={onMouseDown}
      className={cn(
        // Base styles
        'group relative z-10 shrink-0 select-none',

        // Size and cursor
        isHorizontal
          ? 'w-1 cursor-col-resize hover:w-1' // Horizontal: thin vertical line
          : 'h-1 cursor-row-resize hover:h-1', // Vertical: thin horizontal line

        // Border styles
        isHorizontal
          ? 'border-border hover:border-primary border-r' // Right border for horizontal
          : 'border-border hover:border-primary border-b', // Bottom border for vertical

        // Hover effects
        'transition-colors duration-150',
        'hover:bg-primary/10',

        // Active (dragging) state
        'active:bg-primary/20',

        // Focus styles for accessibility
        'focus:ring-primary focus:ring-2 focus:ring-offset-2 focus:outline-none',

        // Custom className overrides
        className,
      )}
    >
      {/* Invisible hit area for easier grabbing */}
      <div
        className={cn(
          'absolute inset-0',
          isHorizontal
            ? '-right-2 -left-2 w-4' // Expand hit area horizontally
            : '-top-2 -bottom-2 h-4', // Expand hit area vertically
        )}
      />

      {/* Visual indicator on hover (optional dots or grip lines) */}
      <div
        className={cn(
          'pointer-events-none absolute opacity-0 transition-opacity group-hover:opacity-100',
          isHorizontal
            ? 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2' // Center for horizontal
            : 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2', // Center for vertical
        )}
      >
        {/* Grip dots/lines indicator */}
        <div className={cn('bg-primary/50 rounded-full', isHorizontal ? 'flex h-12 w-1 flex-col gap-1' : 'flex h-1 w-12 flex-row gap-1')} />
      </div>
    </div>
  );
}
