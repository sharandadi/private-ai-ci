import { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import { CheckCircle2, XCircle, Clock, Loader2 } from "lucide-react";

type Status = "success" | "failed" | "running" | "queued" | string;

interface StatusBadgeProps extends ComponentProps<"div"> {
    status: Status;
}

export function StatusBadge({ status, className, ...props }: StatusBadgeProps) {
    const normalizedStatus = status.toLowerCase();

    let icon = <Clock className="w-3 h-3" />;
    let colorClass = "bg-muted text-muted-foreground border-transparent";

    if (normalizedStatus === "success") {
        icon = <CheckCircle2 className="w-3 h-3" />;
        colorClass = "bg-green-500/15 text-green-500 border-green-500/20";
    } else if (normalizedStatus === "failed") {
        icon = <XCircle className="w-3 h-3" />;
        colorClass = "bg-red-500/15 text-red-500 border-red-500/20";
    } else if (normalizedStatus === "running") {
        icon = <Loader2 className="w-3 h-3 animate-spin" />;
        colorClass = "bg-blue-500/15 text-blue-500 border-blue-500/20";
    }

    return (
        <div
            className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors",
                colorClass,
                className
            )}
            {...props}
        >
            {icon}
            <span className="capitalize">{status}</span>
        </div>
    );
}
