'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { WSEvent, ArenaState, AgentPersonality, ArchitectState, AgentTask, TestFeedback } from '@/lib/types';

interface UseArenaSocketOptions {
  url?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

interface ArenaSocketReturn {
  connect: () => void;
  disconnect: () => void;
  sendProblem: (problem: string, numAgents?: number) => void;
  arenaState: ArenaState;
  isConnected: boolean;
  error: string | null;
}

// Default agent personalities
const DEFAULT_AGENTS: AgentPersonality[] = [
  { name: 'AlgoMaster', color: '#3498db', approach: 'Algorithm Specialist' },
  { name: 'CodeCrafter', color: '#2ecc71', approach: 'Clean Code Expert' },
  { name: 'SpeedDemon', color: '#e74c3c', approach: 'Performance Optimizer' },
];

const DEFAULT_MAX_RETRIES = 5;

const createInitialArchitectState = (): ArchitectState => ({
  status: 'idle',
});

const createInitialAgentState = (personality: AgentPersonality) => ({
  personality,
  status: 'idle' as const,
  retryCount: 0,
  maxRetries: DEFAULT_MAX_RETRIES,
});

export function useArenaSocket(options: UseArenaSocketOptions = {}): ArenaSocketReturn {
  const {
    url = 'ws://localhost:8000/ws/arena',
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [arenaState, setArenaState] = useState<ArenaState>({
    status: 'idle',
    architect: createInitialArchitectState(),
    agents: DEFAULT_AGENTS.map(createInitialAgentState),
  });

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnect = useRef(false);
  const connectRef = useRef<(() => void) | null>(null);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const wsEvent: WSEvent = JSON.parse(event.data);

      switch (wsEvent.type) {
        case 'status': {
          const data = wsEvent.data as { stage: ArenaState['status'] };
          setArenaState(prev => ({ ...prev, status: data.stage }));
          break;
        }

        case 'problem_parsed': {
          const data = wsEvent.data as ArenaState['problem'];
          setArenaState(prev => ({ ...prev, problem: data }));
          break;
        }

        case 'architect_start': {
          setArenaState(prev => ({
            ...prev,
            architect: { ...prev.architect, status: 'planning' },
          }));
          break;
        }

        case 'architect_complete': {
          const data = wsEvent.data as ArchitectState['plan'];
          setArenaState(prev => ({
            ...prev,
            status: 'coding',
            architect: { ...prev.architect, status: 'complete', plan: data },
          }));
          break;
        }

        case 'agent_task_assigned': {
          const data = wsEvent.data as { agent: string; task: AgentTask };
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data.agent
                ? { ...agent, task: data.task, status: 'idle' as const }
                : agent
            ),
          }));
          break;
        }

        case 'agent_start': {
          const data = wsEvent.data as { agent: string };
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data.agent
                ? { ...agent, status: 'coding' as const }
                : agent
            ),
          }));
          break;
        }

        case 'agent_complete': {
          const data = wsEvent.data as { agent: string } & ArenaState['agents'][0]['solution'];
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data.agent
                ? {
                    ...agent,
                    status: 'testing' as const,
                    solution: {
                      agent: data.agent,
                      approach_name: data.approach_name,
                      thinking: data.thinking,
                      time_complexity: data.time_complexity,
                      space_complexity: data.space_complexity,
                      code: data.code,
                    },
                  }
                : agent
            ),
          }));
          break;
        }

        case 'test_start': {
          const data = wsEvent.data as { agent: string };
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data.agent
                ? { ...agent, status: 'testing' as const }
                : agent
            ),
          }));
          break;
        }

        case 'test_results': {
          const data = wsEvent.data as ArenaState['agents'][0]['testResults'];
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data?.agent_name
                ? { ...agent, testResults: data }
                : agent
            ),
          }));
          break;
        }

        case 'test_feedback': {
          const data = wsEvent.data as { agent: string; feedback: TestFeedback };
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data.agent
                ? { 
                    ...agent, 
                    testFeedback: data.feedback,
                    status: data.feedback.passed ? 'complete' as const : 'fixing' as const,
                  }
                : agent
            ),
          }));
          break;
        }

        case 'agent_retry': {
          const data = wsEvent.data as { agent: string; retry_count: number; max_retries: number };
          setArenaState(prev => ({
            ...prev,
            agents: prev.agents.map(agent =>
              agent.personality.name === data.agent
                ? { 
                    ...agent, 
                    status: 'coding' as const,
                    retryCount: data.retry_count,
                    maxRetries: data.max_retries,
                  }
                : agent
            ),
          }));
          break;
        }

        case 'scores': {
          const data = wsEvent.data as { rankings: ArenaState['agents'][0]['score'][] };
          setArenaState(prev => ({
            ...prev,
            status: 'synthesizing',
            agents: prev.agents.map(agent => {
              const score = data.rankings.find(s => s?.agent === agent.personality.name);
              return score
                ? { ...agent, status: 'complete' as const, score }
                : { ...agent, status: 'complete' as const };
            }),
          }));
          break;
        }

        case 'synthesis_complete': {
          const data = wsEvent.data as ArenaState['synthesis'];
          setArenaState(prev => ({
            ...prev,
            status: 'complete',
            synthesis: data,
          }));
          break;
        }

        case 'error': {
          const data = wsEvent.data as { message: string };
          setError(data.message);
          setArenaState(prev => ({ ...prev, status: 'error', error: data.message }));
          break;
        }

        default:
          console.warn('Unknown WebSocket event type:', wsEvent.type);
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
      setError('Failed to parse server message');
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        shouldReconnect.current = true;
        console.log('WebSocket connected');
      };

      ws.current.onmessage = handleMessage;

      ws.current.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error');
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');

        // Auto-reconnect if enabled
        if (shouldReconnect.current && autoReconnect) {
          reconnectTimeout.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connectRef.current?.();
          }, reconnectInterval);
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to connect');
    }
  }, [url, autoReconnect, reconnectInterval, handleMessage]);

  // Keep connectRef updated with the latest connect function
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    shouldReconnect.current = false;

    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }

    setIsConnected(false);
  }, []);

  // Send problem to arena
  const sendProblem = useCallback((problem: string, numAgents: number = 3) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      setError('Not connected to server');
      return;
    }

    try {
      // Reset state
      setArenaState({
        status: 'parsing',
        architect: createInitialArchitectState(),
        agents: DEFAULT_AGENTS.slice(0, numAgents).map(createInitialAgentState),
      });

      // Send problem
      ws.current.send(JSON.stringify({
        problem,
        num_agents: numAgents,
      }));

      setError(null);
    } catch (err) {
      console.error('Failed to send problem:', err);
      setError('Failed to send problem');
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    sendProblem,
    arenaState,
    isConnected,
    error,
  };
}
