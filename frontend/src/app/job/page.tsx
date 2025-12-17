"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { LogViewer } from "@/components/dashboard/LogViewer";
import { ArrowLeft, FileText, Terminal } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { Progress } from "@/components/ui/progress";

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

function JobPageContent() {
    const params = useSearchParams();
    const id = params.get('id');

    const [job, setJob] = useState<JobDetail | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [activeTab, setActiveTab] = useState<"logs" | "report">("logs");
    const [progress, setProgress] = useState(0);

    // Simulated Progress for Running Jobs
    useEffect(() => {
        if (job?.status === "running") {
            const duration = 120 * 1000; // 2 minutes estimated
            const intervalTime = 1000;
            const steps = duration / intervalTime;
            const increment = 90 / steps; // Target 90%

            const timer = setInterval(() => {
                setProgress((prev) => {
                    if (prev >= 90) return 90;
                    return prev + increment;
                });
            }, intervalTime);
            return () => clearInterval(timer);
        } else if (job?.status === "success" || job?.status === "failed") {
            setProgress(100);
        }
    }, [job?.status]);

    // Poll for Job Details
    useEffect(() => {
        const fetchJob = async () => {
            try {
                const res = await fetch(`/api/jobs/${id}`);
                if (res.ok) {
                    const data = await res.json();
                    setJob(data);
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
                    {/* Progress Bar for active jobs */}
                    {job.status === "running" && (
                        <div className="w-[200px] mt-2">
                            <Progress value={progress} className="h-1.5" />
                            <p className="text-[10px] text-muted-foreground mt-1 text-right">Est. {Math.round((progress / 90) * 120)}s elapsed</p>
                        </div>
                    )}
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
                            <CardContent className="pt-6">
                                {job.report_content ? (
                                    <div className="prose prose-invert max-w-none">
                                        <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                            {job.report_content}
                                        </ReactMarkdown>
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

export default function JobPage() {
    return (
        <Suspense fallback={<div className="p-6 text-center">Loading...</div>}>
            <JobPageContent />
        </Suspense>
    );
}
