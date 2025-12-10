"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Crosshair, Play, Loader2 } from "lucide-react"

interface ScanControlsProps {
  onStartScan: (target: string, scanType: string) => void
  isScanning: boolean
}

export function ScanControls({ onStartScan, isScanning }: ScanControlsProps) {
  const [target, setTarget] = useState("")
  const [scanType, setScanType] = useState("analise")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (target.trim()) {
      onStartScan(target.trim(), scanType)
    }
  }

  return (
    <Card className="border-border/50 bg-card overflow-hidden">
      <div className="h-0.5 bg-primary/20">
        {isScanning && (
          <div className="h-full bg-primary animate-pulse" />
        )}
      </div>
      <CardContent className="p-5">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 md:flex-row md:items-end">
          <div className="flex-1 space-y-1.5">
            <label htmlFor="target" className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
              Alvo
            </label>
            <div className="relative">
              <Crosshair className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground/50" />
              <Input
                id="target"
                placeholder="https://exemplo.com.br"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="bg-input border-border/50 text-foreground placeholder:text-muted-foreground/40 font-mono pl-10 h-10"
                disabled={isScanning}
              />
            </div>
          </div>
          <div className="w-full space-y-1.5 md:w-44">
            <label htmlFor="scan-type" className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
              Tipo de Scan
            </label>
            <Select value={scanType} onValueChange={setScanType} disabled={isScanning}>
              <SelectTrigger id="scan-type" className="bg-input border-border/50 text-foreground h-10">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-popover border-border">
                <SelectItem value="analise">Análise</SelectItem>
                <SelectItem value="analise_exploracao">Análise + Exploração</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button
            type="submit"
            disabled={isScanning || !target.trim()}
            className="w-full md:w-auto bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 font-medium gap-2"
          >
            {isScanning ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Escaneando...
              </>
            ) : (
              <>
                <Play className="size-4" />
                Executar Scan
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
