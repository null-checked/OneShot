export interface WSEvent {
    type: string;
    data: any;
}

export interface BuildProgress {
    step: number;
    message: string;
    data?: any;
}

export interface SubstepUpdate {
    step: number;
    substep: string;
    message: string;
    data?: {
        file?: string;
        snippet?: string;
        files?: string[];
        snippets?: Record<string, string>;
        project_path?: string;
        [key: string]: any;
    };
}

export interface HeartbeatUpdate {
    current_step: number;
    last_substep: string;
}

export interface AgentPersonality {
    name: string;
    color: string;
    approach: string;
}

export interface ArchitectState {
    status: "idle" | "planning" | "complete";
    plan?: any;
}

export interface AgentTask {
    description: string;
}

export interface TestFeedback {
    passed: boolean;
    message?: string;
}

export interface ArenaState {
    status: "idle" | "parsing" | "planning" | "coding" | "testing" | "synthesizing" | "complete" | "error";
    problem?: any;
    architect: ArchitectState;
    agents: Array<{
        personality: AgentPersonality;
        status: "idle" | "coding" | "testing" | "fixing" | "complete";
        task?: AgentTask;
        solution?: {
            agent: string;
            approach_name: string;
            thinking: string;
            time_complexity: string;
            space_complexity: string;
            code: string;
        };
        testResults?: {
            agent_name: string;
        };
        testFeedback?: TestFeedback;
        retryCount: number;
        maxRetries: number;
        score?: {
            agent: string;
        };
    }>;
    synthesis?: any;
    error?: string;
}
