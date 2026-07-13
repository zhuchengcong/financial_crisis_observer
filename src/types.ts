export type Signal = 'normal' | 'attention' | 'warning' | 'danger'
export interface Indicator { id: string; name: string; group: string; value: number | null; unit: string; percentile: number | null; signal: Signal; observationDate: string; fetchedAt: string; frequency: string; status: 'success' | 'missing'; change?: string }
export interface ScoreFactor { name: string; weight: number; value: string; rule: string; contribution: number }
export interface Subsystem { name: string; score: number; weight: number; signal: Signal; factors: ScoreFactor[] }
export interface Transmission { from: string; to: string; intensity: number; baseline: number; lag: string; outlook: string }
export interface HistoryMatch { period: string; similarity: number; matches: string; differences: string }
export interface CalendarEvent { date: string; name: string; expected: string; previous: string; risk: string; signal: Signal }
export interface DashboardData {
  generatedAt: string
  crisis: { score: number; trend30d: number; state: string; summary: string; subsystems: Subsystem[] }
  indicators: Indicator[]
  alerts: { date: string; title: string; detail: string; signal: Signal }[]
  history: HistoryMatch[]
  transmission: Transmission[]
  calendar: CalendarEvent[]
}
