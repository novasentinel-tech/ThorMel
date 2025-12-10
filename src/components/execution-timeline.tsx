"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import {
  CheckCircle2,
  Loader2,
  Clock,
  Wifi,
  Cpu,
  Bug,
  Code2,
  Shield,
  Lock,
  ShieldAlert,
  FolderSearch,

} from "lucide-react"
import type { LucideIcon } from "lucide-react"

interface ScannerInfo {
  id: string
  name: string
  status: "completed" | "running" | "pending"
}

interface ExecutionTimelineProps {
  scanners: ScannerInfo[]
}

const scannerIcons: Record<string, LucideIcon> = {
  port: Wifi,
  tech: Cpu,
  sqli: Bug,
  xss: Code2,
  headers: Shield,
  ssl: Lock,
  csrf: ShieldAlert,
  brute: ShieldAlert,
  dir: FolderSearch,
}

export function ExecutionTimeline({ scanners }: ExecutionTimelineProps) {
  const completedCount = scanners.filter((s) => s.status === "completed").length
  const totalCount = scanners.length

  return (
    <Card className="border-border/50 bg-card h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Clock className="size-4 text-primary" />
            Timeline
          </CardTitle>
          <span className="text-xs text-muted-foreground font-mono">
            {completedCount}/{totalCount}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col">
          {scanners.map((scanner, index) => {
            const Icon = scannerIcons[scanner.id] || Shield
            return (
              <div key={scanner.id} className="flex gap-3">
                {/* Timeline line */}
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "size-8 rounded-full flex items-center justify-center border-2 transition-all shrink-0",
                      scanner.status === "completed" && "border-risk-info bg-risk-info/10",
                      scanner.status === "running" && "border-primary bg-primary/10 shadow-[0_0_12px_var(--primary)]",
                      scanner.status === "pending" && "border-border/50 bg-background"
                    )}
                  >
                    {scanner.status === "completed" ? (
                      <CheckCircle2 className="size-4 text-risk-info" />
                    ) : scanner.status === "running" ? (
                      <Loader2 className="size-4 text-primary animate-spin" />
                    ) : (
                      <Icon className="size-3.5 text-muted-foreground/25" />
                    )}
                  </div>
                  {index < scanners.length - 1 && (
                    <div
                      className={cn(
                        "w-px flex-1 min-h-6 my-1",
                        scanner.status === "completed"
                          ? "bg-risk-info/30"
                          : "bg-border/30"
                      )}
                    />
                  )}
                </div>

                {/* Content */}
                <div className={cn(
                  "flex-1 pb-4 min-w-0",
                  index === scanners.length - 1 && "pb-0"
                )}>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "text-sm truncate",
                        scanner.status === "completed" && "text-foreground",
                        scanner.status === "running" && "text-primary font-semibold",
                        scanner.status === "pending" && "text-muted-foreground/30"
                      )}
                    >
                      {scanner.name}
                    </span>
                  </div>
                  <span
                    className={cn(
                      "text-[10px] uppercase tracking-wider font-medium",
                      scanner.status === "completed" && "text-risk-info",
                      scanner.status === "running" && "text-primary",
                      scanner.status === "pending" && "text-muted-foreground/20"
                    )}
                  >
                    {scanner.status === "completed" && "Concluido"}
                    {scanner.status === "running" && "Em execucao..."}
                    {scanner.status === "pending" && "Pendente"}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

    