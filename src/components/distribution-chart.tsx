"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  RadarChart,
  Radar as RadarComponent,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface DistributionChartProps {
  distribution: {
    critical: number
    high: number
    medium: number
    low: number
    info: number
  }
}

const RISK_COLORS: Record<string, string> = {
  critical: "var(--risk-critical)",
  high: "var(--risk-high)",
  medium: "var(--risk-medium)",
  low: "var(--risk-low)",
  info: "var(--risk-info)",
}

const RISK_LABELS: Record<string, string> = {
  critical: "Critico",
  high: "Alto",
  medium: "Medio",
  low: "Baixo",
  info: "Info",
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { name: string; value: number; color: string } }> }) {
  if (!active || !payload || !payload.length) return null
  const data = payload[0].payload
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 shadow-xl">
      <div className="flex items-center gap-2">
        <div className="size-2.5 rounded-full" style={{ backgroundColor: data.color }} />
        <span className="text-sm font-medium text-card-foreground">{data.name}</span>
      </div>
      <p className="text-xs text-muted-foreground mt-1">
        {data.value} vulnerabilidade{data.value !== 1 ? "s" : ""}
      </p>
    </div>
  )
}

export function DistributionChart({ distribution }: DistributionChartProps) {
  const data = Object.entries(distribution)
    .filter(([, value]) => value > 0)
    .map(([key, value]) => ({
      name: RISK_LABELS[key],
      value,
      color: RISK_COLORS[key],
    }))

  const total = data.reduce((sum, d) => sum + d.value, 0)

  const radarData = Object.entries(distribution).map(([key, value]) => ({
    subject: RISK_LABELS[key],
    value,
    fullMark: Math.max(...Object.values(distribution)) + 2,
  }))

  return (
    <Card className="border-border/50 bg-card h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Distribuicao por Risco
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="donut" className="w-full">
          <TabsList className="bg-secondary/50 h-8 mb-4">
            <TabsTrigger value="donut" className="text-xs h-6">Rosca</TabsTrigger>
            <TabsTrigger value="bar" className="text-xs h-6">Barras</TabsTrigger>
            <TabsTrigger value="radar" className="text-xs h-6">Radar</TabsTrigger>
          </TabsList>

          <TabsContent value="donut" className="mt-0">
            <div className="flex items-center gap-6">
              <div className="relative h-[200px] w-[200px] shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={4}
                      dataKey="value"
                      strokeWidth={0}
                      animationBegin={0}
                      animationDuration={800}
                    >
                      {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-3xl font-bold font-mono text-foreground">{total}</span>
                  <span className="text-xs text-muted-foreground">Total</span>
                </div>
              </div>
              <div className="flex flex-col gap-3 flex-1">
                {data.map((entry) => {
                  const percent = total > 0 ? Math.round((entry.value / total) * 100) : 0;
                  return (
                    <div key={entry.name} className="flex flex-col gap-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="size-2.5 rounded-full"
                            style={{ backgroundColor: entry.color }}
                          />
                          <span className="text-sm text-muted-foreground">
                            {entry.name}
                          </span>
                        </div>
                        <span className="text-sm font-bold font-mono text-foreground">
                          {entry.value}
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{
                            width: `${percent}%`,
                            backgroundColor: entry.color,
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="bar" className="mt-0">
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} layout="vertical" barSize={18}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" tick={{ fill: "var(--muted-foreground)", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis
                    dataKey="name"
                    type="category"
                    tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    width={60}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: "var(--accent)", opacity: 0.3 }} />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]} animationDuration={800}>
                    {data.map((entry, index) => (
                      <Cell key={`bar-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="radar" className="mt-0">
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="var(--border)" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  />
                  <PolarRadiusAxis tick={false} axisLine={false} />
                  <RadarComponent
                    dataKey="value"
                    stroke="var(--primary)"
                    fill="var(--primary)"
                    fillOpacity={0.15}
                    strokeWidth={2}
                    animationDuration={800}
                  />
                  <Tooltip content={<CustomTooltip />} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

    