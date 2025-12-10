"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { RiskScoreGauge } from "@/components/risk-score-gauge"
import { cn } from "@/lib/utils"
import {
  getRiskBgColorClass,
  getRiskLabel,
  type ScanResult,
} from "@/lib/mock-data"
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
} from "recharts"
import {
  Calendar,
  Globe,
  Bug,
  ShieldCheck,
  Lightbulb,
  FileCode2,
  Server,
  Code2,
  Layers,
  Monitor,
  LayoutGrid,
  Terminal,
  Filter,
  ShieldAlert,
  Radio,
  AlertTriangle,
  Clock,
  Target,
  Fingerprint,
  BarChart3,
  FileText,
  ChevronRight,
} from "lucide-react"
import { VulnerabilityAnalysisView } from "@/components/vulnerability-analysis-view"

const RISK_COLORS: Record<string, string> = {
  critical: "var(--risk-critical)",
  high: "var(--risk-high)",
  medium: "var(--risk-medium)",
  low: "var(--risk-low)",
  info: "var(--risk-info)",
}

interface ReportViewProps {
  scanResult: ScanResult
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { name: string; value: number; color?: string } }> }) {
  if (!active || !payload || !payload.length) return null
  const data = payload[0].payload
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 shadow-xl">
      <span className="text-sm font-medium text-card-foreground">{data.name}: {data.value}</span>
    </div>
  )
}

