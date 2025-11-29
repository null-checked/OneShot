'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Code2, Brain, TestTube, Scale, Sparkles, CheckCircle2 } from 'lucide-react';
import type { ArenaState } from '@/lib/types';
import { AgentCard } from './AgentCard';
import { Scoreboard } from './Scoreboard';

interface ArenaProps {
  arenaState: ArenaState;
}

export function Arena({ arenaState }: ArenaProps) {
  const { status, problem, agents, synthesis } = arenaState;

  // Status configuration
  const statusConfig = {
    idle: { label: 'Idle', icon: null, color: 'bg-zinc-600' },
    parsing: { label: 'Parsing Problem', icon: Brain, color: 'bg-blue-500 animate-pulse' },
    generating: { label: 'Generating Solutions', icon: Code2, color: 'bg-purple-500 animate-pulse' },
    testing: { label: 'Running Tests', icon: TestTube, color: 'bg-yellow-500 animate-pulse' },
    judging: { label: 'Judging Solutions', icon: Scale, color: 'bg-orange-500 animate-pulse' },
    synthesizing: { label: 'Creating Hybrid', icon: Sparkles, color: 'bg-pink-500 animate-pulse' },
    complete: { label: 'Complete', icon: CheckCircle2, color: 'bg-green-500' },
    error: { label: 'Error', icon: null, color: 'bg-red-500' },
  };

  const currentStatus = statusConfig[status];
  const StatusIcon = currentStatus.icon;

  return (
    <div className="space-y-6">
      {/* Status Bar */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Badge className={`${currentStatus.color} text-white`}>
                {StatusIcon && <StatusIcon className="w-4 h-4 mr-2" />}
                {currentStatus.label}
              </Badge>
              {problem && (
                <span className="text-sm text-muted-foreground">
                  {problem.test_count} test cases
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Problem Display */}
      {problem && (
        <Card>
          <CardContent className="py-4 space-y-3">
            <div>
              <h2 className="text-2xl font-bold mb-2">{problem.title}</h2>
              <p className="text-muted-foreground">{problem.description}</p>
            </div>
            {problem.function_signature && (
              <div className="bg-zinc-100 dark:bg-zinc-900 p-3 rounded font-mono text-sm">
                {problem.function_signature}
              </div>
            )}
            {problem.constraints && problem.constraints.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Constraints:</p>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-0.5">
                  {problem.constraints.map((constraint, i) => (
                    <li key={i}>{constraint}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map(agent => (
          <AgentCard
            key={agent.personality.name}
            agent={agent}
          />
        ))}

        {/* Hybrid Solution Card (only shown when synthesis is complete) */}
        {synthesis && (
          <Card className="relative overflow-hidden border-2 border-purple-500 bg-gradient-to-br from-purple-500/5 to-transparent">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500" />
            <CardContent className="py-4 space-y-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-500" />
                <h3 className="font-bold text-lg">Hybrid Solution</h3>
              </div>

              <Badge className="bg-purple-500 text-white">Synthesized</Badge>

              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium">Approach: </span>
                  <span className="text-muted-foreground">{synthesis.approach}</span>
                </div>
                <div className="flex gap-2">
                  <span>Time: {synthesis.time_complexity}</span>
                  <span>Space: {synthesis.space_complexity}</span>
                </div>
              </div>

              {synthesis.code && (
                <div className="bg-zinc-900 p-3 rounded font-mono text-xs text-white max-h-64 overflow-y-auto">
                  <pre>{synthesis.code}</pre>
                </div>
              )}

              {synthesis.improvements && synthesis.improvements.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium">Key Improvements:</p>
                  <ul className="text-xs text-muted-foreground space-y-0.5">
                    {synthesis.improvements.slice(0, 3).map((improvement, i) => (
                      <li key={i} className="flex items-start gap-1">
                        <span className="text-purple-500">•</span>
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Scoreboard */}
      {agents.some(agent => agent.score) && (
        <Scoreboard agents={agents} synthesis={synthesis} />
      )}
    </div>
  );
}
