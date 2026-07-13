"""Fetch configured FRED series and produce the static dashboard payload.

Set FRED_API_KEY in GitHub Actions secrets. On per-series failure this script keeps
the last successfully stored observation, so a temporary provider outage never
replaces data with zeroes.
"""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "public" / "data" / "dashboard.json"
SERIES = {
    "VIXCLS": ("VIX 波动率指数", "市场", "", "daily", "higher_is_worse", "level"),
    "DGS2": ("美国 2 年期国债收益率", "市场", "%", "daily", "neutral", "level"),
    "DGS10": ("美国 10 年期国债收益率", "市场", "%", "daily", "neutral", "level"),
    "BAMLH0A0HYM2": ("美国高收益债 OAS", "信用", "%", "daily", "higher_is_worse", "level"),
    "BAMLC0A4CBBB": ("BBB 公司债 OAS", "信用", "%", "daily", "higher_is_worse", "level"),
    "ICSA": ("初请失业金", "就业", "", "weekly", "higher_is_worse", "level"),
    "UNRATE": ("美国失业率", "就业", "%", "monthly", "higher_is_worse", "level"),
    "INDPRO": ("工业生产指数", "实体经济", "", "monthly", "lower_is_worse", "level"),
    "RSAFS": ("零售销售", "实体经济", "M USD", "monthly", "lower_is_worse", "level"),
    "WALCL": ("美联储总资产", "政策", "M USD", "weekly", "neutral", "level"),
    "CPIAUCSL": ("美国 CPI 同比", "通胀", "%", "monthly", "higher_is_worse", "yoy"),
    "PCEPILFE": ("美国核心 PCE 同比", "通胀", "%", "monthly", "higher_is_worse", "yoy"),
    "T5YIE": ("5 年期盈亏平衡通胀率", "通胀", "%", "daily", "higher_is_worse", "level"),
    "DTWEXBGS": ("美元贸易加权指数", "外部冲击", "", "daily", "higher_is_worse", "level"),
    "DCOILWTICO": ("WTI 原油现货价格", "外部冲击", " USD/桶", "daily", "higher_is_worse", "level"),
    "HOUST": ("美国新屋开工", "房地产", "K 套", "monthly", "lower_is_worse", "level"),
    "MORTGAGE30US": ("30 年期固定房贷利率", "房地产", "%", "weekly", "higher_is_worse", "level"),
}

def fred(series_id: str, key: str):
    params = urlencode({"series_id": series_id, "api_key": key, "file_type": "json", "sort_order": "desc", "limit": 260})
    with urlopen(f"https://api.stlouisfed.org/fred/series/observations?{params}", timeout=30) as response:
        rows = json.load(response)["observations"]
    return [(x["date"], float(x["value"])) for x in rows if x["value"] != "."]

def percentile(values, value):
    return round(100 * sum(x <= value for x in values) / len(values)) if values else None

def signal(pct, direction):
    if pct is None or direction == "neutral": return "normal"
    if direction == "lower_is_worse": pct = 100 - pct
    return "danger" if pct >= 90 else "warning" if pct >= 80 else "attention" if pct >= 65 else "normal"

def transformed(rows, method):
    if method == "level":
        return rows[0][1], [x[1] for x in rows]
    values = [100 * (rows[i][1] / rows[i + 12][1] - 1) for i in range(len(rows) - 12)]
    return values[0], values

def item(series_id, name, group, value, unit, p, sig, date, now, frequency):
    return {"id": series_id, "name": name, "group": group, "value": round(value, 3), "unit": unit,
            "percentile": p, "signal": sig, "observationDate": date, "fetchedAt": now,
            "frequency": frequency, "status": "success"}

def main():
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    old = {item["id"]: item for item in payload["indicators"]}
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("FRED_API_KEY is unavailable; keeping existing static observations.")
        return
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    indicators = []
    for series_id, config in SERIES.items():
        name, group, unit, frequency, direction, method = config
        try:
            rows = fred(series_id, key)
            value, values = transformed(rows, method)
            p = percentile(values, value)
            indicators.append(item(series_id, name, group, value, unit, p, signal(p, direction), rows[0][0], now, {"daily":"每日", "weekly":"每周", "monthly":"每月"}[frequency]))
        except Exception as exc:
            print(f"{series_id}: {exc}")
            if series_id in old: indicators.append(old[series_id])
            else: indicators.append({"id":series_id,"name":name,"group":group,"value":None,"unit":unit,"percentile":None,"signal":"normal","observationDate":"—","fetchedAt":now,"frequency":frequency,"status":"missing"})

    # Derived liquidity measures use the latest available observations. WALCL and
    # TGA are millions of dollars; RRP is billions, so units are normalized first.
    try:
        sofr, ff = fred("SOFR", key), fred("FEDFUNDS", key)
        spread = (sofr[0][1] - ff[0][1]) * 100
        indicators.append(item("SOFR_FF_SPREAD", "SOFR-联邦基金利率利差", "银行间", spread, "bp", None,
                               "warning" if spread > 10 else "normal", sofr[0][0], now, "每日"))
    except Exception as exc:
        print(f"SOFR_FF_SPREAD: {exc}")
        if "SOFR_FF_SPREAD" in old: indicators.append(old["SOFR_FF_SPREAD"])

    try:
        walcl, tga, rrp = fred("WALCL", key), fred("WTREGEN", key), fred("RRPONTSYD", key)
        net = (walcl[0][1] - tga[0][1] - rrp[0][1] * 1000) / 1_000_000
        indicators.append(item("FED_NET_LIQUIDITY", "美联储净流动性", "政策", net, "T USD", None,
                               "attention", walcl[0][0], now, "每周"))
    except Exception as exc:
        print(f"FED_NET_LIQUIDITY: {exc}")
        if "FED_NET_LIQUIDITY" in old: indicators.append(old["FED_NET_LIQUIDITY"])

    # GPR is not a FRED series. Preserve the separately maintained observation.
    if "GPR_GLOBAL" in old:
        indicators.append(old["GPR_GLOBAL"])
    # S&P Global PMI requires a separately licensed source. Preserve the latest
    # manually/adaptively maintained observation until that adapter is configured.
    if "SPGLOBAL_US_MFG_PMI" in old:
        indicators.append(old["SPGLOBAL_US_MFG_PMI"])
    payload["generatedAt"] = now
    payload["indicators"] = indicators
    subsystem_weights = {
        "市场流动性": 0.20, "信用风险": 0.20, "银行压力": 0.10,
        "实体经济": 0.20, "就业压力": 0.15, "政策异常": 0.15,
    }
    subsystems = {x["name"]: x["score"] for x in payload["crisis"]["subsystems"]}
    total = sum(subsystems.get(name, 0) * weight for name, weight in subsystem_weights.items())
    if all(subsystems.get(name, 0) > 60 for name in ("信用风险", "银行压力", "就业压力")):
        total += 10
    # Avoid binary floating-point turning a mathematical x.x5 into a lower digit.
    payload["crisis"]["score"] = round(min(total, 100) + 1e-9, 1)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__": main()
