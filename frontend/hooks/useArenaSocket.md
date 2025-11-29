# useArenaSocket Hook Documentation

## Overview

The `useArenaSocket` hook manages WebSocket connections for the Code Arena application, handling real-time communication between the frontend and backend during coding competitions.

## Usage

```typescript
import { useArenaSocket } from "@/hooks/useArenaSocket";

function ArenaComponent() {
    const { connect, disconnect, sendProblem, arenaState, isConnected, error } = useArenaSocket({
        url: "ws://localhost:8000/ws/arena",
        autoReconnect: true,
        reconnectInterval: 3000,
    });

    // Connect on mount
    useEffect(() => {
        connect();
        return () => disconnect();
    }, []);

    // Send a problem
    const handleSubmit = (problem: string) => {
        sendProblem(problem, 3); // 3 agents
    };

    return (
        <div>
            <p>Connected: {isConnected}</p>
            {error && <p>Error: {error}</p>}
            <p>Arena Status: {arenaState.status}</p>
        </div>
    );
}
```

## Options

| Option              | Type      | Default                          | Description                              |
| ------------------- | --------- | -------------------------------- | ---------------------------------------- |
| `url`               | `string`  | `"ws://localhost:8000/ws/arena"` | WebSocket server URL                     |
| `autoReconnect`     | `boolean` | `true`                           | Automatically reconnect on disconnect    |
| `reconnectInterval` | `number`  | `3000`                           | Time in ms between reconnection attempts |

## Return Values

| Property      | Type                                            | Description                      |
| ------------- | ----------------------------------------------- | -------------------------------- |
| `connect`     | `() => void`                                    | Establishes WebSocket connection |
| `disconnect`  | `() => void`                                    | Closes WebSocket connection      |
| `sendProblem` | `(problem: string, numAgents?: number) => void` | Sends a problem to the arena     |
| `arenaState`  | `ArenaState`                                    | Current state of the arena       |
| `isConnected` | `boolean`                                       | WebSocket connection status      |
| `error`       | `string \| null`                                | Current error message, if any    |

## WebSocket Events

The hook listens for and handles the following WebSocket events from the server:

### Arena Status Events

#### `status`

Updates the overall arena stage.

**Data:**

```typescript
{
    stage: "idle" | "parsing" | "planning" | "coding" | "testing" | "synthesizing" | "complete" | "error";
}
```

**Effect:** Updates `arenaState.status`

---

#### `problem_parsed`

Received after the problem description is successfully parsed.

**Data:**

```typescript
{
  title?: string;
  description?: string;
  difficulty?: string;
  constraints?: string[];
  examples?: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
}
```

**Effect:** Updates `arenaState.problem`

---

### Architect Events

#### `architect_start`

The architect agent begins analyzing the problem and creating a plan.

**Data:** None

**Effect:** Sets `arenaState.architect.status` to `"planning"`

---

#### `architect_complete`

The architect has finished creating the implementation plan.

**Data:**

```typescript
{
  architecture?: string;
  components?: string[];
  approach?: string;
  considerations?: string[];
}
```

**Effect:**

-   Sets `arenaState.architect.status` to `"complete"`
-   Updates `arenaState.architect.plan`
-   Changes `arenaState.status` to `"coding"`

---

### Agent Events

#### `agent_task_assigned`

An agent receives their specific coding task.

**Data:**

```typescript
{
  agent: string;           // Agent name
  task: {
    description: string;   // Task description
    requirements: string[];
    priority: number;
  };
}
```

**Effect:** Updates the specific agent's `task` and sets status to `"idle"`

---

#### `agent_start`

An agent begins coding their solution.

**Data:**

```typescript
{
    agent: string; // Agent name
}
```

**Effect:** Sets the agent's status to `"coding"`

---

#### `agent_complete`

An agent finishes their initial code implementation.

**Data:**

```typescript
{
    agent: string; // Agent name
    approach_name: string; // Name of the approach used
    thinking: string; // Reasoning/explanation
    time_complexity: string; // Big O time complexity
    space_complexity: string; // Big O space complexity
    code: string; // The actual code
}
```

