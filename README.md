该项目用于实时追踪全球宏观经济指标、识别系统性风险与衰退预警的宏观经济数据仪表盘。此类工具可监控通胀水平、资产负债表与违约率，帮助应对潜在的金融冲击

- 页面本身是纯前端，没有常驻后端服务器；
- GitHub Actions 充当定时数据采集器；
- 采集结果保存成 JSON 文件；
- 前端读取 JSON，计算指标、展示图表和危机等级。

GitHub Pages本身就是静态 HTML、CSS、JavaScript 托管服务，也支持通过 GitHub Actions 构建和发布。公开仓库使用标准 GitHub Actions Runner 目前免费。([GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages?utm_source=chatgpt.com))

项目访问地址：https://zhuchengcong.github.io/financial_crisis_observer/
---

# 一、架构

```text
外部经济数据源
    │
    │ GitHub Actions 定时请求
    ▼
scripts/fetch-data.py
    │
    ├── 清洗数据
    ├── 计算同比、环比、Z-Score
    ├── 生成风险信号
    └── 输出 JSON
            │
            ▼
public/data/
    ├── market.json
    ├── credit.json
    ├── employment.json
    ├── china.json
    ├── crisis-score.json
    └── update-status.json
            │
            ▼
Vue / React 纯前端页面
            │
            ▼
GitHub Pages
```

---

# 三、系统页面设计

建议将首页设计成六个模块。

## 1. 总体危机温度

顶部显示：

```text
全球经济危机指数：42.6 / 100
状态：黄色预警
趋势：过去30天上升 6.4
更新时间：2026-07-13 06:20
```

同时显示六个子指数：


| 子系统   | 得分  | 状态   |
| ----- | --- | ---- |
| 市场流动性 | 35  | 正常偏紧 |
| 信用风险  | 48  | 黄色   |
| 银行压力  | 27  | 正常   |
| 实体经济  | 43  | 黄色   |
| 就业压力  | 31  | 正常   |
| 中国经济  | 52  | 橙色边缘 |


页面不要只显示总分。必须同时展示每个子模块，避免总分掩盖结构性风险。

---



## 2. 风险信号灯

每项指标显示：

```text
● 正常
● 注意
● 警告
● 危险
```

例如：


| 指标        | 当前值   | 历史分位 | 信号  | 更新时间  |
| --------- | ----- | ---- | --- | ----- |
| 美国高收益债利差  | 3.4%  | 43%  | 正常  | 07-12 |
| VIX       | 24.1  | 78%  | 注意  | 07-12 |
| 初请失业金四周均值 | 258K  | 73%  | 注意  | 07-09 |
| 10Y－2Y利差  | 0.42% | —    | 正常化 | 07-12 |
| 失业率三个月变化  | +0.3% | 81%  | 警告  | 06月   |


颜色只是辅助，旁边必须有文字，避免用户只靠颜色理解。

---



## 3. 危机传导链

做一个横向状态图：

```text
流动性
  ↓
信用
  ↓
银行资产负债表
  ↓
企业融资
  ↓
就业
  ↓
消费与生产
```

每个节点显示当前风险：

```text
流动性：黄色
信用：黄色
银行：绿色
就业：绿色
实体需求：黄色
```

这样可以判断风险停留在哪一层。

例如：

```text
股市波动上升，但信用利差和就业稳定
```

系统应判断为：

```text
金融市场调整，暂未形成经济危机传导。
```

而不是简单因为 VIX 上升就给出红色预警。

---



## 4. 历史对比

可以把当前指标与以下时期比较：

- 2000年互联网泡沫；
- 2008年金融危机；
- 2020年疫情冲击；
- 2022年通胀紧缩周期；
- 当前周期。

页面显示：

```text
当前危机特征与历史阶段的相似度
```


| 历史阶段      | 相似度 |
| --------- | --- |
| 2001年衰退   | 61% |
| 2008年金融危机 | 28% |
| 2020年疫情冲击 | 19% |
| 2022年紧缩周期 | 72% |


