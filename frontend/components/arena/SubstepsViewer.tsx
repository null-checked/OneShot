"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, FileCode, CheckCircle, Activity } from "lucide-react";
import { useState } from "react";
import type { SubstepUpdate } from "@/hooks/useProjectBuilder";

interface SubstepsViewerProps {
    substeps: SubstepUpdate[];
    currentStep?: number;
}

export function SubstepsViewer({ substeps, currentStep }: SubstepsViewerProps) {
    const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

    if (substeps.length === 0) {
        return null;
    }

    // Group substeps by step
    const stepGroups = substeps.reduce((acc, substep) => {
        if (!acc[substep.step]) {
            acc[substep.step] = [];
        }
        acc[substep.step].push(substep);
        return acc;
    }, {} as Record<number, SubstepUpdate[]>);

    const toggleStep = (step: number) => {
        const newExpanded = new Set(expandedSteps);
        if (newExpanded.has(step)) {
            newExpanded.delete(step);
        } else {
            newExpanded.add(step);
        }
        setExpandedSteps(newExpanded);
    };

    const getSubstepIcon = (substep: string) => {
        switch (substep) {
            case "done":
                return <CheckCircle className="w-3 h-3 text-green-500" />;
            case "file":
            case "written":
                return <FileCode className="w-3 h-3 text-blue-500" />;
            case "error":
                return <span className="text-red-500">✗</span>;
            default:
                return <Activity className="w-3 h-3 text-gray-500" />;
        }
    };

    const getSubstepBadge = (substep: string) => {
        const colors: Record<string, string> = {
            upcoming: "bg-gray-500",
            start: "bg-blue-500",
            done: "bg-green-500",
            file: "bg-indigo-500",
            written: "bg-purple-500",
            error: "bg-red-500",
        };
        return colors[substep] || "bg-gray-400";
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    Detailed Activity Log
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[400px] overflow-y-auto">
                {Object.entries(stepGroups).map(([step, stepSubsteps]) => {
                    const stepNum = parseInt(step);
                    const isExpanded = expandedSteps.has(stepNum);
                    const isActive = currentStep === stepNum;

                    return (
                        <div key={step} className="border rounded-lg overflow-hidden">
                            <button onClick={() => toggleStep(stepNum)} className={`w-full flex items-center justify-between p-3 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors ${isActive ? "bg-blue-50 dark:bg-blue-950/20" : ""}`}>
                                <div className="flex items-center gap-2">
                                    {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                                    <span className="font-medium text-sm">Step {stepNum}/10</span>
                                    <Badge variant="secondary" className="text-xs">
                                        {stepSubsteps.length} updates
                                    </Badge>
                                </div>
                            </button>

                            {isExpanded && (
                                <div className="p-3 bg-zinc-50 dark:bg-zinc-900/50 space-y-2">
                                    {stepSubsteps.map((substep, idx) => (
                                        <div key={idx} className="bg-white dark:bg-zinc-900 rounded p-2 space-y-2">
                                            <div className="flex items-start gap-2">
                                                {getSubstepIcon(substep.substep)}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <Badge className={`${getSubstepBadge(substep.substep)} text-white text-xs`}>{substep.substep}</Badge>
                                                        <span className="text-sm text-muted-foreground truncate">{substep.message}</span>
                                                    </div>

                                                    {/* Render data payload */}
                                                    {substep.data && (
                                                        <div className="mt-2 space-y-2">
                                                            {/* File snippets */}
                                                            {substep.data.snippets && (
                                                                <div className="space-y-1">
                                                                    <p className="text-xs text-muted-foreground">Generated {Object.keys(substep.data.snippets).length} files:</p>
                                                                    {Object.entries(substep.data.snippets)
                                                                        .slice(0, 3)
                                                                        .map(([filename, snippet]) => (
                                                                            <div key={filename} className="bg-zinc-100 dark:bg-zinc-800 rounded p-2">
                                                                                <p className="text-xs font-mono font-semibold mb-1">📄 {filename}</p>
                                                                                <pre className="text-xs font-mono text-muted-foreground overflow-x-auto whitespace-pre-wrap break-words">
                                                                                    {typeof snippet === "string" ? snippet.slice(0, 150) : String(snippet).slice(0, 150)}
                                                                                    {typeof snippet === "string" && snippet.length > 150 ? "..." : ""}
                                                                                </pre>
                                                                            </div>
                                                                        ))}
                                                                    {Object.keys(substep.data.snippets).length > 3 && <p className="text-xs text-muted-foreground">+ {Object.keys(substep.data.snippets).length - 3} more files</p>}
                                                                </div>
                                                            )}

                                                            {/* Single file */}
                                                            {substep.data.file && substep.data.snippet && (
                                                                <div className="bg-zinc-100 dark:bg-zinc-800 rounded p-2">
                                                                    <p className="text-xs font-mono font-semibold mb-1">📄 {substep.data.file}</p>
                                                                    <pre className="text-xs font-mono text-muted-foreground overflow-x-auto whitespace-pre-wrap break-words">
                                                                        {substep.data.snippet.slice(0, 150)}
                                                                        {substep.data.snippet.length > 150 ? "..." : ""}
                                                                    </pre>
                                                                </div>
                                                            )}

                                                            {/* Project path */}
                                                            {substep.data.project_path && (
                                                                <div className="bg-zinc-100 dark:bg-zinc-800 rounded p-2">
                                                                    <p className="text-xs font-mono">📁 {substep.data.project_path}</p>
                                                                </div>
                                                            )}

                                                            {/* Other data - render as key-value pairs */}
                                                            {!substep.data.snippets && !substep.data.file && !substep.data.project_path && Object.keys(substep.data).length > 0 && (
                                                                <div className="bg-zinc-100 dark:bg-zinc-800 rounded p-2 space-y-1.5">
                                                                    {Object.entries(substep.data).map(([key, value]) => {
                                                                        // Handle different value types
                                                                        const renderValue = (val: any, depth: number = 0): React.ReactNode => {
                                                                            if (val === null || val === undefined) {
                                                                                return <span className="text-gray-400 italic">null</span>;
                                                                            }

                                                                            if (typeof val === "string") {
                                                                                // Truncate very long strings
                                                                                if (val.length > 200) {
                                                                                    return (
                                                                                        <details className="inline">
                                                                                            <summary className="cursor-pointer text-blue-600 hover:text-blue-700">{val.slice(0, 100)}... (click to expand)</summary>
                                                                                            <div className="mt-1 pl-3 border-l-2 border-zinc-300 dark:border-zinc-600 whitespace-pre-wrap">{val}</div>
                                                                                        </details>
                                                                                    );
                                                                                }
                                                                                return val;
                                                                            }

                                                                            if (typeof val === "number" || typeof val === "boolean") {
                                                                                return String(val);
                                                                            }

                                                                            if (Array.isArray(val)) {
                                                                                if (val.length === 0) return "[]";
                                                                                if (val.length <= 5) {
                                                                                    return `[${val.map((v) => (typeof v === "string" ? v : JSON.stringify(v))).join(", ")}]`;
                                                                                }
                                                                                return (
                                                                                    <details className="inline">
                                                                                        <summary className="cursor-pointer text-blue-600 hover:text-blue-700">[{val.length} items] (click to expand)</summary>
                                                                                        <div className="mt-1 pl-3 space-y-0.5">
                                                                                            {val.slice(0, 10).map((item, i) => (
                                                                                                <div key={i}>• {typeof item === "string" ? item : JSON.stringify(item)}</div>
                                                                                            ))}
                                                                                            {val.length > 10 && <div className="text-gray-500">... and {val.length - 10} more</div>}
                                                                                        </div>
                                                                                    </details>
                                                                                );
                                                                            }

                                                                            if (typeof val === "object") {
                                                                                const keys = Object.keys(val);
                                                                                if (keys.length === 0) return "{}";
                                                                                if (depth > 0) {
                                                                                    return `{${keys.length} properties}`;
                                                                                }
                                                                                return (
                                                                                    <details className="inline">
                                                                                        <summary className="cursor-pointer text-blue-600 hover:text-blue-700">{"{" + keys.length + " properties}"} (click to expand)</summary>
                                                                                        <div className="mt-1 pl-3 border-l-2 border-zinc-300 dark:border-zinc-600 space-y-0.5">
                                                                                            {keys.slice(0, 10).map((k) => (
                                                                                                <div key={k} className="text-xs">
                                                                                                    <span className="font-medium">{k}:</span> <span className="text-muted-foreground">{renderValue(val[k], depth + 1)}</span>
                                                                                                </div>
                                                                                            ))}
                                                                                            {keys.length > 10 && <div className="text-gray-500">... and {keys.length - 10} more</div>}
                                                                                        </div>
                                                                                    </details>
                                                                                );
                                                                            }

                                                                            return String(val);
                                                                        };

                                                                        return (
                                                                            <div key={key} className="text-xs">
                                                                                <span className="font-semibold text-foreground">{key}:</span> <span className="text-muted-foreground">{renderValue(value)}</span>
                                                                            </div>
                                                                        );
                                                                    })}
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </CardContent>
        </Card>
    );
}
