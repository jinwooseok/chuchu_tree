'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

export interface UseResizableOptions {
  direction: 'horizontal' | 'vertical';
  initialSize: number;
  minSize: number;
  maxSize: number;
  onResizeStart?: () => void;
  onResize?: (size: number) => void;
  onResizeEnd?: (size: number) => void;
}

export interface UseResizableReturn {
  size: number;
  isResizing: boolean;
  handleMouseDown: (e: React.MouseEvent) => void;
}

/**
 * Custom hook for drag-resize functionality with performance optimization
 * Uses requestAnimationFrame for smooth 60fps updates
 */
export function useResizable(options: UseResizableOptions): UseResizableReturn {
  const { direction, initialSize, minSize, maxSize, onResizeStart, onResize, onResizeEnd } = options;

  // Current size state
  const [size, setSize] = useState(initialSize);
  const [isResizing, setIsResizing] = useState(false);
  const [prevInitialSize, setPrevInitialSize] = useState(initialSize);

  // Refs to avoid re-renders and store drag state
  const isResizingRef = useRef(false);
  const startPosRef = useRef(0);
  const startSizeRef = useRef(0);
  const rafIdRef = useRef<number | null>(null);
  const currentSizeRef = useRef(initialSize);

  // Update size when initialSize changes (React recommended pattern for derived state)
  // Only update if not currently resizing
  if (initialSize !== prevInitialSize && !isResizing) {
    setPrevInitialSize(initialSize);
    setSize(initialSize);
  }

  // Sync currentSizeRef with size changes (in effect to avoid render-time ref access)
  useEffect(() => {
    currentSizeRef.current = size;
  }, [size]);

  /**
   * Clamps size between min and max constraints
   */
  const clampSize = useCallback(
    (value: number): number => {
      return Math.max(minSize, Math.min(maxSize, value));
    },
    [minSize, maxSize],
  );

  /**
   * Handle mouse down - start resize
   */
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();

      // Set initial values
      isResizingRef.current = true;
      setIsResizing(true);
      startPosRef.current = direction === 'horizontal' ? e.clientX : e.clientY;
      startSizeRef.current = currentSizeRef.current;

      // Disable text selection during drag
      document.body.style.userSelect = 'none';
      document.body.style.cursor = direction === 'horizontal' ? 'col-resize' : 'row-resize';

      /**
       * Handle mouse move with requestAnimationFrame for smooth updates
       */
      const handleMouseMove = (e: MouseEvent) => {
        if (!isResizingRef.current) return;

        // Cancel previous frame if still pending
        if (rafIdRef.current !== null) {
          cancelAnimationFrame(rafIdRef.current);
        }

        // Schedule update for next frame
        rafIdRef.current = requestAnimationFrame(() => {
          const currentPos = direction === 'horizontal' ? e.clientX : e.clientY;
          const delta = currentPos - startPosRef.current;

          // Calculate new size
          const newSize = clampSize(startSizeRef.current + delta);

          // Update size
          currentSizeRef.current = newSize;
          setSize(newSize);

          // Call onResize callback if provided
          if (onResize) {
            onResize(newSize);
          }

          rafIdRef.current = null;
        });
      };

      /**
       * Handle mouse up - cleanup and finalize resize
       */
      const handleMouseUp = () => {
        if (!isResizingRef.current) return;

        // Cancel any pending animation frame
        if (rafIdRef.current !== null) {
          cancelAnimationFrame(rafIdRef.current);
          rafIdRef.current = null;
        }

        // Update refs
        isResizingRef.current = false;
        setIsResizing(false);

        // Remove global listeners
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);

        // Enable text selection again
        document.body.style.userSelect = '';
        document.body.style.cursor = '';

        // Call onResizeEnd callback with final size
        if (onResizeEnd) {
          onResizeEnd(currentSizeRef.current);
        }
      };

      // Add global listeners
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      // Call onResizeStart callback
      if (onResizeStart) {
        onResizeStart();
      }
    },
    [direction, clampSize, onResize, onResizeStart, onResizeEnd],
  );

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      // Cancel any pending animation frame
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
      }

      // Reset body styles
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
    };
  }, []);

  return {
    size,
    isResizing,
    handleMouseDown,
  };
}
