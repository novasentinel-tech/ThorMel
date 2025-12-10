"use client"

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import { getScoreStrokeColor } from "@/lib/mock-data"

interface RiskScoreGaugeProps {
  score: number
  size?: number
  showLabel?: boolean
}

export function RiskScoreGauge({ score, size = 180, showLabel = true }: RiskScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const strokeWidth = size > 140 ? 14 : 10
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference
  const strokeColor = getScoreStrokeColor(score)

  useEffect(() => {
    const duration = 1200
    const steps = 60
    const stepTime = duration / steps
    const increment = score / steps
    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= score) {
        current = score
        clearInterval(timer)
      }
      setAnimatedScore(Math.round(current))
    }, stepTime)
    return () => clearInterval(timer)
  }, [score])

  const getLabel = (s: number) => {
    if (s >= 80) return "Critico"
    if (s >= 60) return "Alto"
    if (s >= 40) return "Medio"
    if (s >= 20) return "Baixo"
    return "Seguro"
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="-rotate-90"
          aria-label={`Score de risco: ${score} de 100`}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-secondary"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{
              filter: `drop-shadow(0 0 8px ${strokeColor})`,
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-bold font-mono leading-none"
            style={{
              color: strokeColor,
              fontSize: size > 140 ? "3rem" : "2rem",
            }}
          >
            {animatedScore}
          </span>
          <span className="text-xs text-muted-foreground mt-1">/ 100</span>
        </div>
      </div>
      {showLabel && (
        <div className="flex flex-col items-center gap-0.5">
          <span
            className="text-sm font-bold uppercase tracking-widest"
            style={{ color: strokeColor }}
          >
            Risco {getLabel(score)}
          </span>
          <span className="text-xs text-muted-foreground">Score de Risco Global</span>
        </div>
      )}
    </div>
  )
}

    