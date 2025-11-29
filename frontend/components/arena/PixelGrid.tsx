'use client';

import { useEffect, useMemo, useState, useRef } from 'react';
import { codeToPixels, simplifyPixels } from '@/utils/codeToPixels';

interface PixelGridProps {
  code: string;
  animate?: boolean;
  maxRows?: number;
  pixelSize?: number;
  className?: string;
}

export function PixelGrid({
  code,
  animate = false,
  maxRows = 20,
  pixelSize = 3,
  className = '',
}: PixelGridProps) {
  const [animationKey, setAnimationKey] = useState(0);
  const [revealedRows, setRevealedRows] = useState(0);
  const prevCodeRef = useRef<string | null>(null);

  // Convert code to pixels
  const pixels = useMemo(() => {
    if (!code) return [];
    const fullPixels = codeToPixels(code, 60);
    return simplifyPixels(fullPixels, maxRows);
  }, [code, maxRows]);

  // Compute displayed rows based on animation state
  const displayedRows = animate ? revealedRows : pixels.length;

  // Reset animation when code changes
  useEffect(() => {
    if (code !== prevCodeRef.current) {
      prevCodeRef.current = code;
      if (animate) {
        setRevealedRows(0);
        setAnimationKey(k => k + 1);
      }
    }
  }, [code, animate]);

  // Animation interval effect - only runs when animating
  useEffect(() => {
    if (!animate || pixels.length === 0) {
      return;
    }

    // Start fresh animation
    setRevealedRows(0);

    const interval = setInterval(() => {
      setRevealedRows(prev => {
        if (prev >= pixels.length) {
          clearInterval(interval);
          return pixels.length;
        }
        return prev + 1;
      });
    }, 50); // Reveal one row every 50ms

    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [animationKey, pixels.length]);

  if (!code || pixels.length === 0) {
    return (
      <div className={`flex items-center justify-center h-32 bg-zinc-900 rounded ${className}`}>
        <p className="text-zinc-500 text-xs">No code yet</p>
      </div>
    );
  }

  return (
    <div className={`p-2 bg-zinc-900 rounded overflow-hidden ${className}`}>
      <div className="flex flex-col gap-[1px]">
        {pixels.slice(0, displayedRows).map((row, rowIndex) => (
          <div key={rowIndex} className="flex gap-[1px]">
            {row.map((pixel, colIndex) => (
              <div
                key={colIndex}
                className="transition-colors duration-100"
                style={{
                  width: `${pixelSize}px`,
                  height: `${pixelSize}px`,
                  backgroundColor: pixel.color === 'transparent' ? '#18181b' : pixel.color,
                  opacity: pixel.color === 'transparent' ? 0.3 : 1,
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
