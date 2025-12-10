"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ScanTerminal } from "@/components/scan-terminal"
import { ExecutionTimeline } from "@/components/execution-timeline"
import { VulnerabilityMap } from "@/components/vulnerability-map"
import { Badge } from "@/components/ui/badge"
import { Activity, Globe, Zap } from "lucide-react"
import type { RiskLevel } from "@/lib/mock-data"

interface ScannerStatus {
  id: string
  name: string
  status: "completed" | "running" | "pending"
}

interface FoundVuln {
  id: string
  name: string
  riskLevel: RiskLevel
}

interface RealTimeScanViewProps {
  logs: string[]
  scanners: ScannerStatus[]
  progress: number
  foundVulnerabilities: FoundVuln[]
  target: string
}

export function RealTimeScanView({
  logs,
  scanners,
  progress,
  foundVulnerabilities,
  target,
}: RealTimeScanViewProps) {
  const completedCount = scanners.filter((s) => s.status === "completed").length
  const runningCount = scanners.filter((s) => s.status === "running").length
  const totalCount = scanners.length

  return (
    <div className="flex flex-col gap-6">
      <Card className="border-border/50 bg-card overflow-hidden">
        <div className="h-1 bg-secondary">
          <div
            className="h-full bg-primary transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <CardContent className="py-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Activity className="size-5 text-primary animate-pulse" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-foreground">
                  Scan em Execucao
                </h2>
                <div className="flex items-center gap-2 mt-0.5">
                  <Globe className="size-3 text-muted-foreground" />
                  <span className="font-mono text-sm text-muted-foreground">
                    {target}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="border-primary/30 text-primary font-mono gap-1.5">
                <Zap className="size-3" />
                {completedCount}/{totalCount} scanners
              </Badge>
              {runningCount > 0 && (
                <Badge variant="outline" className="border-risk-medium/30 text-risk-medium font-mono animate-pulse">
                  {runningCount} rodando
                </Badge>
              )}
              <Badge variant="outline" className="border-risk-critical/30 text-risk-critical font-mono">
                {foundVulnerabilities.length} encontradas
              </Badge>
              <span className="text-lg font-bold font-mono text-foreground">
                {Math.round(progress)}%
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 flex flex-col gap-6">
          <ScanTerminal logs={logs} />
          <VulnerabilityMap vulnerabilities={foundVulnerabilities} />
        </div>
        <div>
          <ExecutionTimeline scanners={scanners} />
        </div>
      </div>
    </div>
  )
}

    