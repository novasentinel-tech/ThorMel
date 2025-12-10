"use client"

import { useState, useCallback } from "react"
import { DashboardView } from "@/components/dashboard-view"
import { RealTimeScanView } from "@/components/realtime-scan-view"
import { ReportView } from "@/components/report-view"
import {
  mockScanHistory,
  scanners as scannersList,
  type ScanResult,
  type RiskLevel,
  type ScanHistoryEntry,
} from "@/lib/mock-data"
import { Shield, LayoutDashboard, Activity, FileText, Radio, ShieldCheck } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { runScan } from './actions'
import { useToast } from "@/hooks/use-toast"

type TabState = "dashboard" | "scanning" | "report"

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

export default function Page() {
  const [activeTab, setActiveTab] = useState<TabState>("dashboard")
  const [scanResult, setScanResult] = useState<ScanResult | null>(null)
  const [scanHistory, setScanHistory] = useState<ScanHistoryEntry[]>(mockScanHistory)
  const [logs, setLogs] = useState<string[]>([])
  const [scannerStatuses, setScannerStatuses] = useState<ScannerStatus[]>([])
  const [progress, setProgress] = useState(0)
  const [foundVulns, setFoundVulns] = useState<FoundVuln[]>([])
  const [scanTarget, setScanTarget] = useState("")
  const [isScanning, setIsScanning] = useState(false)
  const { toast } = useToast()

  const handleStartScan = useCallback(async (target: string, scanType: string) => {
    setIsScanning(true)
    setActiveTab("scanning")
    setScanTarget(target)
    setLogs(["[SYSTEM] Iniciando scan... Por favor, aguarde. A execução pode levar alguns minutos."])
    setScanResult(null)
    setFoundVulns([])
    setProgress(5) // Initial progress
    setScannerStatuses(scannersList.map((s) => ({ ...s, status: "pending" })))

    const newScanEntryId = `scan-in-progress-${Date.now()}`;
    setScanHistory(prev => [{
      id: newScanEntryId,
      target,
      date: new Date().toISOString(),
      riskScore: 0,
      scanType,
      status: 'running',
    }, ...prev]);

    toast({
      title: "Scan Iniciado",
      description: `Executando scan do tipo '${scanType}' em ${target}.`,
    })

    try {
      const reportJsonString = await runScan(target, scanType);
      setLogs(prev => [...prev, "[SYSTEM] Script finalizado. Processando relatório..."]);
      
      let finalReport: ScanResult | null = null;

      try {
        finalReport = JSON.parse(reportJsonString);
      } catch (e) {
          console.error("Failed to parse report JSON:", e);
          const errorMessage = (e as Error).message;
          setLogs(prev => [...prev, "[ERRO DO SISTEMA] Falha ao interpretar o relatório JSON do script.", errorMessage]);
          toast({
              variant: "destructive",
              title: "Erro de Relatório",
              description: "O script retornou dados em formato inválido.",
          })
          setScanHistory(prev => prev.map(h => h.id === newScanEntryId ? { ...h, status: 'failed' } : h));
      }

      if (finalReport) {
        setScanResult(finalReport);
        setFoundVulns(finalReport.vulnerabilities.map(v => ({ id: v.id, name: v.name, riskLevel: v.riskLevel })))
        setScanHistory(prev => prev.map(h => h.id === newScanEntryId ? {
            id: finalReport.id,
            target: finalReport.target,
            date: finalReport.date,
            riskScore: finalReport.riskScore,
            scanType: finalReport.scanType,
            status: 'completed',
        } : h));
        toast({
          title: "Scan Concluído!",
          description: `${finalReport.totalVulnerabilities} vulnerabilidades encontradas.`,
        })
        setLogs(prev => [...prev, "[SYSTEM] Relatório processado com sucesso."]);
        setTimeout(() => {
          setActiveTab("report");
        }, 1000);
      }

    } catch (error: any) {
        console.error(error);
        const errorMessage = error.message || "Ocorreu um erro desconhecido durante o scan."
        setLogs(prev => [...prev, "\n[ERRO CRÍTICO]", errorMessage]);
        setScanHistory(prev => prev.map(h => h.id === newScanEntryId ? { ...h, status: 'failed' } : h));
        toast({
            variant: "destructive",
            title: "Falha na Execução do Scan",
            description: errorMessage,
        })
    } finally {
        setIsScanning(false);
        setProgress(100);
        setScannerStatuses(scannersList.map((s) => ({ ...s, status: "completed" })))
    }
  }, [toast]);


  const handleViewReport = useCallback(() => {
    if (scanResult) {
      setActiveTab("report")
    }
  }, [scanResult])

  const navItems = [
    {
      id: "dashboard" as const,
      label: "Dashboard",
      icon: LayoutDashboard,
      disabled: isScanning,
    },
    {
      id: "scanning" as const,
      label: "Scan Ativo",
      icon: Activity,
      disabled: !isScanning,
      badge: isScanning ? "LIVE" : null,
    },
    {
      id: "report" as const,
      label: "Relatorio",
      icon: FileText,
      disabled: isScanning || !scanResult,
      badge: scanResult ? String(scanResult.totalVulnerabilities) : null,
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2.5">
              <div className="size-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Shield className="size-4 text-primary" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-foreground tracking-tight leading-none">
                  VulnScanner
                </span>
                <span className="text-[10px] text-muted-foreground leading-none mt-0.5">
                  Security Platform
                </span>
              </div>
            </div>

            <nav className="flex items-center gap-1" role="navigation" aria-label="Navegacao principal">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    if (!item.disabled) setActiveTab(item.id)
                  }}
                  disabled={item.disabled}
                  className={cn(
                    "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-all relative",
                    activeTab === item.id
                      ? "bg-primary/10 text-primary font-medium"
                      : item.disabled
                        ? "text-muted-foreground/30 cursor-not-allowed"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                  )}
                  aria-current={activeTab === item.id ? "page" : undefined}
                >
                  <item.icon className={cn(
                    "size-4",
                    item.id === "scanning" && isScanning && "animate-pulse"
                  )} />
                  <span className="hidden sm:inline">{item.label}</span>
                  {item.badge && (
                    <span
                      className={cn(
                        "text-[10px] font-bold px-1.5 py-0.5 rounded-full leading-none",
                        item.id === "scanning"
                          ? "bg-risk-critical/20 text-risk-critical animate-pulse"
                          : "bg-primary/20 text-primary"
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {isScanning && (
            <div className="flex items-center gap-2 text-sm">
              <Radio className="size-3 text-risk-critical animate-pulse" />
              <span className="text-xs text-muted-foreground font-mono hidden md:inline">
                Escaneando {scanTarget}
              </span>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6">
        {activeTab === "dashboard" && (
          <DashboardView
            scanResult={scanResult}
            scanHistory={scanHistory}
            onStartScan={handleStartScan}
            onViewReport={handleViewReport}
            isScanning={isScanning}
          />
        )}
        {activeTab === "scanning" && (
          <RealTimeScanView
            logs={logs}
            scanners={scannerStatuses}
            progress={progress}
            foundVulnerabilities={foundVulns}
            target={scanTarget}
          />
        )}
        {activeTab === "report" && scanResult && (
          <ReportView scanResult={scanResult} />
        )}
         {activeTab === "report" && !scanResult && (
            <Card className="border-border/50 bg-card">
                <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                    <ShieldCheck className="size-10 text-muted-foreground/30" />
                    <h3 className="mt-4 text-lg font-semibold">Nenhum Relatório Disponível</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Execute um scan no dashboard para visualizar o relatório aqui.
                    </p>
                </CardContent>
            </Card>
        )}
      </main>
    </div>
  )
}