export function ReportView({ scanResult }: ReportViewProps) {
  const [riskFilter, setRiskFilter] = useState<string>("all")
  const [scannerFilter, setScannerFilter] = useState<string>("all")

  const filteredVulnerabilities = useMemo(() => {
      if (!scanResult || !scanResult.vulnerabilities) return [];
      return scanResult.vulnerabilities.filter((vuln) => {
        const matchesRisk = riskFilter === "all" || vuln.riskLevel === riskFilter
        const matchesScanner = scannerFilter === "all" || vuln.scanner === scannerFilter
        return matchesRisk && matchesScanner
      })
    }, [scanResult, riskFilter, scannerFilter]);


  const uniqueScanners = useMemo(() => {
    if (!scanResult || !scanResult.vulnerabilities) return [];
    return Array.from(new Set(scanResult.vulnerabilities.map((v) => v.scanner)))
  }, [scanResult]);

  const distributionData = useMemo(() => {
    if (!scanResult || !scanResult.distribution) return [];
    return Object.entries(scanResult.distribution)
    .filter(([, value]) => value > 0)
    .map(([key, value]) => ({
      name: getRiskLabel(key as keyof typeof scanResult.distribution),
      value,
      color: RISK_COLORS[key],
    }))
  }, [scanResult]);

  const scannerStats = useMemo(() => {
    if (!scanResult || !scanResult.vulnerabilities) return [];
    const stats: Record<string, number> = {}
    scanResult.vulnerabilities.forEach((v) => {
      const shortName = v.scanner.replace(" Scanner", "")
      stats[shortName] = (stats[shortName] || 0) + 1
    })
    return Object.entries(stats).map(([name, value]) => ({ name, value }))
  }, [scanResult.vulnerabilities])

  const totalVulns = useMemo(() => {
    if (!scanResult || !scanResult.distribution) return 0;
    return Object.values(scanResult.distribution).reduce((a, b) => a + b, 0)
  }, [scanResult]);

  return (
    <div className="flex flex-col gap-6">
      {/* Header Summary */}
      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="border-border/50 bg-card lg:col-span-3 flex items-center justify-center p-6">
          <RiskScoreGauge score={scanResult.riskScore} size={190} />
        </Card>

        <Card className="border-border/50 bg-card lg:col-span-5">
          <CardContent className="p-6">
            <div className="flex flex-col gap-5">
              <div>
                <h2 className="text-xl font-bold text-foreground tracking-tight">
                  Relatorio Completo
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Analise detalhada de todas as vulnerabilidades encontradas
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-3 rounded-lg bg-secondary/50 p-3">
                  <Globe className="size-4 text-primary shrink-0" />
                  <div className="min-w-0">
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider block">Alvo</span>
                    <span className="text-sm font-mono text-foreground truncate block">{scanResult.target}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-secondary/50 p-3">
                  <Calendar className="size-4 text-primary shrink-0" />
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider block">Data</span>
                    <span className="text-sm font-mono text-foreground">
                      {new Date(scanResult.date).toLocaleDateString("pt-BR", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                      })}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-secondary/50 p-3">
                  <Target className="size-4 text-primary shrink-0" />
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider block">Tipo</span>
                    <span className="text-sm font-mono text-foreground">{scanResult.scanType}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-secondary/50 p-3">
                  <Clock className="size-4 text-primary shrink-0" />
                  <div>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider block">Horario</span>
                    <span className="text-sm font-mono text-foreground">
                      {new Date(scanResult.date).toLocaleTimeString("pt-BR", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Badge variant="outline" className="border-border text-muted-foreground font-mono gap-1">
                  <Fingerprint className="size-3" />
                  {scanResult.id}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="lg:col-span-4 flex flex-col gap-3">
          <Card className="border-border/50 bg-card flex-1">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="size-12 rounded-lg bg-risk-critical/10 border border-risk-critical/20 flex items-center justify-center">
                <ShieldAlert className="size-6 text-risk-critical" />
              </div>
              <div>
                <span className="text-2xl font-bold font-mono text-risk-critical">{scanResult.totalVulnerabilities}</span>
                <span className="text-xs text-muted-foreground block uppercase tracking-wider">Vulnerabilidades</span>
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/50 bg-card flex-1">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="size-12 rounded-lg bg-risk-medium/10 border border-risk-medium/20 flex items-center justify-center">
                <Radio className="size-6 text-risk-medium" />
              </div>
              <div>
                <span className="text-2xl font-bold font-mono text-risk-medium">{scanResult.openPorts}</span>
                <span className="text-xs text-muted-foreground block uppercase tracking-wider">Portas Abertas</span>
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/50 bg-card flex-1">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="size-12 rounded-lg bg-risk-high/10 border border-risk-high/20 flex items-center justify-center">
                <AlertTriangle className="size-6 text-risk-high" />
              </div>
              <div>
                <span className="text-2xl font-bold font-mono text-risk-high">{scanResult.warnings}</span>
                <span className="text-xs text-muted-foreground block uppercase tracking-wider">Avisos</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border/50 bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
              <BarChart3 className="size-4 text-primary" />
              Distribuicao por Risco
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6">
              <div className="relative h-[200px] w-[200px] shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={distributionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={4}
                      dataKey="value"
                      strokeWidth={0}
                      animationDuration={800}
                    >
                      {distributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<ChartTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-3xl font-bold font-mono text-foreground">{totalVulns}</span>
                  <span className="text-xs text-muted-foreground">Total</span>
                </div>
              </div>
              <div className="flex flex-col gap-3 flex-1">
                {distributionData.map((entry) => {
                  const percent = totalVulns > 0 ? Math.round((entry.value / totalVulns) * 100) : 0;
                  return (
                    <div key={entry.name} className="flex flex-col gap-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="size-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                          <span className="text-sm text-muted-foreground">{entry.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">{percent}%</span>
                          <span className="text-sm font-bold font-mono text-foreground">{entry.value}</span>
                        </div>
                      </div>
                      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${percent}%`, backgroundColor: entry.color }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
              <Bug className="size-4 text-primary" />
              Vulnerabilidades por Scanner
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scannerStats} barSize={24}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "var(--muted-foreground)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    angle={-20}
                    textAnchor="end"
                    height={50}
                  />
                  <YAxis
                    tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={25}
                    allowDecimals={false}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--accent)", opacity: 0.3 }} />
                  <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} animationDuration={800} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for Details */}
      <Tabs defaultValue="vulnerabilities" className="w-full">
        <TabsList className="bg-secondary/50 h-10">
          <TabsTrigger value="vulnerabilities" className="gap-1.5 text-sm">
            <ShieldAlert className="size-4" />
            Vulnerabilidades
          </TabsTrigger>
          <TabsTrigger value="technologies" className="gap-1.5 text-sm">
            <Server className="size-4" />
            Tecnologias
          </TabsTrigger>
          <TabsTrigger value="log" className="gap-1.5 text-sm">
            <Terminal className="size-4" />
            Log Completo
          </TabsTrigger>
        </TabsList>

        <TabsContent value="vulnerabilities" className="mt-6">
          <div className="flex flex-col gap-4">
            {/* Filters */}
            <Card className="border-border/50 bg-card">
              <CardContent className="flex flex-col gap-4 py-4 md:flex-row md:items-center">
                <div className="flex items-center gap-2 text-sm text-muted-foreground shrink-0">
                  <Filter className="size-4" />
                  Filtrar:
                </div>
                <Select value={riskFilter} onValueChange={setRiskFilter}>
                  <SelectTrigger className="w-full md:w-44 bg-input border-border/50 text-foreground h-9">
                    <SelectValue placeholder="Nivel de Risco" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    <SelectItem value="all">Todos os Niveis</SelectItem>
                    <SelectItem value="critical">Critico</SelectItem>
                    <SelectItem value="high">Alto</SelectItem>
                    <SelectItem value="medium">Medio</SelectItem>
                    <SelectItem value="low">Baixo</SelectItem>
                    <SelectItem value="info">Informativo</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={scannerFilter} onValueChange={setScannerFilter}>
                  <SelectTrigger className="w-full md:w-56 bg-input border-border/50 text-foreground h-9">
                    <SelectValue placeholder="Scanner" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    <SelectItem value="all">Todos os Scanners</SelectItem>
                    {uniqueScanners.map((scanner) => (
                      <SelectItem key={scanner} value={scanner}>
                        {scanner}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-xs text-muted-foreground ml-auto font-mono">
                  {filteredVulnerabilities.length}/{scanResult.vulnerabilities.length}
                </span>
              </CardContent>
            </Card>

            {/* Vulnerability Cards */}
            <Accordion type="multiple" className="flex flex-col gap-2">
              {filteredVulnerabilities.map((vuln, index) => (
                <AccordionItem
                  key={vuln.id}
                  value={vuln.id}
                  className="border border-border/50 rounded-lg bg-card overflow-hidden"
                >
                  <AccordionTrigger className="px-4 py-3 hover:no-underline hover:bg-accent/20 [&[data-state=open]]:bg-accent/10">
                    <div className="flex flex-1 items-center gap-3 min-w-0">
                      <span className="text-xs text-muted-foreground/40 font-mono shrink-0 w-6 text-right">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <div
                        className={cn(
                          "size-2 rounded-full shrink-0",
                          getRiskBgColorClass(vuln.riskLevel)
                        )}
                      />
                      <span className="font-medium text-foreground truncate text-left">
                        {vuln.name}
                      </span>
                      <Badge
                        className={cn(
                          "shrink-0 text-[10px] font-bold uppercase h-5",
                          vuln.riskLevel === "critical" && "bg-risk-critical/15 text-risk-critical border-risk-critical/30",
                          vuln.riskLevel === "high" && "bg-risk-high/15 text-risk-high border-risk-high/30",
                          vuln.riskLevel === "medium" && "bg-risk-medium/15 text-risk-medium border-risk-medium/30",
                          vuln.riskLevel === "low" && "bg-risk-low/15 text-risk-low border-risk-low/30",
                          vuln.riskLevel === "info" && "bg-risk-info/15 text-risk-info border-risk-info/30"
                        )}
                      >
                        {getRiskLabel(vuln.riskLevel)}
                      </Badge>
                      <ChevronRight className="size-4 text-muted-foreground/30 ml-auto shrink-0 hidden md:block" />
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="px-4 pb-4">
                    <div className="flex flex-col gap-5 mt-2 ml-9">
                      <div className="flex items-center gap-4 text-xs text-muted-foreground font-mono">
                        <span className="flex items-center gap-1">
                          <Target className="size-3" />
                          {vuln.location}
                        </span>
                        <span className="flex items-center gap-1">
                          <Fingerprint className="size-3" />
                          {vuln.scanner}
                        </span>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                          <ShieldCheck className="size-4 text-primary" />
                          Descricao
                        </div>
                        <p className="text-sm text-muted-foreground leading-relaxed pl-6">
                          {vuln.description}
                        </p>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                          <FileCode2 className="size-4 text-risk-high" />
                          Evidencia
                        </div>
                        <div className="ml-6 rounded-lg bg-background/80 border border-border/30 overflow-hidden">
                          <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary/30 border-b border-border/30">
                            <FileText className="size-3 text-muted-foreground/50" />
                            <span className="text-[10px] text-muted-foreground/50 font-mono">output</span>
                          </div>
                          <pre className="p-4 text-xs text-muted-foreground font-mono overflow-x-auto leading-relaxed">
                            {vuln.evidence}
                          </pre>
                        </div>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                          <Lightbulb className="size-4 text-risk-medium" />
                          Recomendacao
                        </div>
                        <div className="ml-6 rounded-lg bg-risk-info/5 border border-risk-info/10 p-4">
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {vuln.recommendation}
                          </p>
                        </div>
                      </div>
                      
                      <VulnerabilityAnalysisView vulnerability={vuln} />

                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}

              {filteredVulnerabilities.length === 0 && (
                <Card className="border-border/50 bg-card">
                  <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                    <ShieldCheck className="size-12 text-muted-foreground/15 mb-3" />
                    <p className="text-sm text-muted-foreground">
                      Nenhuma vulnerabilidade encontrada com os filtros selecionados.
                    </p>
                  </CardContent>
                </Card>
              )}
            </Accordion>
          </div>
        </TabsContent>

        <TabsContent value="technologies" className="mt-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="border-border/50 bg-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  <Layers className="size-4 text-primary" />
                  Stack Detectada
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  {[
                    { label: "Servidor Web", value: scanResult.technologies.server, icon: Server },
                    { label: "Linguagem", value: scanResult.technologies.language, icon: Code2 },
                    { label: "Framework", value: scanResult.technologies.framework, icon: Layers },
                    { label: "Sistema Operacional", value: scanResult.technologies.os, icon: Monitor },
                    { label: "CMS", value: scanResult.technologies.cms, icon: LayoutGrid },
                  ].map((tech) => (
                    <div
                      key={tech.label}
                      className="flex items-center gap-4 rounded-lg bg-secondary/30 p-4 hover:bg-secondary/50 transition-colors"
                    >
                      <div className="size-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                        <tech.icon className="size-5 text-primary" />
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
                          {tech.label}
                        </span>
                        <span className="text-sm font-medium text-foreground font-mono truncate">
                          {tech.value}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  <Radio className="size-4 text-primary" />
                  Portas Abertas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  {[
                    { port: "22", service: "SSH", version: "OpenSSH 8.9", risk: "medium" as const },
                    { port: "80", service: "HTTP", version: "Apache 2.4.41", risk: "low" as const },
                    { port: "443", service: "HTTPS", version: "Apache 2.4.41", risk: "low" as const },
                    { port: "3306", service: "MySQL", version: "8.0.32", risk: "critical" as const },
                    { port: "8080", service: "HTTP", version: "Node.js", risk: "medium" as const },
                  ].map((port) => (
                    <div
                      key={port.port}
                      className="flex items-center gap-4 rounded-lg bg-secondary/30 p-4"
                    >
                      <div className="flex items-center justify-center size-10 rounded-lg bg-secondary font-mono text-sm font-bold text-foreground shrink-0">
                        {port.port}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-foreground">{port.service}</span>
                          <Badge
                            className={cn(
                              "text-[10px] h-5",
                              port.risk === "critical" && "bg-risk-critical/15 text-risk-critical border-risk-critical/30",
                              port.risk === "medium" && "bg-risk-medium/15 text-risk-medium border-risk-medium/30",
                              port.risk === "low" && "bg-risk-low/15 text-risk-low border-risk-low/30"
                            )}
                          >
                            {getRiskLabel(port.risk)}
                          </Badge>
                        </div>
                        <span className="text-xs text-muted-foreground font-mono">{port.version}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="log" className="mt-6">
          <Card className="border-border/50 bg-card overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2.5 bg-secondary/50 border-b border-border/50">
              <div className="flex items-center gap-1.5">
                <div className="size-3 rounded-full bg-risk-critical/60" />
                <div className="size-3 rounded-full bg-risk-medium/60" />
                <div className="size-3 rounded-full bg-risk-info/60" />
              </div>
              <span className="text-xs text-muted-foreground font-mono ml-2">
                vulnscanner -- log completo
              </span>
              <span className="text-xs text-muted-foreground/50 font-mono ml-auto">
                {scanResult.logEntries.length} linhas
              </span>
            </div>
            <CardContent className="p-0">
              <ScrollArea className="h-[500px] p-4">
                <div className="flex flex-col gap-0.5 font-mono text-xs">
                  {scanResult.logEntries.map((log, index) => {
                    let color = "text-muted-foreground"
                    if (log.includes("[CRITICO]")) color = "text-risk-critical font-semibold"
                    else if (log.includes("[ALTO]")) color = "text-risk-high font-semibold"
                    else if (log.includes("[MEDIO]")) color = "text-risk-medium"
                    else if (log.includes("[BAIXO]")) color = "text-risk-low"
                    else if (log.includes("===")) color = "text-primary font-semibold"
                    else if (log.includes("concluido") || log.includes("finalizado")) color = "text-risk-info"

                    return (
                      <div key={index} className={cn("leading-relaxed flex gap-3", color)}>
                        <span className="text-muted-foreground/20 select-none shrink-0 w-7 text-right">
                          {String(index + 1).padStart(3, " ")}
                        </span>
                        <span>{log}</span>
                      </div>
                    )
                  })}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
