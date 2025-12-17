"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, GitBranch, GitCommit, User } from "lucide-react";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { cn } from "@/lib/utils";

interface Job {
    id: string;
    repo_url: string;
    commit_sha: string;
    pusher: string;
    branch: string;
    status: string;
    created_at: string;
}

interface Repository {
    id: number;
    name: string;
    github_url: string;
    active: boolean;
}

export default function DashboardPage() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [repos, setRepos] = useState<Repository[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [jobsRes, reposRes] = await Promise.all([
                    fetch("/api/jobs"),
                    fetch("/api/repositories")
                ]);

                if (jobsRes.ok) setJobs(await jobsRes.json());
                if (reposRes.ok) setRepos(await reposRes.json());
            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="container mx-auto p-6 space-y-8 max-w-7xl">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                    <p className="text-muted-foreground">Manage your repositories and view build status.</p>
                </div>
                <Button>
                    <Plus className="w-4 h-4 mr-2" /> Add Repository
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Repository List */}
                <Card className="md:col-span-1 h-fit">
                    <CardHeader>
                        <CardTitle>Repositories</CardTitle>
                        <CardDescription>{repos.length} Connected</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {repos.length === 0 ? (
                            <div className="text-sm text-muted-foreground py-4 text-center border border-dashed rounded-lg">
                                No repositories connected.
                            </div>
                        ) : (
                            repos.map((repo) => (
                                <div key={repo.id} className="flex items-center justify-between p-3 rounded-lg border bg-card/50 hover:bg-accent/50 transition-colors">
                                    <div className="flex flex-col overflow-hidden">
                                        <span className="font-medium truncate">{repo.name}</span>
                                        <span className="text-xs text-muted-foreground truncate">{repo.github_url}</span>
                                    </div>
                                    <div className={`w-2 h-2 rounded-full ${repo.active ? 'bg-green-500' : 'bg-gray-300'}`} />
                                </div>
                            ))
                        )}
                    </CardContent>
                </Card>

                {/* Recent Jobs */}
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                        <CardDescription>Latest CI pipeline runs</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-0">
                        {loading && jobs.length === 0 ? (
                            <div className="space-y-4">
                                {[1, 2, 3].map((i) => (
                                    <div key={i} className="h-16 bg-muted/50 rounded-lg animate-pulse" />
                                ))}
                            </div>
                        ) : jobs.length === 0 ? (
                            <div className="text-center py-12 text-muted-foreground">
                                No jobs found.
                            </div>
                        ) : (
                            <div className="divide-y border rounded-lg overflow-hidden">
                                {jobs.map((job) => (
                                    <Link
                                        key={job.id}
                                        href={`/job?id=${job.id}`}
                                        className="flex items-center p-4 hover:bg-muted/50 transition-colors gap-4 group"
                                    >
                                        <StatusBadge status={job.status} />

                                        <div className="flex-1 min-w-0 grid gap-1">
                                            <div className="flex items-center gap-2">
                                                <span className="font-mono text-sm font-medium">{job.commit_sha.substring(0, 7)}</span>
                                                <span className="text-muted-foreground text-xs">•</span>
                                                <span className="text-sm font-medium truncate">{job.repo_url.split('/').pop()?.replace('.git', '')}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                                <span className="flex items-center gap-1">
                                                    <GitBranch className="w-3 h-3" /> {job.branch}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <User className="w-3 h-3" /> {job.pusher}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <GitCommit className="w-3 h-3" /> {new Date(job.created_at).toLocaleTimeString()}
                                                </span>
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
