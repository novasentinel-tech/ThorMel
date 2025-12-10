"use client"

import { Card, CardContent } from "@/components/ui/card"
import { RiskScoreGauge } from "@/components/risk-score-gauge"
import { StatCard } from "@/components/stat-card"
import { DistributionChart } from "@/components/distribution-chart"
import { ScanHistoryTable } from "@/components/scan-history-table"
import { ScanControls } from "@/components/scan-controls"
import { ScanTrendChart } from "@/components/scan-trend-chart"
import type { ScanResult, ScanHistoryEntry } from "@/lib/mock-data"
import { ShieldCheck } from "lucide-react"

interface DashboardViewProps {
  scanResult: ScanResult | null
  scanHistory: ScanHistoryEntry[]
  onStartScan: (target: string, scanType: string) => void
  onViewReport: () => void
  isScanning: boolean
}

export function DashboardView({
  scanResult,
  scanHistory,
  onStartScan,
  onViewReport,
  isScanning,
}: DashboardViewProps) {
  return (
    <div className="flex flex-col gap-6">
      <ScanControls onStartScan={onStartScan} isScanning={isScanning} />

      {scanResult ? (
        <>
          <div className="grid gap-6 lg:grid-cols-12">
            <Card className="border-border/50 bg-card lg:col-span-3 flex items-center justify-center p-6">
              <RiskScoreGauge score={scanResult.riskScore} size={200} />
            </Card>

            <div className="lg:col-span-3 flex flex-col gap-4">
              <StatCard
                title="Vulnerabilidades"
                value={scanResult.totalVulnerabilities}
                icon="vulnerabilities"
                trend="up"
                trendValue="vs ultimo scan"
              />
              <StatCard
                title="Portas Abertas"
                value={scanResult.openPorts}
                icon="ports"
                trend="neutral"
                trendValue="sem alteracao"
              />
              <StatCard
                title="Avisos"
                value={scanResult.warnings}
                icon="warnings"
                trend="down"
                trendValue="-2 vs anterior"
              />
            </div>

            <div className="lg:col-span-6">
              <DistributionChart distribution={scanResult.distribution} />
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ScanTrendChart history={scanHistory} />
            <ScanHistoryTable history={scanHistory} onViewReport={onViewReport} />
          </div>
        </>
      ) : (
        <Card className="border-border/50 bg-card">
          <CardContent className="flex flex-col items-center justify-center py-20 text-center">
            <div className="size-20 rounded-full bg-secondary flex items-center justify-center mb-6">
              <ShieldCheck className="size-10 text-muted-foreground/30" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Nenhum scan realizado
            </h3>
            <p className="text-sm text-muted-foreground max-w-md leading-relaxed">
              Insira um alvo acima e execute um scan para ver os resultados
              aqui. O dashboard sera atualizado automaticamente ao concluir.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

    