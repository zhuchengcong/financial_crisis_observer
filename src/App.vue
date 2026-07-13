<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadDashboard } from './services/data'
import type { DashboardData, Signal } from './types'
import { getIndicatorHelp } from './data/indicatorHelp'

const data = ref<DashboardData | null>(null)
const error = ref('')
const activeGroup = ref('全部')
const groups = computed(() => ['全部', ...new Set(data.value?.indicators.map(i => i.group) ?? [])])
const indicators = computed(() => data.value?.indicators.filter(i => activeGroup.value === '全部' || i.group === activeGroup.value) ?? [])
const headlineIds = ['VIXCLS', 'BAMLH0A0HYM2', 'CPIAUCSL', 'PCEPILFE', 'T5YIE', 'MORTGAGE30US', 'SOFR_FF_SPREAD', 'FED_NET_LIQUIDITY']
const headlineIndicators = computed(() => headlineIds.map(id => data.value?.indicators.find(i => i.id === id)).filter((i): i is NonNullable<typeof i> => Boolean(i)))
const expandedScore = ref<string | null>(null)
const openHelpId = ref<string | null>(null)
const label: Record<Signal, string> = { normal: '正常', attention: '注意', warning: '警告', danger: '危险' }
const number = (n: number) => n.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
const fresh = (iso: string) => new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Shanghai' }).format(new Date(iso))
onMounted(async () => { try { data.value = await loadDashboard() } catch (e) { error.value = e instanceof Error ? e.message : '加载失败' } })
</script>