第一版不建议直接使用机器学习。先采用指标标准化后的欧氏距离或余弦相似度，结果更容易解释。

---



## 5. 数据日历

把指标按更新频率分类：

### 每日指标

- VIX；
- MOVE；
- 2年和10年美债收益率；
- 高收益债利差；
- 投资级信用利差；
- 银行股相对强弱；
- 美元指数；
- 黄金、铜、原油；
- 离岸人民币。



### 每周指标

- 初次申请失业救济人数；
- 持续申请失业救济人数；
- 银行贷款和存款；
- 房贷申请；
- 房地产成交；
- 中国高频地产数据。



### 每月指标

- 失业率；
- 非农就业；
- CPI、PPI；
- 工业生产；
- 零售销售；
- PMI；
- 社融；
- M1、M2；
- 房地产投资和销售。



### 每季度指标

- 银行坏账率；
- 企业现金流；
- 利息保障倍数；
- 居民偿债压力；
- 政府财政和利息支出。

系统不能把“没有更新”误判为“数值没有变化”。每个指标必须保存：

```json
{
  "seriesId": "UNRATE",
  "value": 4.3,
  "observationDate": "2026-06-01",
  "fetchedAt": "2026-07-13T00:10:00Z",
  "frequency": "monthly",
  "status": "success"
}
```

---



## 6. 异常事件列表

页面自动列出最近的变化：

```text
2026-07-12
高收益债利差5日上升42个基点，进入过去5年82%分位。

2026-07-10
初请失业金四周均值连续4周上升。

2026-07-08
收益率曲线继续牛陡，市场降息预期增强。
```

这比单纯画很多折线图更有用。

---



# 四、第一版接入的指标

