'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Code, TestTube, Trophy } from 'lucide-react';
import type { AgentState } from '@/lib/types';
import { PixelGrid } from './PixelGrid';
import { TestRunner } from './TestRunner';

interface AgentCardProps {
  agent: AgentState;
  totalTests?: number;
}

export function AgentCard({ agent, totalTests = 0 }: AgentCardProps) {
  const { personality, status, solution, testResults, score } = agent;

  // Status badge configuration
  const statusConfig = {
    idle: { label: 'Idle', icon: null, color: 'bg-zinc-600' },
    thinking: { label: 'Thinking', icon: Brain, color: 'bg-blue-500 animate-pulse' },
    testing: { label: 'Testing', icon: TestTube, color: 'bg-yellow-500 animate-pulse' },
    complete: { label: 'Complete', icon: Trophy, color: 'bg-green-500' },
    error: { label: 'Error', icon: null, color: 'bg-red-500' },
  };

  const currentStatus = statusConfig[status];
  const StatusIcon = currentStatus.icon;

  // Calculate test progress
  const testProgress = testResults
    ? (testResults.passed_tests / testResults.total_tests) * 100
    : 0;

  return (
    <Card className="relative overflow-hidden border-2 transition-all hover:shadow-lg">
      {/* Color indicator */}
      <div
        className="absolute top-0 left-0 right-0 h-1"
        style={{ backgroundColor: personality.color }}
      />

      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold">{personality.name}</CardTitle>
          <Badge className={currentStatus.color}>
            {StatusIcon && <StatusIcon className="w-3 h-3 mr-1" />}
            {currentStatus.label}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">{personality.approach}</p>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Approach and Complexity */}
        {solution && (
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <Code className="w-3 h-3 text-muted-foreground" />
              <p className="text-xs font-medium">{solution.approach_name}</p>
            </div>
            <div className="flex gap-2 text-xs text-muted-foreground">
              <span>Time: {solution.time_complexity}</span>
              <span>Space: {solution.space_complexity}</span>
            </div>
          </div>
        )}

        {/* Pixel Visualization */}
        {solution?.code && (
          <PixelGrid
            code={solution.code}
            animate={status === 'thinking'}
            maxRows={15}
            pixelSize={2}
          />
        )}

        {/* Test Results */}
        {testResults && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium">
                Tests: {testResults.passed_tests}/{testResults.total_tests}
              </span>
              <span className="text-muted-foreground">
                {testResults.avg_time_ms.toFixed(2)}ms avg
              </span>
            </div>
            <Progress value={testProgress} className="h-2" />
            <TestRunner
              results={testResults.results}
              totalTests={testResults.total_tests}
              animate={status === 'testing'}
            />
          </div>
        )}

        {/* Score Breakdown */}
        {score && (
          <div className="mt-4 pt-3 border-t space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">Rank #{score.rank}</span>
              <span className="text-lg font-bold" style={{ color: personality.color }}>
                {score.total.toFixed(1)}
              </span>
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Correctness</span>
                <span className="font-medium">{score.correctness.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Performance</span>
                <span className="font-medium">{score.performance.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Quality</span>
                <span className="font-medium">{score.quality.toFixed(1)}</span>
              </div>
            </div>
            {score.analysis && (
              <p className="text-xs text-muted-foreground mt-2 italic">
                {score.analysis}
              </p>
            )}
          </div>
        )}

        {/* Thinking display */}
        {status === 'thinking' && !solution && (
          <div className="flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-900 rounded">
            <div className="text-center space-y-2">
              <Brain className="w-8 h-8 mx-auto text-muted-foreground animate-pulse" />
              <p className="text-xs text-muted-foreground">Generating solution...</p>
            </div>
          </div>
        )}

        {/* Idle state */}
        {status === 'idle' && (
          <div className="flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-900 rounded">
            <p className="text-xs text-muted-foreground">Waiting to start...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
