"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Copy, ArrowRight, Loader2, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SetupPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [webhookData, setWebhookData] = useState<{ webhook_url: string; webhook_secret: string } | null>(null);
    const [error, setError] = useState("");

    const handleAutoSetup = async () => {
        setLoading(true);
        setError("");
        try {
            // Complete setup without asking for API key (Backend managed)
            const res = await fetch("/api/setup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({}),
            });

            if (!res.ok) throw new Error("Setup failed");

            // Fetch webhook details
            const webhookRes = await fetch("/api/webhook-url");
            if (webhookRes.ok) {
                setWebhookData(await webhookRes.json());
                setStep(2);
            }
        } catch (err) {
            setError("Failed to complete setup. Is the backend running?");
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <div className="container mx-auto flex items-center justify-center min-h-[calc(100vh-4rem)] p-4">
            <Card className="w-full max-w-lg">
                <CardHeader>
                    <CardTitle>Setup CodeLens</CardTitle>
                    <CardDescription>Configure your CodeLens environment.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {step === 1 && (
                        <div className="space-y-4">
                            <div className="bg-muted/50 p-4 rounded-lg flex items-start gap-3">
                                <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                                <div>
                                    <h4 className="font-medium">System Check</h4>
                                    <p className="text-sm text-muted-foreground">Backend detected. Gemini API is managed centrally.</p>
                                </div>
                            </div>

                            {error && (
                                <div className="bg-red-500/10 text-red-500 p-3 rounded-lg flex items-center gap-2 text-sm">
                                    <AlertCircle className="w-4 h-4" /> {error}
                                </div>
                            )}
                        </div>
                    )}

                    {step === 2 && webhookData && (
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Webhook URL</label>
                                <div className="flex bg-muted rounded-md border text-sm font-mono overflow-hidden">
                                    <input
                                        readOnly
                                        value={webhookData.webhook_url}
                                        className="flex-1 bg-transparent px-3 py-2 outline-none"
                                    />
                                    <button
                                        onClick={() => copyToClipboard(webhookData.webhook_url)}
                                        className="px-3 hover:bg-background border-l transition-colors"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                                <p className="text-xs text-muted-foreground">Add this to your GitHub repository settings under Webhooks.</p>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Webhook Secret</label>
                                <div className="flex bg-muted rounded-md border text-sm font-mono overflow-hidden">
                                    <input
                                        readOnly
                                        value={webhookData.webhook_secret}
                                        className="flex-1 bg-transparent px-3 py-2 outline-none"
                                    />
                                    <button
                                        onClick={() => copyToClipboard(webhookData.webhook_secret)}
                                        className="px-3 hover:bg-background border-l transition-colors"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </CardContent>
                <CardFooter className="flex justify-end">
                    {step === 1 ? (
                        <Button onClick={handleAutoSetup} disabled={loading}>
                            {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                            Continue <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    ) : (
                        <Button asChild>
                            <Link href="/dashboard">Finish & Go to Dashboard</Link>
                        </Button>
                    )}
                </CardFooter>
            </Card>
        </div>
    );
}