<template>
  <main v-if="data" class="shell">
    <header class="topbar">
      <div class="brand"><span class="pulse"></span><div><b>宏观风险观测站</b><small>MACRO RISK OBSERVER</small></div></div>
      <div class="updated"><span>数据最后更新</span><strong>{{ fresh(data.generatedAt) }}</strong></div>
    </header>

    <section class="hero panel command-bar">
      <div class="hero-title"><p class="eyebrow">GLOBAL ECONOMIC CRISIS INDEX</p><h1>全球经济危机指数</h1><p class="summary">{{ data.crisis.summary }}</p></div>
      <div class="headline-metrics"><article v-for="item in headlineIndicators" :key="item.id"><span>{{ item.name }}</span><b>{{ item.value === null ? '—' : number(item.value) }}{{ item.unit }}</b><small><i :class="item.signal"></i>{{ label[item.signal] }} · {{ item.percentile === null ? '待计算' : item.percentile + '% 分位' }}</small></article></div>
      <div class="score-wrap"><div class="score" :style="{ '--score': data.crisis.score + '%' }"><span>{{ data.crisis.score }}</span><small>/ 100</small></div><div><strong class="state">{{ data.crisis.state }}</strong><p>30 天 <em>+{{ data.crisis.trend30d }}</em></p></div></div>
    </section>

    <section class="subsystems"><article v-for="item in data.crisis.subsystems" :key="item.name" class="subsystem panel" @click="expandedScore = expandedScore === item.name ? null : item.name"><div class="sub-head"><span>{{ item.name }}</span><span class="badge" :class="item.signal">{{ label[item.signal] }}</span></div><b>{{ item.score }}</b><div class="bar"><i :class="item.signal" :style="{ width: item.score + '%' }"></i></div><small>综合权重 {{ item.weight }}% · 点击查看构成</small></article></section>
    <p class="score-note"><strong>综合指数 =</strong> 流动性 20% + 信用 20% + 银行 10% + 实体 20% + 就业 15% + 政策 15% = <b>{{ data.crisis.score }}</b>。固定权重确保分项与总分可复算；信用、银行、就业同时超过 60 分时额外加 10 分。</p>

    <section v-if="expandedScore" class="panel scorecard"><div class="section-title"><div><p class="eyebrow">SCORING BREAKDOWN</p><h2>{{ expandedScore }}评分拆解</h2></div><button class="close" @click="expandedScore = null">收起 ×</button></div><div class="factor-grid"><article v-for="factor in data.crisis.subsystems.find(s => s.name === expandedScore)?.factors" :key="factor.name"><div><b>{{ factor.name }}</b><span>权重 {{ factor.weight }}%</span></div><strong>{{ factor.value }}</strong><div class="mini-bar"><i :style="{ width: factor.contribution + '%' }"></i></div><small>{{ factor.rule }}</small></article></div></section>

    <section class="grid">
      <article class="panel chain"><div class="section-title"><div><p class="eyebrow">TRANSMISSION MAP</p><h2>危机传导强度与滞后</h2></div><span>风险尚未形成全面传导</span></div><div class="transmission-list"><article v-for="edge in data.transmission" :key="edge.from + edge.to"><div class="edge-head"><b>{{ edge.from }}</b><span>→</span><b>{{ edge.to }}</b><em>强度 {{ edge.intensity.toFixed(2) }}</em></div><div class="strength"><i :style="{ width: edge.intensity * 100 + '%' }"></i><mark>历史均值 {{ edge.baseline.toFixed(2) }}</mark></div><p><strong>{{ edge.lag }}</strong>{{ edge.outlook }}</p></article></div></article>
      <article class="panel similarity"><div class="section-title"><div><p class="eyebrow">HISTORICAL PATTERN</p><h2>历史周期相似度</h2></div><small>标准化多维距离加权</small></div><div v-for="row in data.history" :key="row.period" class="history-card"><div class="similar-row"><span>{{ row.period }}</span><div><i :style="{ width: row.similarity + '%' }"></i></div><b>{{ row.similarity }}%</b></div><p><strong>匹配</strong>{{ row.matches }}</p><p><strong>差异</strong>{{ row.differences }}</p></div></article>
    </section>

    <section class="panel table-panel signal-panel"><div class="section-title"><div><p class="eyebrow">RISK SIGNALS</p><h2>风险信号灯</h2><small>{{ indicators.length }} 项指标</small></div><div class="tabs"><button v-for="group in groups" :key="group" :class="{ active: activeGroup === group }" @click="activeGroup = group">{{ group }}</button></div></div><div class="signal-grid"><article v-for="item in indicators" :key="item.id" class="signal-card"><div class="signal-main"><div class="signal-name" @mouseenter="openHelpId = item.id" @mouseleave="openHelpId = null"><div class="signal-title"><b>{{ item.name }}</b><button class="help-trigger" type="button" :aria-label="`查看${item.name}说明`" :aria-expanded="openHelpId === item.id" @click.stop="openHelpId = openHelpId === item.id ? null : item.id" @focus="openHelpId = item.id" @blur="openHelpId = null">ⓘ</button></div><small>{{ item.id }} · {{ item.group }}<template v-if="item.source"> · {{ item.source }}</template></small><div v-if="openHelpId === item.id" class="indicator-tip" role="tooltip"><strong>小白说明</strong><p><b>是什么：</b>{{ getIndicatorHelp(item).what }}</p><p><b>为什么重要：</b>{{ getIndicatorHelp(item).why }}</p><p><b>怎么看：</b>{{ getIndicatorHelp(item).reading }}</p></div></div><strong v-if="item.status === 'success'">{{ number(item.value!) }}{{ item.unit }}</strong><strong v-else>—</strong><span class="badge" :class="item.signal"><i></i>{{ label[item.signal] }}</span></div><div class="signal-meta"><span>分位 <b>{{ item.percentile === null ? '—' : item.percentile + '%' }}</b></span><span>观测 <b>{{ item.observationDate }}</b></span><span>{{ item.frequency }}</span><em v-if="item.change">{{ item.change }}</em></div><div class="percentile-track"><i :class="item.signal" :style="{ width: (item.percentile ?? 0) + '%' }"></i></div></article></div></section>

    <section class="grid lower"><article class="panel alerts"><div class="section-title"><div><p class="eyebrow">EVENT LOG</p><h2>异常事件</h2></div></div><div v-for="alert in data.alerts" :key="alert.title" class="alert"><span class="dot" :class="alert.signal"></span><div><small>{{ alert.date }}</small><b>{{ alert.title }}</b><p>{{ alert.detail }}</p></div></div></article><article class="panel calendar"><div class="inline-heading"><p class="eyebrow">RISK CALENDAR</p><h2>本周风险日程</h2></div><div class="calendar-head"><span>日期 / 数据</span><span>预期 / 前值</span></div><div v-for="event in data.calendar" :key="event.name" class="calendar-event"><span class="dot" :class="event.signal"></span><div><small>{{ event.date }}</small><b>{{ event.name }}</b><p>{{ event.risk }}</p></div><strong>{{ event.expected }}<small>前值 {{ event.previous }}</small></strong></div><p class="disclaimer">市场预期会随调查更新；历史数据采用当前最新修订值，不代表当时可见数据。</p></article></section>
  </main>
  <main v-else class="loading"><span class="pulse"></span>{{ error || '正在读取宏观数据…' }}</main>
</template>
