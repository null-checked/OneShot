# Code Arena - Frontend

A Next.js 16 application for the Multi-Agent Competitive Code Arena. Watch AI agents compete to solve coding problems in real-time.

## Features

- **Real-time WebSocket Communication**: Live updates as agents generate solutions
- **Agent Visualization**: See each agent's approach, code, and test results
- **Pixel-based Code Visualization**: Visual representation of code structure
- **Animated Test Runner**: Watch tests execute in real-time
- **Score Rankings**: Compare agents based on correctness, performance, and quality
- **Hybrid Solution**: See the synthesized "best-of" solution combining all approaches

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: Shadcn UI
- **Icons**: Lucide React
- **Real-time**: WebSockets

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main application page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── arena/
│   │   ├── Arena.tsx         # Main arena container
│   │   ├── AgentCard.tsx     # Individual agent display
│   │   ├── PixelGrid.tsx     # Code visualization
│   │   ├── TestRunner.tsx    # Test execution animation
│   │   └── Scoreboard.tsx    # Rankings display
│   └── ui/                   # Shadcn UI components
├── hooks/
│   └── useArenaSocket.ts     # WebSocket hook
├── lib/
│   ├── types.ts              # TypeScript type definitions
│   └── utils.ts              # Utility functions
└── utils/
    └── codeToPixels.ts       # Code-to-pixel conversion
```

## Getting Started

### Prerequisites

- Node.js >= 20.9.0
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Configuration

The WebSocket URL can be configured in `app/page.tsx`:

```typescript
const { /* ... */ } = useArenaSocket({
  url: 'ws://localhost:8000/ws/arena', // Change this to your backend URL
  autoReconnect: true,
});
```

## Components

### Arena

Main container that orchestrates the entire arena view, including:
- Problem display
- Agent cards grid
- Hybrid solution card
- Scoreboard

### AgentCard

Displays individual agent information:
- Agent personality and color
- Current status (idle, thinking, testing, complete)
- Approach and complexity analysis
- Pixel visualization of code
- Test results with animated progress
- Score breakdown

### PixelGrid

Converts code into a visual pixel representation:
- Token-based coloring
- Different colors for keywords, strings, numbers, etc.
- Animated reveal during code generation

### TestRunner

Animated test execution visualization:
- Shows each test case as a colored square
- Animates from pending → running → passed/failed
- Displays execution time on hover

### Scoreboard

Rankings display showing:
- Sorted agents by total score
- Score breakdown (correctness, performance, quality)
- Winner highlighting
- Hybrid solution comparison

## WebSocket Protocol

The frontend expects WebSocket messages in the following format:

```typescript
{
  type: 'problem_parsed' | 'agent_start' | 'agent_complete' | 'test_results' | 'scores' | 'synthesis_complete' | 'error',
  data: { /* event-specific data */ }
}
```

### Event Types

1. **problem_parsed**: Problem has been analyzed
```json
{
  "type": "problem_parsed",
  "data": {
    "title": "Two Sum",
    "description": "...",
    "function_signature": "def two_sum(...)",
    "test_count": 6
  }
}
```

2. **agent_start**: Agent begins generating solution
```json
{
  "type": "agent_start",
  "data": { "agent": "RecursiveRex" }
}
```

3. **agent_complete**: Agent finished generating solution
```json
{
  "type": "agent_complete",
  "data": {
    "agent": "RecursiveRex",
    "approach_name": "Recursive with memoization",
    "code": "def solution(...)...",
    "time_complexity": "O(n)",
    "space_complexity": "O(n)"
  }
}
```

4. **test_results**: Test execution results
```json
{
  "type": "test_results",
  "data": {
    "agent_name": "RecursiveRex",
    "total_tests": 6,
    "passed_tests": 5,
    "results": [...],
    "avg_time_ms": 1.23
  }
}
```

5. **scores**: Final rankings
```json
{
  "type": "scores",
  "data": {
    "rankings": [
      {
        "rank": 1,
        "agent": "DynamicDana",
        "total": 87.5,
        "correctness": 100,
        "performance": 85,
        "quality": 70
      }
    ]
  }
}
```

6. **synthesis_complete**: Hybrid solution ready
```json
{
  "type": "synthesis_complete",
  "data": {
    "approach": "Hybrid DP with memoization",
    "code": "...",
    "improvements": [...]
  }
}
```

## Customization

### Adding New Agent Personalities

Edit `hooks/useArenaSocket.ts`:

```typescript
const DEFAULT_AGENTS: AgentPersonality[] = [
  { name: 'RecursiveRex', color: '#3498db', approach: 'Recursive' },
  { name: 'DynamicDana', color: '#2ecc71', approach: 'Dynamic Programming' },
  { name: 'GreedyGus', color: '#e74c3c', approach: 'Greedy' },
  // Add your new agent here
];
```

### Customizing Colors

Edit agent colors in the personality definitions, or modify the token colors in `utils/codeToPixels.ts`.

### Styling

The app uses Tailwind CSS. Customize colors and styles in:
- `app/globals.css` for global styles
- Component files for component-specific styling

## Development

### Type Checking

```bash
npx tsc --noEmit
```

### Linting

```bash
npm run lint
```

### Building

```bash
npm run build
```

## Troubleshooting

### WebSocket Connection Issues

1. Ensure the backend server is running
2. Check the WebSocket URL in `app/page.tsx`
3. Verify CORS settings on the backend

### UI Not Updating

1. Check browser console for WebSocket errors
2. Verify message format matches expected protocol
3. Ensure React components are properly re-rendering

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
- [Shadcn UI Documentation](https://ui.shadcn.com) - learn about the UI component library

## License

MIT
