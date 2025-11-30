"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Code2, Play, RotateCcw, Wifi, WifiOff, Download, FileCode, CheckCircle2, Activity } from "lucide-react";
import { useProjectBuilder } from "@/hooks/useProjectBuilder";
import { SubstepsViewer } from "@/components/arena/SubstepsViewer";

export default function Home() {
    const [promptInput, setPromptInput] = useState("");

    const {
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
        error: socketError,
    } = useProjectBuilder({
        url: "ws://localhost:8000/ws",
        autoReconnect: true,
    });

    // Auto-connect on mount and load projects
    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    useEffect(() => {
        if (isConnected) {
            listProjects();
        }
    }, [isConnected, listProjects]);

    const handleBuildProject = () => {
        if (!promptInput.trim()) {
            return;
        }

        buildProject(promptInput);
    };

    const handleReset = () => {
        setPromptInput("");
    };

    // Example prompts
    const examplePrompts = [
        {
            title: "Todo List API",
            description: "Create a REST API for a todo list application using FastAPI with CRUD operations, SQLite database, and proper error handling.",
        },
        {
            title: "Weather Dashboard",
            description: "Build a web application that displays weather information using a public API, with a clean UI and search functionality.",
        },
        {
            title: "Task Scheduler",
            description: "Create a Python application that schedules and executes tasks at specified times with logging and error recovery.",
        },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-white to-zinc-100 dark:from-zinc-950 dark:via-zinc-900 dark:to-zinc-950">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg">
                            <Code2 className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">AI Project Builder</h1>
                            <p className="text-sm text-muted-foreground">Multi-Agent Software Factory</p>
                        </div>
                    </div>

                    {/* Connection Status */}
                    <Badge variant={isConnected ? "default" : "destructive"} className="gap-2">
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
                            <p className="text-red-600 dark:text-red-400 text-sm">Error: {socketError}</p>
                        </CardContent>
                    </Card>
                )}

                {/* Main Content */}
                <div className="max-w-4xl mx-auto space-y-6">
                    {/* Input Form */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Describe Your Project</CardTitle>
                            <CardDescription>Describe your project idea and our AI agents will build a complete application for you</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Textarea
                                placeholder="Example: Create a REST API for a todo list using FastAPI with SQLite database and full CRUD operations."
                                value={promptInput}
                                onChange={(e) => setPromptInput(e.target.value)}
                                className="min-h-[150px] text-sm"
                                disabled={isBuilding}
                            />

                            <div className="flex items-center gap-2">
                                <Button onClick={handleBuildProject} disabled={!promptInput.trim() || !isConnected || isBuilding} size="lg" className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600">
                                    <Play className="w-4 h-4 mr-2" />
                                    {isBuilding ? "Building..." : "Build Project"}
                                </Button>

                                {isBuilding && (
                                    <Button onClick={handleReset} variant="outline" size="lg">
                                        <RotateCcw className="w-4 h-4 mr-2" />
                                        Cancel
                                    </Button>
                                )}

                                {!isConnected && <p className="text-sm text-muted-foreground">Waiting for server connection...</p>}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Progress Display */}
                    {progress && (
                        <Card className="border-blue-200 dark:border-blue-900 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20">
                            <CardContent className="py-6 space-y-3">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium">{progress.message}</p>
                                    <Badge variant="secondary">Step {progress.step}/10</Badge>
                                </div>
                                <Progress value={(progress.step / 10) * 100} className="h-2" />
                                {heartbeat && (
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2 border-t">
                                        <Activity className="w-3 h-3 animate-pulse" />
                                        <span className="truncate">{heartbeat.last_substep}</span>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    )}

                    {/* Substeps Display */}
                    {substeps.length > 0 && <SubstepsViewer substeps={substeps} currentStep={progress?.step} />}

                    {/* Result Display */}
                    {result && (
                        <Card className="border-green-200 dark:border-green-900 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                                    <CardTitle className="text-green-700 dark:text-green-400">Project Built Successfully!</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-muted-foreground">Project Name</p>
                                        <p className="font-medium">{result.project_name}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Files Created</p>
                                        <p className="font-medium flex items-center gap-1">
                                            <FileCode className="w-4 h-4" />
                                            {result.files_count}
                                        </p>
                                    </div>
                                    {result.review_score && (
                                        <div>
                                            <p className="text-sm text-muted-foreground">Review Score</p>
                                            <p className="font-medium">⭐ {result.review_score.toFixed(1)}/10</p>
                                        </div>
                                    )}
                                    {result.tests_passed !== undefined && (
                                        <div>
                                            <p className="text-sm text-muted-foreground">Tests Passed</p>
                                            <p className="font-medium">✓ {result.tests_passed}</p>
                                        </div>
                                    )}
                                </div>
                                <Button className="w-full" asChild>
                                    <a href={`http://localhost:8000${result.download_url}`} download>
                                        <Download className="w-4 h-4 mr-2" />
                                        Download Project
                                    </a>
                                </Button>
                            </CardContent>
                        </Card>
                    )}

                    {/* Example Prompts */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Example Projects</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-3">
                                {examplePrompts.map((example, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setPromptInput(example.description)}
                                        className="text-left p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                        disabled={isBuilding}
                                    >
                                        <p className="font-medium text-sm">{example.title}</p>
                                        <p className="text-xs text-muted-foreground mt-1">{example.description}</p>
                                    </button>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recent Projects */}
                    {projects.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Recent Projects</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid gap-3">
                                    {projects.slice(0, 5).map((project) => (
                                        <div key={project.name} className="flex items-center justify-between p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors">
                                            <div className="flex-1">
                                                <p className="font-medium text-sm">{project.name}</p>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    {project.files_count} files • {(project.size_bytes / 1024).toFixed(1)} KB
                                                </p>
                                            </div>
                                            <Button variant="outline" size="sm" onClick={() => getProjectDetails(project.name)}>
                                                View Details
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Project Details Modal */}
                    {projectDetails && (
                        <Card className="border-blue-200 dark:border-blue-900">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle>{projectDetails.project_name}</CardTitle>
                                    <Button variant="ghost" size="sm" onClick={() => getProjectDetails("")}>
                                        Close
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-muted-foreground">Total Files</p>
                                        <p className="font-medium">{projectDetails.total_files}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Total Size</p>
                                        <p className="font-medium">{(projectDetails.total_size_bytes / 1024).toFixed(1)} KB</p>
                                    </div>
                                </div>
                                {projectDetails.files.length > 0 && (
                                    <div>
                                        <p className="text-sm font-medium mb-2">Files:</p>
                                        <div className="max-h-40 overflow-y-auto space-y-1">
                                            {projectDetails.files.map((file) => (
                                                <p key={file} className="text-xs font-mono text-muted-foreground">
                                                    {file}
                                                </p>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    )}

                    {/* Info Card */}
                    <Card className="border-blue-200 dark:border-blue-900 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20">
                        <CardContent className="py-6">
                            <h3 className="font-semibold mb-2 flex items-center gap-2">
                                <Code2 className="w-4 h-4 text-blue-600" />
                                How it works
                            </h3>
                            <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                                <li>Describe your project in natural language</li>
                                <li>AI agents analyze your requirements and conduct research</li>
                                <li>Multiple agents implement different parts of the project</li>
                                <li>Code is reviewed and tested automatically</li>
                                <li>Complete documentation is generated</li>
                                <li>Download your ready-to-use project as a zip file</li>
                            </ol>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
