'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trophy, Medal, Award } from 'lucide-react';
import type { AgentState, SynthesisResult } from '@/lib/types';

interface ScoreboardProps {
  agents: AgentState[];
  synthesis?: SynthesisResult;
}

export function Scoreboard({ agents, synthesis }: ScoreboardProps) {
  // Get agents with scores and sort by rank
  const rankedAgents = agents
    .filter(agent => agent.score)
    .sort((a, b) => (a.score?.rank || 0) - (b.score?.rank || 0));

  if (rankedAgents.length === 0) {
    return null;
  }

  // Medal icons for top 3
  const getMedalIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-5 h-5 text-yellow-500" />;
      case 2:
        return <Medal className="w-5 h-5 text-zinc-400" />;
      case 3:
        return <Award className="w-5 h-5 text-amber-600" />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="w-5 h-5" />
          Final Rankings
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {rankedAgents.map((agent, index) => {
            const score = agent.score!;
            const isWinner = score.rank === 1;

            return (
              <div
                key={agent.personality.name}
                className={`
                  relative p-4 rounded-lg border-2 transition-all
                  ${
                    isWinner
                      ? 'bg-gradient-to-r from-yellow-500/10 to-transparent border-yellow-500 animate-pulse'
                      : 'border-zinc-200 dark:border-zinc-800'
                  }
                `}
              >
                {/* Rank indicator */}
                <div className="absolute -left-3 -top-3 w-10 h-10 rounded-full bg-white dark:bg-zinc-900 border-2 flex items-center justify-center font-bold shadow-lg"
                  style={{ borderColor: agent.personality.color }}
                >
                  {getMedalIcon(score.rank) || `#${score.rank}`}
                </div>

                <div className="ml-4 space-y-2">
                  {/* Agent name and total score */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: agent.personality.color }}
                      />
                      <h3 className="font-semibold">{agent.personality.name}</h3>
                      {isWinner && (
                        <Badge variant="secondary" className="bg-yellow-500 text-white">
                          Winner
                        </Badge>
                      )}
                    </div>
                    <div className="text-2xl font-bold" style={{ color: agent.personality.color }}>
                      {score.total.toFixed(1)}
                    </div>
                  </div>

                  {/* Score breakdown */}
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div className="flex flex-col">
                      <span className="text-xs text-muted-foreground">Correctness</span>
                      <span className="font-semibold">{score.correctness.toFixed(1)}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs text-muted-foreground">Performance</span>
                      <span className="font-semibold">{score.performance.toFixed(1)}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs text-muted-foreground">Quality</span>
                      <span className="font-semibold">{score.quality.toFixed(1)}</span>
                    </div>
                  </div>

                  {/* Approach */}
                  {agent.solution && (
                    <p className="text-xs text-muted-foreground">
                      {agent.solution.approach_name} • {agent.solution.time_complexity}
                    </p>
                  )}

                  {/* Analysis */}
                  {score.analysis && (
                    <p className="text-xs text-muted-foreground italic mt-1">
                      {score.analysis}
                    </p>
                  )}
                </div>
              </div>
            );
          })}

          {/* Hybrid Solution */}
          {synthesis && (
            <div className="mt-6 p-4 rounded-lg border-2 border-purple-500 bg-gradient-to-r from-purple-500/10 to-transparent">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <h3 className="font-semibold">Hybrid Solution</h3>
                  <Badge variant="secondary" className="bg-purple-500 text-white">
                    Synthesized
                  </Badge>
                </div>

                <p className="text-xs text-muted-foreground">
                  {synthesis.approach} • {synthesis.time_complexity}
                </p>

                {synthesis.synthesis_reasoning && (
                  <div className="mt-2 space-y-1">
                    <p className="text-xs font-medium">Reasoning:</p>
                    <p className="text-xs text-muted-foreground italic">
                      {synthesis.synthesis_reasoning}
                    </p>
                  </div>
                )}

                {synthesis.improvements && synthesis.improvements.length > 0 && (
                  <div className="mt-2 space-y-1">
                    <p className="text-xs font-medium">Improvements:</p>
                    <ul className="text-xs text-muted-foreground space-y-0.5">
                      {synthesis.improvements.map((improvement, i) => (
                        <li key={i} className="flex items-start gap-1">
                          <span className="text-purple-500">•</span>
                          <span>{improvement}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
