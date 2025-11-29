'use client';

import { useEffect, useState } from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import type { TestResult } from '@/lib/types';

interface TestRunnerProps {
  results?: TestResult[];
  totalTests: number;
  animate?: boolean;
  className?: string;
}

type TestState = 'pending' | 'running' | 'passed' | 'failed';

export function TestRunner({
  results = [],
  totalTests,
  animate = false,
  className = '',
}: TestRunnerProps) {
  const [animatedStates, setAnimatedStates] = useState<TestState[]>(
    Array(totalTests).fill('pending')
  );

  // Animate test execution
  useEffect(() => {
    if (!animate || results.length === 0) {
      // No animation, show final state immediately
      setAnimatedStates(
        Array.from({ length: totalTests }, (_, i) => {
          if (i >= results.length) return 'pending';
          return results[i].passed ? 'passed' : 'failed';
        })
      );
      return;
    }

    // Reset to pending
    setAnimatedStates(Array(totalTests).fill('pending'));

    // Animate each test
    let currentTest = 0;
    const interval = setInterval(() => {
      if (currentTest >= results.length) {
        clearInterval(interval);
        return;
      }

      // Set to running
      setAnimatedStates(prev => {
        const next = [...prev];
        next[currentTest] = 'running';
        return next;
      });

      // After a delay, set to passed/failed
      setTimeout(() => {
        setAnimatedStates(prev => {
          const next = [...prev];
          next[currentTest] = results[currentTest].passed ? 'passed' : 'failed';
          return next;
        });
      }, 200);

      currentTest++;
    }, 400);

    return () => clearInterval(interval);
  }, [results, totalTests, animate]);

  return (
    <div className={`flex flex-wrap gap-1.5 ${className}`}>
      {animatedStates.map((state, index) => {
        const result = results[index];
        const executionTime = result?.execution_time_ms?.toFixed(2);

        return (
          <div
            key={index}
            className="group relative"
            title={
              result
                ? `Test ${index + 1}: ${state === 'passed' ? 'Passed' : 'Failed'}${
                    executionTime ? ` (${executionTime}ms)` : ''
                  }${result.error ? `\nError: ${result.error}` : ''}`
                : `Test ${index + 1}: Pending`
            }
          >
            <div
              className={`
                w-8 h-8 rounded flex items-center justify-center transition-all duration-300
                ${
                  state === 'pending'
                    ? 'bg-zinc-700'
                    : state === 'running'
                    ? 'bg-yellow-500 animate-pulse'
                    : state === 'passed'
                    ? 'bg-green-500'
                    : 'bg-red-500'
                }
              `}
            >
              {state === 'running' && (
                <Loader2 className="w-4 h-4 text-white animate-spin" />
              )}
              {state === 'passed' && <Check className="w-4 h-4 text-white" />}
              {state === 'failed' && <X className="w-4 h-4 text-white" />}
            </div>

            {/* Tooltip on hover */}
            {result && (
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                <div className="bg-zinc-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap shadow-lg border border-zinc-700">
                  {executionTime && <div>Time: {executionTime}ms</div>}
                  {result.error && (
                    <div className="text-red-400 max-w-xs truncate">
                      Error: {result.error}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
