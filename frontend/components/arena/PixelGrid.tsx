'use client';

import { useEffect, useMemo, useState } from 'react';
import { codeToPixels, simplifyPixels, type Pixel } from '@/utils/codeToPixels';

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
  const [revealedRows, setRevealedRows] = useState(0);

  // Convert code to pixels
  const pixels = useMemo(() => {
    if (!code) return [];
    const fullPixels = codeToPixels(code, 60);
    return simplifyPixels(fullPixels, maxRows);
  }, [code, maxRows]);

  // Animation effect
  useEffect(() => {
    if (!animate || pixels.length === 0) {
      setRevealedRows(pixels.length);
      return;
    }

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
  }, [animate, pixels.length]);

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
        {pixels.slice(0, revealedRows).map((row, rowIndex) => (
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
