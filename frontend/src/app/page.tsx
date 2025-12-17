import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Terminal, Shield, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center items-center text-center p-8 space-y-8 max-w-4xl mx-auto">
        <div className="space-y-4">
          <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-6 bg-gradient-to-b from-foreground to-foreground/50 bg-clip-text text-transparent">
            CodeLens
          </h1>
          <p className="text-xl text-muted-foreground max-w-[600px] mb-8">
            The Private, Autonomous CI/CD Pipeline.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <Button size="lg" className="h-12 px-8 text-base" asChild>
            <Link href="/setup">
              Get Started <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" className="h-12 px-8 text-base" asChild>
            <Link href="/dashboard">
              View Dashboard
            </Link>
          </Button>
        </div>
      </section>

      {/* Access Denied / Features Teaser */}
      <section className="grid md:grid-cols-3 gap-8 p-8 max-w-6xl mx-auto w-full">
        <div className="p-6 rounded-2xl bg-card border shadow-sm">
          <Shield className="w-10 h-10 mb-4 text-primary" />
          <h3 className="text-xl font-bold mb-2">Private & Secure</h3>
          <p className="text-muted-foreground">
            Runs locally. Your code never leaves your machine unless you want it to. Secure HMAC webhooks.
          </p>
        </div>
        <div className="p-6 rounded-2xl bg-card border shadow-sm">
          <Zap className="w-10 h-10 mb-4 text-primary" />
          <h3 className="text-xl font-bold mb-2">Zero Config</h3>
          <p className="text-muted-foreground">
            No complex YAML files. Just connect your repo and let the AI agents figure out the rest.
          </p>
        </div>
        <div className="p-6 rounded-2xl bg-card border shadow-sm">
          <Terminal className="w-10 h-10 mb-4 text-primary" />
          <h3 className="text-xl font-bold mb-2">Deep Insights</h3>
          <p className="text-muted-foreground">
            Get intelligent reports on your code structure, bugs, and potential optimizations.
          </p>
        </div>
      </section>
    </div>
  );
}
