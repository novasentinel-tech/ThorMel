"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { FileText, Clock } from "lucide-react"
import type { ScanHistoryEntry } from "@/lib/mock-data"

interface ScanHistoryTableProps {
  history: ScanHistoryEntry[]
  onViewReport: () => void
}

function getScoreColor(score: number) {
  if (score >= 80) return "text-risk-critical"
  if (score >= 60) return "text-risk-high"
  if (score >= 40) return "text-risk-medium"
  if (score >= 20) return "text-risk-low"
  return "text-risk-info"
}

function getScoreBg(score: number) {
  if (score >= 80) return "bg-risk-critical/10"
  if (score >= 60) return "bg-risk-high/10"
  if (score >= 40) return "bg-risk-medium/10"
  if (score >= 20) return "bg-risk-low/10"
  return "bg-risk-info/10"
}

export function ScanHistoryTable({ history, onViewReport }: ScanHistoryTableProps) {
  return (
    <Card className="border-border/50 bg-card">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <Clock className="size-4 text-primary" />
          Historico de Scans
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-2">
          {history.map((entry) => (
            <div
              key={entry.id}
              className="flex items-center gap-4 rounded-lg bg-secondary/30 p-3 hover:bg-secondary/50 transition-colors group"
            >
              <div className={cn("size-10 rounded-lg flex items-center justify-center font-mono text-sm font-bold shrink-0", getScoreBg(entry.riskScore), getScoreColor(entry.riskScore))}>
                {entry.riskScore}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground font-mono truncate">
                  {entry.target}
                </p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-muted-foreground">
                    {new Date(entry.date).toLocaleDateString("pt-BR", {
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <Badge variant="outline" className="text-[10px] h-5 border-border text-muted-foreground">
                    {entry.scanType}
                  </Badge>
                </div>
              </div>
              <button
                onClick={() => onViewReport()}
                className="opacity-50 group-hover:opacity-100 transition-opacity text-primary hover:text-primary/80"
                aria-label={`Ver relatorio do scan ${entry.target}`}
              >
                <FileText className="size-4" />
              </button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

    