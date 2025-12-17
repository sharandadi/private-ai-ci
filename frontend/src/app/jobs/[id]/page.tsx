"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { LogViewer } from "@/components/dashboard/LogViewer";
import { ArrowLeft, FileText, Terminal } from "lucide-react";
import Link from "next/link";

interface JobDetail {
    id: string;
    repo_url: string;
    commit_sha: string;
    pusher: string;
    branch: string;
    status: string;
    created_at: string;
    report_content?: string;
}

interface LogEntry {
    job_id: string;
    content: string;
    timestamp: string;
}

export default function JobPage() {
    const params = useParams();
    const id = params.id as string;

    const [job, setJob] = useState<JobDetail | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [activeTab, setActiveTab] = useState<"logs" | "report">("logs");
    const [loading, setLoading] = useState(true);

    // Poll for Job Details
    useEffect(() => {
        const fetchJob = async () => {
            try {
                const res = await fetch(`/api/jobs/${id}`);
                if (res.ok) {
                    const data = await res.json();
                    setJob(data);
                    // If job is success/failed, we might switch to report tab automatically if wanted, but logs are safer default
                }
            } catch (err) {
                console.error(err);
            }
        };
        fetchJob();
        const interval = setInterval(fetchJob, 5000);
        return () => clearInterval(interval);
    }, [id]);

    // Poll for Logs
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch(`/api/jobs/${id}/logs`);
                if (res.ok) {
                    setLogs(await res.json());
                }
            } catch (err) {
                console.error(err);
            }
        };
        fetchLogs();
        // Poll more frequently for logs if job is running
        const interval = setInterval(fetchLogs, 2000);
        return () => clearInterval(interval);
    }, [id]);

    if (!job) {
        return (
            <div className="container mx-auto p-6 text-center text-muted-foreground">
                Loading job {id}...
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6 max-w-5xl">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" asChild>
                    <Link href="/dashboard"><ArrowLeft className="w-4 h-4" /></Link>
                </Button>
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold tracking-tight">Job {id}</h1>
                        <StatusBadge status={job.status} />
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                        {job.repo_url} on <span className="font-mono text-primary">{job.branch}</span>
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="md:col-span-3 space-y-6">
                    {/* Tabs Control */}
                    <div className="flex items-center gap-2 p-1 bg-muted/50 rounded-lg w-fit">
                        <button
                            onClick={() => setActiveTab("logs")}
                            className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === "logs" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                                }`}
                        >
                            <Terminal className="w-4 h-4" /> Live Logs
                        </button>
                        <button
                            onClick={() => setActiveTab("report")}
                            className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === "report" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                                }`}
                        >
                            <FileText className="w-4 h-4" /> AI Report
                        </button>
                    </div>

                    <Card className="min-h-[500px]">
                        {activeTab === "logs" ? (
                            <div className="p-0 h-full">
                                <LogViewer logs={logs} className="h-[600px] border-none rounded-none bg-black text-white" />
                            </div>
                        ) : (
                            <CardContent className="pt-6 prose prose-invert max-w-none">
                                {job.report_content ? (
                                    <div className="whitespace-pre-wrap font-sans">
                                        {/* In a real app, use a markdown renderer here */}
                                        {job.report_content}
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
                                        <p>No report generated yet.</p>
                                        {job.status === "running" && <p className="text-xs">Agents are working...</p>}
                                    </div>
                                )}
                            </CardContent>
                        )}
                    </Card>
                </div>

                <div className="md:col-span-1 space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-sm">Job Details</CardTitle>
                        </CardHeader>
                        <CardContent className="text-sm space-y-3">
                            <div>
                                <span className="text-muted-foreground block text-xs uppercase tracking-wider">Commit</span>
                                <span className="font-mono truncate block">{job.commit_sha}</span>
                            </div>
                            <div>
                                <span className="text-muted-foreground block text-xs uppercase tracking-wider">Triggered By</span>
                                <span>{job.pusher || "System"}</span>
                            </div>
                            <div>
                                <span className="text-muted-foreground block text-xs uppercase tracking-wider">Started</span>
                                <span>{new Date(job.created_at).toLocaleString()}</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
