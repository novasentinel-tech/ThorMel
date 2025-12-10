"use client"

import { useEffect, useRef } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

interface ScanTerminalProps {
  logs: string[]
}

function getLogColor(log: string) {
  const logLower = log.toLowerCase();
  if (logLower.includes("[critico]") || logLower.includes("crítico")) return "text-risk-critical font-semibold"
  if (logLower.includes("[alto]")) return "text-risk-high font-semibold"
  if (logLower.includes("[medio]") || logLower.includes("médio")) return "text-risk-medium"
  if (logLower.includes("[baixo]")) return "text-risk-low"
  if (logLower.includes("===")) return "text-primary font-semibold"
  if (logLower.includes("concluido") || logLower.includes("finalizado") || logLower.includes("✅")) return "text-risk-info"
  if (logLower.includes("error") || logLower.includes("erro") || logLower.includes("❌")) return "text-red-400"
  if (logLower.includes("warning") || logLower.includes("aviso") || logLower.includes("⚠️")) return "text-yellow-400"
  return "text-muted-foreground"
}

export function ScanTerminal({ logs }: ScanTerminalProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      const viewport = scrollRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (viewport) {
        viewport.scrollTop = viewport.scrollHeight
      }
    }
  }, [logs])

  return (
    <Card className="border-border/50 bg-card overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2.5 bg-secondary/50 border-b border-border/50">
        <div className="flex items-center gap-1.5">
          <div className="size-3 rounded-full bg-risk-critical/60" />
          <div className="size-3 rounded-full bg-risk-medium/60" />
          <div className="size-3 rounded-full bg-risk-info/60" />
        </div>
        <span className="text-xs text-muted-foreground font-mono ml-2">
          vulnscanner -- terminal
        </span>
      </div>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px] p-4" ref={scrollRef}>
          <div className="flex flex-col gap-0.5 font-mono text-xs">
            {logs.length === 0 ? (
              <div className="flex items-center gap-2">
                <span className="text-primary">$</span>
                <span className="text-muted-foreground/50">
                  Aguardando inicio do scan...
                </span>
                <span className="inline-block w-2 h-4 bg-primary/50 animate-pulse" />
              </div>
            ) : (
              logs.map((log, index) => (
                <div
                  key={index}
                  className={cn("leading-relaxed flex gap-3", getLogColor(log))}
                >
                  <span className="text-muted-foreground/20 select-none shrink-0 w-7 text-right">
                    {String(index + 1).padStart(3, " ")}
                  </span>
                  <span>{log}</span>
                </div>
              ))
            )}
            {logs.length > 0 && !logs[logs.length - 1]?.includes("finalizado") && (
              <div className="flex items-center gap-3">
                <span className="text-muted-foreground/20 select-none shrink-0 w-7" />
                <span className="inline-block w-2 h-4 bg-primary animate-pulse" />
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

    