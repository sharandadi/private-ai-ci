"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface LogViewerProps {
    logs: { timestamp: string; content: string }[];
    className?: string;
}

export function LogViewer({ logs, className }: LogViewerProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    return (
        <div className={cn("bg-black rounded-lg border border-neutral-800 font-mono text-sm p-4 overflow-y-auto max-h-[600px]", className)}>
            {logs.length === 0 ? (
                <span className="text-neutral-500 italic">Waiting for logs...</span>
            ) : (
                <div className="flex flex-col space-y-1">
                    {logs.map((log, i) => (
                        <div key={i} className="flex gap-4 group hover:bg-white/5 px-2 -mx-2 rounded">
                            <span className="text-neutral-500 shrink-0 select-none">
                                {new Date(log.timestamp).toLocaleTimeString()}
                            </span>
                            <span className="text-neutral-200 whitespace-pre-wrap break-all">{log.content}</span>
                        </div>
                    ))}
                    <div ref={bottomRef} />
                </div>
            )}
        </div>
    );
}
