import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Ghost, Zap } from "lucide-react";

export function Header() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 border-b bg-background/80 backdrop-blur-md">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 transition-opacity hover:opacity-80">
                    <Zap className="w-5 h-5 text-primary" />
                    <span className="font-bold tracking-tight">CodeLens</span>
                </Link>
                <nav className="flex items-center gap-4">
                    <Link href="/dashboard" className="text-sm font-medium hover:text-primary/80 transition-colors">
                        Dashboard
                    </Link>
                    <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:text-primary/80 transition-colors">
                        GitHub
                    </a>
                    <Button variant="default" size="sm" asChild>
                        <Link href="/setup">Setup</Link>
                    </Button>
                </nav>
            </div>
        </header>
    );
}
