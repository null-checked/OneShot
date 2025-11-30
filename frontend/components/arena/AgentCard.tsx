'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Code, TestTube, Trophy, RefreshCw, AlertCircle, CheckCircle2, Wrench } from 'lucide-react';
import type { AgentState } from '@/lib/types';
import { PixelGrid } from './PixelGrid';
import { TestRunner } from './TestRunner';

interface AgentCardProps {
  agent: AgentState;
}

export function AgentCard({ agent }: AgentCardProps) {
  const { personality, status, task, solution, testResults, testFeedback, score, retryCount, maxRetries } = agent;

  // Status badge configuration
  const statusConfig = {
    idle: { label: 'Idle', icon: null, color: 'bg-zinc-600' },
    thinking: { label: 'Thinking', icon: Brain, color: 'bg-blue-500 animate-pulse' },
    coding: { label: 'Coding', icon: Code, color: 'bg-purple-500 animate-pulse' },
    testing: { label: 'Testing', icon: TestTube, color: 'bg-yellow-500 animate-pulse' },
    fixing: { label: 'Fixing', icon: Wrench, color: 'bg-orange-500 animate-pulse' },
    complete: { label: 'Complete', icon: Trophy, color: 'bg-green-500' },
    error: { label: 'Error', icon: AlertCircle, color: 'bg-red-500' },
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
          <div className="flex items-center gap-2">
            {/* Retry counter */}
            {retryCount > 0 && (
              <Badge variant="outline" className="text-xs">
                <RefreshCw className="w-3 h-3 mr-1" />
                {retryCount}/{maxRetries}
              </Badge>
            )}
            <Badge className={currentStatus.color}>
              {StatusIcon && <StatusIcon className="w-3 h-3 mr-1" />}
              {currentStatus.label}
            </Badge>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">{personality.approach}</p>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Assigned Task */}
        {task && (
          <div className="p-2 rounded bg-zinc-100 dark:bg-zinc-900 border-l-2" style={{ borderColor: personality.color }}>
            <p className="text-xs font-medium mb-1">Assigned Task:</p>
            <p className="text-xs text-muted-foreground">{task.description}</p>
            {task.requirements && task.requirements.length > 0 && (
              <div className="mt-2">
                <p className="text-xs font-medium">Requirements:</p>
                <ul className="text-xs text-muted-foreground mt-1 space-y-0.5">
                  {task.requirements.slice(0, 3).map((req, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span style={{ color: personality.color }}>•</span>
                      <span>{req}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

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
            animate={status === 'coding'}
            maxRows={12}
            pixelSize={2}
          />
        )}

        {/* Test Feedback from Test Agent */}
        {testFeedback && (
          <div className={`p-2 rounded border ${testFeedback.passed ? 'bg-green-50 dark:bg-green-950/20 border-green-500' : 'bg-red-50 dark:bg-red-950/20 border-red-500'}`}>
            <div className="flex items-center gap-1 mb-1">
              {testFeedback.passed ? (
                <CheckCircle2 className="w-3 h-3 text-green-500" />
              ) : (
                <AlertCircle className="w-3 h-3 text-red-500" />
              )}
              <p className="text-xs font-medium">
                Test Agent: {testFeedback.test_agent}
              </p>
            </div>
            <p className="text-xs text-muted-foreground">{testFeedback.feedback}</p>
            
            {!testFeedback.passed && testFeedback.failed_tests && testFeedback.failed_tests.length > 0 && (
              <div className="mt-2">
                <p className="text-xs font-medium text-red-600 dark:text-red-400">Failed Tests:</p>
                <ul className="text-xs text-muted-foreground mt-1">
                  {testFeedback.failed_tests.slice(0, 2).map((test, i) => (
                    <li key={i} className="text-red-600 dark:text-red-400">• {test}</li>
                  ))}
                </ul>
              </div>
            )}

            {!testFeedback.passed && testFeedback.suggestions && testFeedback.suggestions.length > 0 && (
              <div className="mt-2">
                <p className="text-xs font-medium">Suggestions:</p>
                <ul className="text-xs text-muted-foreground mt-1">
                  {testFeedback.suggestions.slice(0, 2).map((suggestion, i) => (
                    <li key={i}>💡 {suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
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

        {/* Coding animation */}
        {(status === 'coding' || status === 'fixing') && !solution && (
          <div className="flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-900 rounded">
            <div className="text-center space-y-2">
              {status === 'fixing' ? (
                <>
                  <Wrench className="w-8 h-8 mx-auto text-orange-500 animate-pulse" />
                  <p className="text-xs text-muted-foreground">Fixing issues (Retry {retryCount}/{maxRetries})...</p>
                </>
              ) : (
                <>
                  <Code className="w-8 h-8 mx-auto text-muted-foreground animate-pulse" />
                  <p className="text-xs text-muted-foreground">Implementing solution...</p>
                </>
              )}
            </div>
          </div>
        )}

        {/* Idle state */}
        {status === 'idle' && !task && (
          <div className="flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-900 rounded">
            <p className="text-xs text-muted-foreground">Waiting for task assignment...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
