"use client"

import { Card, CardContent } from "@/components/ui/card"
import { ShieldAlert, Radio, AlertTriangle, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"

interface StatCardProps {
  title: string
  value: number
  icon: "vulnerabilities" | "ports" | "warnings"
  trend?: "up" | "down" | "neutral"
  trendValue?: string
}

const iconMap = {
  vulnerabilities: ShieldAlert,
  ports: Radio,
  warnings: AlertTriangle,
}

const colorMap = {
  vulnerabilities: { text: "text-risk-critical", bg: "bg-risk-critical/10", border: "border-risk-critical/20" },
  ports: { text: "text-risk-medium", bg: "bg-risk-medium/10", border: "border-risk-medium/20" },
  warnings: { text: "text-risk-high", bg: "bg-risk-high/10", border: "border-risk-high/20" },
}

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
}

export function StatCard({ title, value, icon, trend = "neutral", trendValue }: StatCardProps) {
  const Icon = iconMap[icon]
  const colors = colorMap[icon]
  const TrendIcon = trendIcons[trend]

  return (
    <Card className={cn("border-border/50 bg-card group hover:border-border transition-colors overflow-hidden relative")}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {title}
            </span>
            <span className={cn("text-3xl font-bold font-mono tracking-tight", colors.text)}>
              {value}
            </span>
            {trendValue && (
              <div className="flex items-center gap-1 mt-1">
                <TrendIcon className={cn(
                  "size-3",
                  trend === "up" ? "text-risk-critical" : trend === "down" ? "text-risk-info" : "text-muted-foreground"
                )} />
                <span className="text-xs text-muted-foreground">{trendValue}</span>
              </div>
            )}
          </div>
          <div className={cn("size-10 rounded-lg flex items-center justify-center", colors.bg, "border", colors.border)}>
            <Icon className={cn("size-5", colors.text)} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

    