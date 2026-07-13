import type { DashboardData } from '../types'

export async function loadDashboard(): Promise<DashboardData> {
  const response = await fetch(`${import.meta.env.BASE_URL}data/dashboard.json`, { cache: 'no-store' })
  if (!response.ok) throw new Error('数据文件暂不可用')
  return response.json()
}