**Effect:**

-   Sets the agent's status to `"testing"`
-   Updates `agent.solution` with the provided data

---

#### `agent_retry`

An agent is retrying after failed tests.

**Data:**

```typescript
{
    agent: string; // Agent name
    retry_count: number; // Current retry attempt
    max_retries: number; // Maximum allowed retries
}
```

**Effect:**

-   Sets the agent's status to `"coding"`
-   Updates `retryCount` and `maxRetries`

---

### Testing Events

#### `test_start`

Testing begins for an agent's solution.

**Data:**

```typescript
{
    agent: string; // Agent name
}
```

**Effect:** Sets the agent's status to `"testing"`

---

#### `test_results`

Test execution results are available.

**Data:**

```typescript
{
  agent_name: string;
  passed: number;      // Number of tests passed
  failed: number;      // Number of tests failed
  total: number;       // Total number of tests
  test_cases?: Array<{
    id: string;
    input: any;
    expected: any;
    actual: any;
    passed: boolean;
    error?: string;
  }>;
}
```

**Effect:** Updates the agent's `testResults`

---

#### `test_feedback`

Feedback from test execution, including whether to proceed or retry.

**Data:**

```typescript
{
  agent: string;
  feedback: {
    passed: boolean;      // Overall pass/fail
    message: string;      // Feedback message
    suggestions?: string[];
    error_analysis?: string;
  };
}
```

**Effect:**

-   Updates the agent's `testFeedback`
-   Sets status to `"complete"` if passed, `"fixing"` if failed

---

### Scoring & Synthesis Events

#### `scores`

Final scores and rankings for all agents.

**Data:**

```typescript
{
    rankings: Array<{
        agent: string;
        score: number;
        passed_tests: number;
        total_tests: number;
        time_complexity_score: number;
        space_complexity_score: number;
        code_quality_score: number;
    }>;
}
```

**Effect:**

-   Sets `arenaState.status` to `"synthesizing"`
-   Updates each agent's `score` and sets status to `"complete"`

---

#### `synthesis_complete`

The final synthesized solution combining the best approaches.

**Data:**

```typescript
{
  winner?: string;
  best_approach?: string;
  combined_solution?: string;
  analysis?: string;
  final_code?: string;
  recommendations?: string[];
}
```

**Effect:**

-   Sets `arenaState.status` to `"complete"`
-   Updates `arenaState.synthesis`

---

### Error Events

#### `error`

An error occurred during arena execution.

**Data:**

```typescript
{
    message: string; // Error description
}
```

**Effect:**

-   Sets `arenaState.status` to `"error"`
-   Updates `arenaState.error` with the error message
-   Sets the hook's `error` state

---

## Agent Status Flow

```
idle → coding → testing → complete
  ↑       ↓
  └─── fixing ←┘
```

-   **idle**: Agent is waiting or task assigned
-   **coding**: Agent is writing code
-   **testing**: Code is being tested
-   **fixing**: Agent is fixing failed tests (retry)
-   **complete**: Agent finished successfully

## Arena Status Flow

```
idle → parsing → planning → coding → testing → synthesizing → complete
                                                                  ↓
                                                               error
```

## Default Agents

The hook initializes with three default agent personalities:

```typescript
[
    { name: "AlgoMaster", color: "#3498db", approach: "Algorithm Specialist" },
    { name: "CodeCrafter", color: "#2ecc71", approach: "Clean Code Expert" },
    { name: "SpeedDemon", color: "#e74c3c", approach: "Performance Optimizer" },
];
```

## Error Handling

-   Connection errors are stored in the `error` state
-   Failed reconnection attempts will retry based on `reconnectInterval`
-   Maximum retry count per agent: `DEFAULT_MAX_RETRIES = 5`
-   WebSocket errors trigger automatic reconnection if `autoReconnect` is enabled

## Notes

-   The hook automatically cleans up WebSocket connections on unmount
-   State updates are immutable and use functional state updates
-   All agent updates are name-matched to ensure correct agent receives updates
-   Unknown event types are logged as warnings but don't break execution
