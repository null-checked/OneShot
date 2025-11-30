'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, CheckCircle2, ListTodo, Target, Loader2 } from 'lucide-react';
import type { ArchitectState } from '@/lib/types';

interface ArchitectCardProps {
  architect: ArchitectState;
}

export function ArchitectCard({ architect }: ArchitectCardProps) {
  const { status, plan } = architect;

  const statusConfig = {
    idle: { label: 'Idle', color: 'bg-zinc-600', icon: null },
    planning: { label: 'Planning...', color: 'bg-blue-500 animate-pulse', icon: Loader2 },
    complete: { label: 'Plan Ready', color: 'bg-green-500', icon: CheckCircle2 },
    error: { label: 'Error', color: 'bg-red-500', icon: null },
  };

  const currentStatus = statusConfig[status];
  const StatusIcon = currentStatus.icon;

  return (
    <Card className="relative overflow-hidden border-2 border-purple-500/50 bg-gradient-to-br from-purple-500/5 to-transparent">
      {/* Color indicator */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500" />

      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-500" />
            <CardTitle className="text-lg font-bold">Architect Agent</CardTitle>
          </div>
          <Badge className={`${currentStatus.color} text-white`}>
            {StatusIcon && <StatusIcon className="w-3 h-3 mr-1 animate-spin" />}
            {currentStatus.label}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">Plans tasks and defines test criteria</p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Planning animation */}
        {status === 'planning' && (
          <div className="flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-900 rounded">
            <div className="text-center space-y-2">
              <Brain className="w-8 h-8 mx-auto text-purple-500 animate-pulse" />
              <p className="text-xs text-muted-foreground">Analyzing problem and planning tasks...</p>
            </div>
          </div>
        )}

        {/* Idle state */}
        {status === 'idle' && (
          <div className="flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-900 rounded">
            <p className="text-xs text-muted-foreground">Waiting for problem...</p>
          </div>
        )}

        {/* Plan display */}
        {plan && (
          <div className="space-y-4">
            {/* Overview */}
            <div className="space-y-1">
              <h4 className="text-sm font-semibold flex items-center gap-1">
                <Target className="w-3 h-3 text-purple-500" />
                Approach
              </h4>
              <p className="text-xs text-muted-foreground">{plan.approach}</p>
            </div>

            {/* Overview description */}
            <div className="space-y-1">
              <h4 className="text-sm font-semibold">Overview</h4>
              <p className="text-xs text-muted-foreground">{plan.overview}</p>
            </div>

            {/* Task assignments */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold flex items-center gap-1">
                <ListTodo className="w-3 h-3 text-purple-500" />
                Task Assignments
              </h4>
              <div className="space-y-2">
                {plan.agent_tasks.map((assignment, i) => (
                  <div
                    key={i}
                    className="p-2 rounded bg-zinc-100 dark:bg-zinc-900 border-l-2 border-purple-500"
                  >
                    <p className="text-xs font-medium text-purple-600 dark:text-purple-400">
                      {assignment.agent_name}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {assignment.task.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Test Strategy */}
            <div className="space-y-1">
              <h4 className="text-sm font-semibold">Test Strategy</h4>
              <p className="text-xs text-muted-foreground">{plan.test_strategy}</p>
            </div>

            {/* Success Criteria */}
            {plan.success_criteria && plan.success_criteria.length > 0 && (
              <div className="space-y-1">
                <h4 className="text-sm font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-green-500" />
                  Success Criteria
                </h4>
                <ul className="text-xs text-muted-foreground space-y-0.5">
                  {plan.success_criteria.map((criteria, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span className="text-green-500">✓</span>
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
