'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Swords, Play, RotateCcw, Wifi, WifiOff } from 'lucide-react';
import { Arena } from '@/components/arena/Arena';
import { useArenaSocket } from '@/hooks/useArenaSocket';

export default function Home() {
  const [problemInput, setProblemInput] = useState('');
  const [showArena, setShowArena] = useState(false);

  const {
    connect,
    disconnect,
    sendProblem,
    arenaState,
    isConnected,
    error: socketError,
  } = useArenaSocket({
    url: 'ws://localhost:8000/ws/arena',
    autoReconnect: true,
  });

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  const handleStartArena = () => {
    if (!problemInput.trim()) {
      return;
    }

    setShowArena(true);
    sendProblem(problemInput, 3);
  };

  const handleReset = () => {
    setShowArena(false);
    setProblemInput('');
  };

  // Example problems
  const exampleProblems = [
    {
      title: 'Two Sum',
      description: 'Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.',
    },
    {
      title: 'Fibonacci',
      description: 'Write a function that returns the nth Fibonacci number.',
    },
    {
      title: 'Palindrome Check',
      description: 'Given a string, determine if it is a palindrome, considering only alphanumeric characters and ignoring cases.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-white to-zinc-100 dark:from-zinc-950 dark:via-zinc-900 dark:to-zinc-950">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
              <Swords className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Code Arena
              </h1>
              <p className="text-sm text-muted-foreground">
                Multi-Agent Competitive Programming
              </p>
            </div>
          </div>

          {/* Connection Status */}
          <Badge variant={isConnected ? 'default' : 'destructive'} className="gap-2">
            {isConnected ? (
              <>
                <Wifi className="w-3 h-3" />
                Connected
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3" />
                Disconnected
              </>
            )}
          </Badge>
        </div>

        {/* Error Display */}
        {socketError && (
          <Card className="mb-6 border-red-500 bg-red-50 dark:bg-red-950/20">
            <CardContent className="py-4">
              <p className="text-red-600 dark:text-red-400 text-sm">
                Error: {socketError}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Input Form or Arena */}
        {!showArena ? (
          <div className="max-w-4xl mx-auto space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Enter a Coding Problem</CardTitle>
                <CardDescription>
                  Describe a programming problem and watch multiple AI agents compete to solve it
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Example: Write a function that finds the longest palindromic substring in a given string."
                  value={problemInput}
                  onChange={(e) => setProblemInput(e.target.value)}
                  className="min-h-[150px] font-mono text-sm"
                />

                <div className="flex items-center gap-2">
                  <Button
                    onClick={handleStartArena}
                    disabled={!problemInput.trim() || !isConnected}
                    size="lg"
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Arena
                  </Button>

                  {!isConnected && (
                    <p className="text-sm text-muted-foreground">
                      Waiting for server connection...
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Example Problems */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Example Problems</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3">
                  {exampleProblems.map((example, index) => (
                    <button
                      key={index}
                      onClick={() => setProblemInput(example.description)}
                      className="text-left p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors"
                    >
                      <p className="font-medium text-sm">{example.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {example.description}
                      </p>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Info Card */}
            <Card className="border-purple-200 dark:border-purple-900 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
              <CardContent className="py-6">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Swords className="w-4 h-4 text-purple-600" />
                  How it works
                </h3>
                <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                  <li>Enter a coding problem in natural language</li>
                  <li>Three AI agents with different approaches generate solutions</li>
                  <li>Each solution is tested and evaluated</li>
                  <li>A judge ranks them based on correctness, performance, and quality</li>
                  <li>A synthesizer creates a hybrid &quot;best-of&quot; solution</li>
                </ol>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Arena Controls */}
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Arena in Progress</h2>
              <Button
                onClick={handleReset}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                New Problem
              </Button>
            </div>

            {/* Arena Component */}
            <Arena arenaState={arenaState} />
          </div>
        )}
      </div>
    </div>
  );
}