FRED API可以获取数据序列的历史观察值，并支持 JSON、CSV 等格式。([FRED](https://fred.stlouisfed.org/docs/api/fred/overview.html?utm_source=chatgpt.com))

建议第一版先做美国和全球美元体系，因为公开数据最完整。

## 市场流动性

```text
VIXCLS       VIX
DGS2         美国2年期国债收益率
DGS10        美国10年期国债收益率
DGS3MO       美国3个月国债收益率
SOFR         SOFR
DTWEXBGS     美元贸易加权指数
```



## 信用风险

```text
BAMLH0A0HYM2       美国高收益债OAS
BAMLC0A4CBBB       BBB公司债OAS
BAMLC0A0CM         美国公司债总体OAS
```



## 就业

```text
ICSA          初次申请失业救济人数
CCSA          持续申请失业救济人数
UNRATE        失业率
PAYEMS        非农就业人数
JTSJOL        职位空缺
AWHAETP       私营企业平均周工时
TEMPHELPS     临时帮助服务就业
```



## 实体经济

```text
INDPRO        工业生产
RSAFS         零售销售
UMCSENT       消费者信心
HOUST         新屋开工
PERMIT        建筑许可
NEWORDER      制造业新订单
```



## 通胀和政策

```text
CPIAUCSL      CPI
CPILFESL      核心CPI
PCEPI         PCE价格指数
FEDFUNDS      联邦基金利率
WALCL         美联储总资产
```

需要注意，部分序列可能存在授权、更新延迟或数据源调整，因此指标配置必须支持替换，不要把所有 series ID 硬编码在页面组件内。

---

## GitHub Actions自动采集

稳定数据源自动抓取，失败时保留旧值。

## 第三阶段：数据源适配器

为每个数据源写独立适配器：

```text
adapters/
├── fred.py
├── world_bank.py
├── china_nbs.py
├── pbc.py
├── customs.py
└── manual_csv.py
```

某个数据源失效时，不会影响整个系统。

---



# 六、实际更新频率

不建议所有指标每5分钟抓一次。宏观指标本身不更新，频繁调用没有意义。

推荐：


| 数据类别     | GitHub Actions频率 |
| -------- | ---------------- |
| 金融市场指标   | 每小时或每日           |
| 信用利差     | 每日               |
| 初请失业金    | 每周五检查            |
| 美国月度宏观数据 | 每日检查一次           |
| 中国月度数据   | 每日检查一次           |
| 历史危机评分   | 数据变化后重新计算        |
| 前端部署     | 数据或代码变化后         |


GitHub Actions定时任务支持 POSIX cron，官方文档显示最短计划间隔为5分钟，但计划任务可能并非严格实时，因此不适合高频交易或秒级监控。([GitHub Docs](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions?utm_source=chatgpt.com))

对于经济危机监控，每小时甚至每天一次已经足够。

---



# 七、GitHub Actions配置示例

每日更新：

```yaml
name: Update Economic Data

on:
  schedule:
    - cron: "20 1 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-data:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install requests pandas numpy

      - name: Fetch and calculate
        env:
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
        run: |
          python scripts/update_data.py

      - name: Commit updated data
        run: |
          git config user.name "economic-monitor-bot"
          git config user.email "actions@github.com"
          git add public/data
          git diff --cached --quiet || git commit -m "data: update economic indicators"
          git push
```

GitHub Actions 的 cron 默认按 UTC 理解。

例如：

```yaml
cron: "20 1 * * *"
```

对应新加坡时间：

```text
每天09:20
```

避免设置在整点，因为整点附近通常有更多计划任务排队。

---



# 八、前端技术

```text
Vue 3
TypeScript
Vite
Vue Router
Apache ECharts
Tailwind CSS 或普通 SCSS
```



---



# 九、项目目录

```text
economic-crisis-monitor/
├── .github/
│   └── workflows/
│       ├── update-daily.yml
│       ├── update-weekly.yml
│       └── deploy-pages.yml
│
├── scripts/
│   ├── update_data.py
│   ├── fetchers/
│   │   ├── fred_fetcher.py
│   │   └── manual_fetcher.py
│   ├── indicators/
│   │   ├── normalize.py
│   │   ├── signals.py
│   │   ├── sahm_rule.py
│   │   └── yield_curve.py
│   └── scoring/
│       └── crisis_score.py
│
├── public/
│   └── data/
│       ├── manifest.json
│       ├── indicators.json
│       ├── history.json
│       ├── alerts.json
│       └── update-status.json
│
├── src/
│   ├── components/
│   │   ├── CrisisGauge.vue
│   │   ├── RiskSignalTable.vue
│   │   ├── IndicatorChart.vue
│   │   ├── TransmissionChain.vue
│   │   └── DataFreshness.vue
│   ├── views/
│   │   ├── DashboardView.vue
│   │   ├── MarketView.vue
│   │   ├── CreditView.vue
│   │   ├── EmploymentView.vue
│   │   ├── ChinaView.vue
│   │   └── MethodologyView.vue
│   ├── services/
│   │   └── dataService.ts
│   ├── types/
│   │   └── indicator.ts
│   └── App.vue
│
├── vite.config.ts
├── package.json
└── README.md
```

---



# 十、评分模型

采用三层计算。

## 第一层：单项指标风险分

对于“数值越大风险越高”的指标：

[
z_i=\frac{x_i-\operatorname{median}(x)}{1.4826 \times MAD(x)}
]

使用 Median 和 MAD，比普通均值和标准差更不容易被危机极值扭曲。

转换成0—100分：

[
score_i=100\times\Phi(z_i)
]

其中 (\Phi) 是标准正态分布的累积分布函数。

## 第二层：子系统评分

```text
信用风险 =
高收益债利差 × 40%
BBB利差 × 25%
信用利差变化速度 × 20%
违约相关指标 × 15%
```



## 第三层：总评分

```text
总危机分 =
流动性 × 20%
信用风险 × 25%
银行压力 × 20%
就业压力 × 15%
实体经济 × 15%
政策异常 × 5%
```

还应加入“共振加分”：

```text
如果信用、银行和就业三个模块同时超过60分：
    总分额外增加10分
```

因为经济危机的核心不是一个指标极端，而是多个子系统共同恶化。

---



# 十一、必须处理的数据问题



## 数据修订

宏观数据会被修订。至少需要保存：

```json
{
  "observationDate": "2026-05-01",
  "value": 123.4,
  "retrievedAt": "2026-07-13T01:20:00Z"
}
```

否则历史回测可能使用修订后的数据，形成前视偏差。

第一版可以暂时使用最新修订值，但页面应明确写：

```text
历史数据采用当前最新修订值，不代表当时可获得的数据。
```

后续可以接入 ALFRED vintage data，重建“当时真实可见”的历史信号。FRED官方说明其 API 可查询 FRED 和 ALFRED 数据。([FRED](https://fred.stlouisfed.org/docs/api/fred/overview.html?utm_source=chatgpt.com))

## 发布日与观察日

例如某个6月份指标可能7月份才发布。

必须区分：

```text
observationDate：数据所属月份
releaseDate：实际发布日期
fetchedAt：系统抓取时间
```



## 缺失数据

不要自动将缺失值填为0。

应记录：

```json
{
  "status": "missing",
  "reason": "source_not_updated"
}
```



## 方向统一

有的指标越高越危险：

```text
VIX
信用利差
失业金申请人数
```

有的越低越危险：

```text
PMI
工业生产增速
职位空缺
M1增速
```

指标配置中应保存：

```json
{
  "riskDirection": "higher_is_worse"
}
```

或：

```json
{
  "riskDirection": "lower_is_worse"
}
```

---



# 十二、部署成本与限制

这套方案可以做到近乎零成本：


| 项目             | 成本       |
| -------------- | -------- |
| GitHub仓库       | 免费       |
| GitHub Pages   | 免费       |
| 公开仓库标准 Actions | 免费       |
| FRED API       | 免费申请     |
| 自定义域名          | 可选，需自行购买 |
| 数据库            | 不需要      |
| 后端服务器          | 不需要      |


GitHub Pages支持 HTTPS，也可以配置自定义域名。([GitHub Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site?utm_source=chatgpt.com))

需要注意：

- 页面和生成的 JSON 默认公开；
- 不能存个人秘密数据；
- 不适合分钟级、高频或实时交易监控；
- Actions计划任务可能延迟；
- 第三方数据源变化时需要维护采集代码；
- GitHub Pages只负责静态内容，不提供传统后端服务。([GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages?utm_source=chatgpt.com))

---



# 十三、最合理的开发顺序

## V0.1：美国危机监控

先做12个核心指标：

```text
VIX
2Y收益率
10Y收益率
10Y-2Y利差
高收益债OAS
BBB债OAS
初请失业金
失业率
工业生产
零售销售
新屋开工
美联储资产负债表
```

实现：

- 数据抓取；
- 图表；
- 历史分位；
- 单项风险等级；
- 总评分；
- GitHub Pages部署。



## V0.2：传导链和事件提醒

加入：

- 指标变化速度；
- 多指标共振；
- 自动事件描述；
- 数据更新时间和失败状态；
- 2008、2020等历史区间标记。



## V0.3：中国模块

加入：

- 社融；
- M1、M2；
-居民中长期贷款；
- 房地产销售；
- 新开工；
- 土地收入；
- PMI；
- PPI；
- 工业企业利润。



## V1.0：危机状态机

最终定义：

```text
NORMAL
LIQUIDITY_STRESS
CREDIT_TIGHTENING
BALANCE_SHEET_RECESSION
REAL_ECONOMY_RECESSION
SYSTEMIC_CRISIS
POLICY_RESCUE
RECOVERY
```

**结论：这个项目完全可以使用 GitHub 免费部署。最佳方案不是让浏览器直接访问所有 API，而是让 GitHub Actions定时生成静态数据，Vue前端负责分析展示。**这样兼顾了密钥安全、稳定性、零服务器成本和可维护性。
