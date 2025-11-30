"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// Types
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

export interface ProjectResult {
    status: string;
    project_name: string;
    project_path: string;
    files_count: number;
    download_url: string;
    review_score?: number;
    tests_passed?: number;
}

export interface Project {
    name: string;
    path: string;
    files_count: number;
    size_bytes: number;
}

export interface ProjectDetails extends Project {
    project_name: string;
    project_path: string;
    total_files: number;
    total_size_bytes: number;
    files: string[];
    readme: string;
}

interface WSMessage {
    type: "connected" | "progress" | "substep" | "heartbeat" | "complete" | "error";
    message?: string;
    step?: number;
    substep?: string;
    data?: any;
    error?: string;
    current_step?: number;
    last_substep?: string;
}

interface UseProjectBuilderOptions {
    url?: string;
    autoReconnect?: boolean;
    reconnectInterval?: number;
}

interface ProjectBuilderReturn {
    connect: () => void;
    disconnect: () => void;
    buildProject: (prompt: string) => void;
    listProjects: () => void;
    getProjectDetails: (projectName: string) => void;
    isConnected: boolean;
    isBuilding: boolean;
    progress: BuildProgress | null;
    substeps: SubstepUpdate[];
    heartbeat: HeartbeatUpdate | null;
    result: ProjectResult | null;
    projects: Project[];
    projectDetails: ProjectDetails | null;
    error: string | null;
}

export function useProjectBuilder(options: UseProjectBuilderOptions = {}): ProjectBuilderReturn {
    const { url = "ws://localhost:8000/ws", autoReconnect = true, reconnectInterval = 3000 } = options;

    const [isConnected, setIsConnected] = useState(false);
    const [isBuilding, setIsBuilding] = useState(false);
    const [progress, setProgress] = useState<BuildProgress | null>(null);
    const [substeps, setSubsteps] = useState<SubstepUpdate[]>([]);
    const [heartbeat, setHeartbeat] = useState<HeartbeatUpdate | null>(null);
    const [result, setResult] = useState<ProjectResult | null>(null);
    const [projects, setProjects] = useState<Project[]>([]);
    const [projectDetails, setProjectDetails] = useState<ProjectDetails | null>(null);
    const [error, setError] = useState<string | null>(null);

    const ws = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
    const shouldReconnect = useRef(false);
    const connectRef = useRef<(() => void) | null>(null);

    // Handle incoming WebSocket messages
    const handleMessage = useCallback((event: MessageEvent) => {
        console.log("WebSocket message received:", event.data);

        try {
            const message: WSMessage = JSON.parse(event.data);

            switch (message.type) {
                case "connected":
                    console.log("WebSocket connected:", message.message);
                    break;

                case "progress":
                    if (message.step && message.message) {
                        setProgress({
                            step: message.step,
                            message: message.message,
                            data: message.data,
                        });
                    }
                    break;

                case "substep":
                    if (message.step && message.substep && message.message) {
                        const substepUpdate: SubstepUpdate = {
                            step: message.step,
                            substep: message.substep,
                            message: message.message,
                            data: message.data,
                        };
                        setSubsteps((prev) => [...prev, substepUpdate]);
                    }
                    break;

                case "heartbeat":
                    if (message.current_step !== undefined && message.last_substep) {
                        setHeartbeat({
                            current_step: message.current_step,
                            last_substep: message.last_substep,
                        });
                    }
                    break;

                case "complete":
                    setIsBuilding(false);
                    setProgress(null);

                    // Handle different response types
                    if (message.data) {
                        // Build complete
                        if (message.data.project_name) {
                            setResult(message.data as ProjectResult);
                        }
                        // List projects
                        else if (message.data.projects) {
                            setProjects(message.data.projects);
                        }
                        // Project details
                        else if (message.data.total_files !== undefined) {
                            setProjectDetails(message.data as ProjectDetails);
                        }
                    }
                    break;

                case "error":
                    setIsBuilding(false);
                    setProgress(null);
                    setError(message.error || "An unknown error occurred");
                    break;

                default:
                    console.warn("Unknown message type:", message.type);
            }
        } catch (err) {
            console.error("Error parsing WebSocket message:", err);
            setError("Failed to parse server message");
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
                console.log("WebSocket connected to project builder");
            };

            ws.current.onmessage = handleMessage;

            ws.current.onerror = (event) => {
                console.error("WebSocket error:", event);
                setError("Connection error");
            };

            ws.current.onclose = () => {
                setIsConnected(false);
                console.log("WebSocket disconnected");

                // Auto-reconnect if enabled
                if (shouldReconnect.current && autoReconnect) {
                    reconnectTimeout.current = setTimeout(() => {
                        console.log("Attempting to reconnect...");
                        connectRef.current?.();
                    }, reconnectInterval);
                }
            };
        } catch (err) {
            console.error("Failed to create WebSocket:", err);
            setError("Failed to connect");
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

    // Build a new project
    const buildProject = useCallback((prompt: string) => {
        if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
            setError("Not connected to server");
            return;
        }

        try {
            setIsBuilding(true);
            setProgress(null);
            setSubsteps([]);
            setHeartbeat(null);
            setResult(null);
            setError(null);

            ws.current.send(
                JSON.stringify({
                    action: "build",
                    data: { prompt },
                })
            );
        } catch (err) {
            console.error("Failed to send build request:", err);
            setError("Failed to send build request");
            setIsBuilding(false);
        }
    }, []);

    // List all projects
    const listProjects = useCallback(() => {
        if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
            setError("Not connected to server");
            return;
        }

        try {
            setError(null);
            ws.current.send(
                JSON.stringify({
                    action: "list",
                    data: {},
                })
            );
        } catch (err) {
            console.error("Failed to list projects:", err);
            setError("Failed to list projects");
        }
    }, []);

    // Get project details
    const getProjectDetails = useCallback((projectName: string) => {
        if (!projectName) {
            setProjectDetails(null);
            return;
        }

        if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
            setError("Not connected to server");
            return;
        }

        try {
            setError(null);
            setProjectDetails(null);

            ws.current.send(
                JSON.stringify({
                    action: "details",
                    data: { project_name: projectName },
                })
            );
        } catch (err) {
            console.error("Failed to get project details:", err);
            setError("Failed to get project details");
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
        buildProject,
        listProjects,
        getProjectDetails,
        isConnected,
        isBuilding,
        progress,
        substeps,
        heartbeat,
        result,
        projects,
        projectDetails,
        error,
    };
}
