"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import type { ScanHistoryEntry } from "@/lib/mock-data"
import { TrendingUp } from "lucide-react"

interface ScanTrendChartProps {
  history: ScanHistoryEntry[]
}

function TrendTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { target: string; score: number; date: string } }> }) {
  if (!active || !payload || !payload.length) return null
  const data = payload[0].payload
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 shadow-xl">
      <p className="text-xs font-mono text-muted-foreground">{data.target}</p>
      <p className="text-sm font-bold text-foreground mt-1">Score: {data.score}</p>
      <p className="text-xs text-muted-foreground">{data.date}</p>
    </div>
  )
}

export function ScanTrendChart({ history }: ScanTrendChartProps) {
  const data = [...history].reverse().map((entry) => ({
    target: new URL(entry.target).hostname,
    score: entry.riskScore,
    date: new Date(entry.date).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
    }),
    label: new URL(entry.target).hostname.split(".")[0],
  }))

  return (
    <Card className="border-border/50 bg-card">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <TrendingUp className="size-4 text-primary" />
          Tendencia de Risco
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--risk-high)" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="var(--risk-high)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={35}
              />
              <Tooltip content={<TrendTooltip />} />
              <Area
                type="monotone"
                dataKey="score"
                stroke="var(--risk-high)"
                strokeWidth={2}
                fill="url(#riskGradient)"
                dot={{ fill: "var(--risk-high)", strokeWidth: 0, r: 4 }}
                activeDot={{ fill: "var(--risk-high)", strokeWidth: 2, stroke: "var(--card)", r: 6 }}
                animationDuration={1000}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

    