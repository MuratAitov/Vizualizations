import json
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


RAW_DATA = [
    {"Country": "Albania", "Military Deaths": "30,000", "Total Deaths": "30,200"},
    {"Country": "Australia", "Military Deaths": "39,800", "Total Deaths": "40,500"},
    {"Country": "Austria", "Military Deaths": "261,000", "Total Deaths": "384,700"},
    {"Country": "Belgium", "Military Deaths": "12,100", "Total Deaths": "86,100"},
    {"Country": "Brazil", "Military Deaths": "1,000", "Total Deaths": "2,000"},
    {"Country": "Bulgaria", "Military Deaths": "22,000", "Total Deaths": "25,000"},
    {"Country": "Canada", "Military Deaths": "45,400", "Total Deaths": "45,400"},
    {"Country": "China", "Military Deaths": "3-4,000,000", "Total Deaths": "20,000,000"},
    {"Country": "Czechoslovakia", "Military Deaths": "25,000", "Total Deaths": "345,000"},
    {"Country": "Denmark", "Military Deaths": "2,100", "Total Deaths": "3,200"},
    {"Country": "Dutch East Indies", "Military Deaths": "--", "Total Deaths": "3-4,000,000"},
    {"Country": "Estonia", "Military Deaths": "--", "Total Deaths": "51,000"},
    {"Country": "Ethiopia", "Military Deaths": "5,000", "Total Deaths": "100,000"},
    {"Country": "Finland", "Military Deaths": "95,000", "Total Deaths": "97,000"},
    {"Country": "France", "Military Deaths": "217,600", "Total Deaths": "567,600"},
    {"Country": "French Indochina", "Military Deaths": "--", "Total Deaths": "1-1,500,000"},
    {"Country": "Germany", "Military Deaths": "5,533,000", "Total Deaths": "6,600,000-8,800,000"},
    {"Country": "Greece", "Military Deaths": "20,000-35,000", "Total Deaths": "300,000-800,000"},
    {"Country": "Hungary", "Military Deaths": "300,000", "Total Deaths": "580,000"},
    {"Country": "India", "Military Deaths": "87,000", "Total Deaths": "1,500,000-2,500,000"},
    {"Country": "Italy", "Military Deaths": "301,400", "Total Deaths": "457,000"},
    {"Country": "Japan", "Military Deaths": "2,120,000", "Total Deaths": "2,600,000-3,100,000"},
    {"Country": "Korea", "Military Deaths": "--", "Total Deaths": "378,000-473,000"},
    {"Country": "Latvia", "Military Deaths": "--", "Total Deaths": "227,000"},
    {"Country": "Lithuania", "Military Deaths": "--", "Total Deaths": "353,000"},
    {"Country": "Luxembourg", "Military Deaths": "--", "Total Deaths": "2,000"},
    {"Country": "Malaya", "Military Deaths": "--", "Total Deaths": "100,000"},
    {"Country": "Netherlands", "Military Deaths": "17,000", "Total Deaths": "301,000"},
    {"Country": "New Zealand", "Military Deaths": "11,900", "Total Deaths": "11,900"},
    {"Country": "Norway", "Military Deaths": "3,000", "Total Deaths": "9,500"},
    {"Country": "Papua New Guinea", "Military Deaths": "--", "Total Deaths": "15,000"},
    {"Country": "Philippines", "Military Deaths": "57,000", "Total Deaths": "500,000-1,000,000"},
    {"Country": "Poland", "Military Deaths": "240,000", "Total Deaths": "5,600,000"},
    {"Country": "Romania", "Military Deaths": "300,000", "Total Deaths": "833,000"},
    {"Country": "Singapore", "Military Deaths": "--", "Total Deaths": "50,000"},
    {"Country": "South Africa", "Military Deaths": "11,900", "Total Deaths": "11,900"},
    {"Country": "Soviet Union", "Military Deaths": "8,800,000-10,700,000", "Total Deaths": "24,000,000"},
    {"Country": "United Kingdom", "Military Deaths": "383,600", "Total Deaths": "450,700"},
    {"Country": "United States", "Military Deaths": "416,800", "Total Deaths": "418,500"},
    {"Country": "Yugoslavia", "Military Deaths": "446,000", "Total Deaths": "1,000,000"},
]

POP_1939 = {
    "Albania": 1073000,
    "Australia": 7000000,
    "Austria": 6760000,
    "Belgium": 8300000,
    "Brazil": 41000000,
    "Bulgaria": 6300000,
    "Canada": 11400000,
    "China": 517000000,
    "Czechoslovakia": 14800000,
    "Denmark": 3800000,
    "Dutch East Indies": 70000000,
    "Estonia": 1100000,
    "Ethiopia": 17000000,
    "Finland": 3700000,
    "France": 41700000,
    "French Indochina": 24000000,
    "Germany": 69000000,
    "Greece": 7200000,
    "Hungary": 9100000,
    "India": 389000000,
    "Italy": 44400000,
    "Japan": 72000000,
    "Korea": 25000000,
    "Latvia": 1900000,
    "Lithuania": 2600000,
    "Luxembourg": 300000,
    "Malaya": 4800000,
    "Netherlands": 8900000,
    "New Zealand": 1600000,
    "Norway": 3000000,
    "Papua New Guinea": 1000000,
    "Philippines": 16700000,
    "Poland": 35000000,
    "Romania": 19900000,
    "Singapore": 900000,
    "South Africa": 10200000,
    "Soviet Union": 168000000,
    "United Kingdom": 47000000,
    "United States": 131000000,
    "Yugoslavia": 15400000,
}


def _parse_death_text(value: str) -> tuple[float | None, float | None]:
    text = (value or "").strip()
    if text in {"", "--"}:
        return None, None

    text = text.replace(" ", "")

    if "-" not in text:
        number = float(text.replace(",", ""))
        return number, number

    left, right = text.split("-", 1)
    right_clean = right.replace(",", "")

    if "," in right and "," not in left and left.isdigit():
        digits = len(right_clean)
        left_value = float(left) * (10 ** (digits - len(left)))
    else:
        left_value = float(left.replace(",", ""))

    right_value = float(right_clean)
    lo = min(left_value, right_value)
    hi = max(left_value, right_value)
    return lo, hi


def _format_range(lo: float | None, hi: float | None) -> str:
    if lo is None or hi is None:
        return "Unknown"
    if lo == hi:
        return f"{int(lo):,}"
    return f"{int(lo):,} to {int(hi):,}"


@st.cache_data(show_spinner=False)
def _load_df() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in RAW_DATA:
        military_min, military_max = _parse_death_text(row["Military Deaths"])
        total_min, total_max = _parse_death_text(row["Total Deaths"])

        military_avg = (
            (military_min + military_max) / 2
            if military_min is not None and military_max is not None
            else None
        )
        total_avg = (
            (total_min + total_max) / 2
            if total_min is not None and total_max is not None
            else None
        )

        civilian_min = None
        civilian_max = None
        civilian_avg = None
        if (
            military_min is not None
            and military_max is not None
            and total_min is not None
            and total_max is not None
        ):
            civilian_min = max(0.0, total_min - military_max)
            civilian_max = max(0.0, total_max - military_min)
            civilian_avg = (civilian_min + civilian_max) / 2

        rows.append(
            {
                "country": row["Country"],
                "pop_1939": POP_1939.get(row["Country"]),
                "military_text": row["Military Deaths"],
                "total_text": row["Total Deaths"],
                "military_min": military_min,
                "military_max": military_max,
                "military_avg": military_avg,
                "total_min": total_min,
                "total_max": total_max,
                "total_avg": total_avg,
                "civilian_min": civilian_min,
                "civilian_max": civilian_max,
                "civilian_avg": civilian_avg,
                "military_range_label": _format_range(military_min, military_max),
                "total_range_label": _format_range(total_min, total_max),
                "civilian_range_label": _format_range(civilian_min, civilian_max),
            }
        )
    return pd.DataFrame(rows)


def render_hw4() -> None:
    st.subheader("Human Impact: WWII Death Estimates by Country")
    st.markdown(
        """
**Question:** Which countries faced the highest WWII human losses, and how did military and civilian burdens differ?

**Interactivity:** Choose the metric, set country count, and play a country-by-country animated build-up.

**Note:** Several values are ranges. This view uses range midpoints in the animation.
"""
    )

    df = _load_df()

    st.markdown("### Cinematic Growth View")
    st.caption(
        "Play an animated sequence where each country appears and the bar grows to show cumulative human impact."
    )

    c1, c2, c3 = st.columns([1.6, 1, 1])
    with c1:
        metric_focus = st.selectbox(
            "Focus metric",
            options=["Total impact", "Military burden", "Civilian burden"],
            index=0,
            key="metric_focus",
        )
    with c2:
        cinematic_n = st.slider(
            "Countries in animation",
            min_value=5,
            max_value=len(df),
            value=20,
            step=1,
            key="cinematic_n",
        )
    with c3:
        step_ms = st.slider(
            "Base step (ms)",
            min_value=250,
            max_value=3000,
            value=900,
            step=50,
            key="step_ms",
        )

    c4, c5, c6 = st.columns([1.25, 1, 1])
    with c4:
        narrative_mode = st.radio(
            "Narrative mode",
            options=[
                "Absolute deaths",
                "Deaths per 100k people",
                "% of 1939 population",
            ],
            horizontal=False,
            key="narrative_mode",
        )
    with c5:
        memorial_mode = st.checkbox("Memorial mode", value=True, key="memorial_mode")
    with c6:
        pace_multiplier = st.slider(
            "Pace multiplier",
            min_value=0.25,
            max_value=2.0,
            value=1.0,
            step=0.05,
            key="pace_multiplier",
        )
        city_unit = st.slider(
            "City size for equivalence",
            min_value=100000,
            max_value=2000000,
            value=500000,
            step=50000,
            key="city_unit",
        )
        realtime_sec_per_100k = st.slider(
            "Real-time seconds per 100k deaths",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.05,
            key="realtime_sec_per_100k",
            help="0 disables death-based slowdown.",
        )

    focus_map = {
        "Total impact": ("total", "Total impact"),
        "Military burden": ("military", "Military burden"),
        "Civilian burden": ("civilian", "Civilian burden"),
    }
    focus_key, focus_title = focus_map[metric_focus]

    def scale_values(row: pd.Series, key: str) -> tuple[float | None, float | None, float | None]:
        avg = row[f"{key}_avg"]
        lo = row[f"{key}_min"]
        hi = row[f"{key}_max"]
        pop = row["pop_1939"]
        if avg is None:
            return None, None, None

        if narrative_mode == "Absolute deaths":
            return avg, lo, hi
        if pop is None or pop <= 0:
            return None, None, None
        if narrative_mode == "Deaths per 100k people":
            factor = 100000.0 / pop
            return avg * factor, lo * factor, hi * factor
        factor = 100.0 / pop
        return avg * factor, lo * factor, hi * factor

    cinematic_df = df[
        df["total_avg"].notna()
        & df["military_avg"].notna()
        & df["civilian_avg"].notna()
    ].copy()
    if narrative_mode != "Absolute deaths":
        cinematic_df = cinematic_df[cinematic_df["pop_1939"].notna()].copy()

    total_scaled = cinematic_df.apply(lambda r: scale_values(r, "total"), axis=1)
    military_scaled = cinematic_df.apply(lambda r: scale_values(r, "military"), axis=1)
    civilian_scaled = cinematic_df.apply(lambda r: scale_values(r, "civilian"), axis=1)

    cinematic_df["total_scaled"] = [v[0] for v in total_scaled]
    cinematic_df["total_scaled_min"] = [v[1] for v in total_scaled]
    cinematic_df["total_scaled_max"] = [v[2] for v in total_scaled]
    cinematic_df["military_scaled"] = [v[0] for v in military_scaled]
    cinematic_df["military_scaled_min"] = [v[1] for v in military_scaled]
    cinematic_df["military_scaled_max"] = [v[2] for v in military_scaled]
    cinematic_df["civilian_scaled"] = [v[0] for v in civilian_scaled]
    cinematic_df["civilian_scaled_min"] = [v[1] for v in civilian_scaled]
    cinematic_df["civilian_scaled_max"] = [v[2] for v in civilian_scaled]

    focus_col = {
        "total": "total_scaled",
        "military": "military_scaled",
        "civilian": "civilian_scaled",
    }[focus_key]

    cinematic_df = cinematic_df[cinematic_df[focus_col].notna()].copy()
    cinematic_df = (
        cinematic_df.sort_values(focus_col, ascending=False)
        .head(cinematic_n)
        .sort_values(focus_col, ascending=True)
        .copy()
    )
    cinematic_df["metric_value"] = cinematic_df[focus_col]
    cinematic_rows = cinematic_df[
        [
            "country",
            "metric_value",
            "pop_1939",
            "total_scaled",
            "total_scaled_min",
            "total_scaled_max",
            "military_avg",
            "military_scaled",
            "civilian_avg",
            "civilian_scaled",
            "total_avg",
            "military_scaled_min",
            "military_scaled_max",
            "civilian_scaled_min",
            "civilian_scaled_max",
            "military_range_label",
            "total_range_label",
            "civilian_range_label",
        ]
    ].to_dict(orient="records")
    components.html(
        _build_cinematic_html(
            rows=cinematic_rows,
            metric_title=focus_title,
            step_ms=step_ms,
            narrative_mode=narrative_mode,
            memorial_mode=memorial_mode,
            pace_multiplier=pace_multiplier,
            city_unit=city_unit,
            realtime_sec_per_100k=realtime_sec_per_100k,
        ),
        height=700,
    )


def _build_cinematic_html(
    rows: list[dict[str, Any]],
    metric_title: str,
    step_ms: int,
    narrative_mode: str,
    memorial_mode: bool,
    pace_multiplier: float,
    city_unit: int,
    realtime_sec_per_100k: float,
) -> str:
    data_json = json.dumps(rows)
    title_json = json.dumps(metric_title)
    mode_json = json.dumps(narrative_mode)
    memorial_json = "true" if memorial_mode else "false"
    pace_json = json.dumps(float(pace_multiplier))
    city_unit_json = json.dumps(int(city_unit))
    realtime_pace_json = json.dumps(float(realtime_sec_per_100k))
    return f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
      body {{
        margin: 0;
        font-family: "Segoe UI", Arial, sans-serif;
        background: radial-gradient(circle at 20% 10%, #1f2937 0%, #0f172a 50%, #020617 100%);
        color: #f8fafc;
      }}
      body.memorial {{
        background: radial-gradient(circle at 50% 12%, #111827 0%, #030712 62%, #000000 100%);
      }}
      .wrap {{
        padding: 18px;
      }}
      .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      }}
      .title {{
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.2px;
      }}
      .subtitle {{
        font-size: 12px;
        color: #cbd5e1;
        margin-top: 4px;
      }}
      .controls {{
        display: flex;
        gap: 8px;
      }}
      button {{
        border: 1px solid rgba(148, 163, 184, 0.35);
        background: rgba(15, 23, 42, 0.8);
        color: #e2e8f0;
        border-radius: 8px;
        padding: 6px 10px;
        cursor: pointer;
        font-size: 12px;
      }}
      button:hover {{
        background: rgba(30, 41, 59, 0.92);
      }}
      .panel {{
        margin-top: 8px;
        display: grid;
        grid-template-columns: 1fr 310px;
        gap: 10px;
      }}
      .chart-card, .info-card {{
        border: 1px solid rgba(148, 163, 184, 0.2);
        background: rgba(15, 23, 42, 0.55);
        border-radius: 14px;
      }}
      .chart-card {{
        padding: 10px 10px 6px 10px;
      }}
      .info-card {{
        padding: 14px;
        font-size: 13px;
      }}
      .kpi {{
        margin-bottom: 12px;
      }}
      .kpi-label {{
        color: #93c5fd;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.7px;
      }}
      .kpi-value {{
        font-size: 22px;
        font-weight: 700;
        margin-top: 2px;
      }}
      .country {{
        margin-top: 8px;
        font-size: 17px;
        font-weight: 650;
      }}
      .meta {{
        color: #cbd5e1;
        font-size: 12px;
        margin-top: 8px;
        line-height: 1.35;
      }}
      .progress {{
        margin-top: 10px;
        color: #93c5fd;
      }}
      .axis text {{
        fill: #cbd5e1;
        font-size: 11px;
      }}
      .axis path, .axis line {{
        stroke: rgba(203, 213, 225, 0.3);
      }}
      .bar-label {{
        fill: #e2e8f0;
        font-size: 11px;
      }}
      .uncertainty {{
        stroke: rgba(255, 255, 255, 0.28);
        stroke-width: 2;
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="header">
        <div>
          <div class="title">Human Impact: Animated Country Build-Up</div>
          <div class="subtitle">Countries appear one-by-one and cumulative deaths grow at each step.</div>
        </div>
        <div class="controls">
          <button id="playBtn">Play</button>
          <button id="pauseBtn">Pause</button>
          <button id="restartBtn">Restart</button>
        </div>
      </div>
      <div class="panel">
        <div class="chart-card">
          <svg id="chart" width="100%" height="600" viewBox="0 0 980 600"></svg>
        </div>
        <div class="info-card">
          <div class="kpi">
            <div class="kpi-label">Metric</div>
            <div id="metricName" class="kpi-value"></div>
          </div>
          <div class="kpi">
            <div class="kpi-label">Cumulative Total</div>
            <div id="cumulative" class="kpi-value">0</div>
          </div>
          <div class="kpi">
            <div class="kpi-label">Cumulative Military</div>
            <div id="cumulativeMilitary" class="kpi-value" style="color:#f97316">0</div>
          </div>
          <div class="kpi">
            <div class="kpi-label">Cumulative Civilian</div>
            <div id="cumulativeCivilian" class="kpi-value" style="color:#38bdf8">0</div>
          </div>
          <div class="kpi">
            <div class="kpi-label">Current Country</div>
            <div id="countryName" class="country">-</div>
          </div>
          <div id="countryMeta" class="meta">Press Play to start animation.</div>
          <div id="cityEq" class="meta"></div>
          <div id="progress" class="progress"></div>
          <div class="meta" style="margin-top:12px;">
            <strong style="color:#f97316">Military</strong> + <strong style="color:#38bdf8">Civilian</strong> = Total
          </div>
        </div>
      </div>
    </div>
    <script>
      const allData = {data_json};
      const metricTitle = {title_json};
      const narrativeMode = {mode_json};
      const memorialMode = {memorial_json};
      const paceMultiplier = {pace_json};
      const cityUnit = {city_unit_json};
      const realtimeSecPer100k = {realtime_pace_json};
      const stepMs = {int(step_ms)};
      const totalAnim = Math.max(160, Math.floor(stepMs * 0.78));
      const repositionAnim = Math.max(90, Math.floor(totalAnim * 0.34));
      const growAnim = Math.max(70, totalAnim - repositionAnim);
      const militaryAnim = Math.max(50, Math.floor(growAnim * 0.55));
      const civilianAnim = Math.max(40, growAnim - militaryAnim);
      const minStepGap = totalAnim + 40;

      if (memorialMode) document.body.classList.add("memorial");

      const usCities = [
        {{ name: "New York", pop: 8336817 }},
        {{ name: "Los Angeles", pop: 3820914 }},
        {{ name: "Chicago", pop: 2664452 }},
        {{ name: "Houston", pop: 2304580 }},
        {{ name: "Phoenix", pop: 1650070 }},
        {{ name: "Philadelphia", pop: 1553697 }},
        {{ name: "San Antonio", pop: 1492510 }},
        {{ name: "San Diego", pop: 1386932 }},
        {{ name: "Dallas", pop: 1304379 }},
        {{ name: "San Jose", pop: 1013240 }},
        {{ name: "Seattle", pop: 755078 }},
        {{ name: "Denver", pop: 716577 }},
        {{ name: "Boston", pop: 653833 }},
        {{ name: "Portland", pop: 630498 }},
        {{ name: "Las Vegas", pop: 660929 }},
        {{ name: "Boise", pop: 235684 }},
        {{ name: "Spokane Valley", pop: 108235 }},
        {{ name: "Coeur d'Alene", pop: 56208 }},
        {{ name: "Post Falls", pop: 38950 }},
        {{ name: "Yakima", pop: 97044 }},
        {{ name: "Kennewick", pop: 83921 }},
        {{ name: "Pasco", pop: 80446 }},
        {{ name: "Richland", pop: 64206 }},
        {{ name: "Walla Walla", pop: 34655 }},
        {{ name: "Moscow (ID)", pop: 25852 }},
        {{ name: "Pullman", pop: 32495 }},
        {{ name: "Lewiston", pop: 34668 }},
        {{ name: "Clarkston", pop: 7310 }},
        {{ name: "Sandpoint", pop: 9277 }},
        {{ name: "Missoula", pop: 76788 }},
        {{ name: "Billings", pop: 119960 }},
        {{ name: "Great Falls", pop: 60252 }},
        {{ name: "Bend", pop: 104557 }},
        {{ name: "Salem", pop: 177723 }},
        {{ name: "Eugene", pop: 176654 }},
        {{ name: "Spokane", pop: 229447 }},
      ];
      const spokanePop = usCities.find(c => c.name === "Spokane").pop;
      const baseCityCandidates = usCities
        .slice()
        .sort((a, b) => Math.abs(a.pop - cityUnit) - Math.abs(b.pop - cityUnit));
      let baseTargetCity = baseCityCandidates[0];
      if (baseTargetCity && baseTargetCity.name === "Spokane" && baseCityCandidates.length > 1) {{
        baseTargetCity = baseCityCandidates[1];
      }}

      const svg = d3.select("#chart");
      const width = 980;
      const height = 600;
      const margin = {{ top: 22, right: 18, bottom: 32, left: 190 }};
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;
      const g = svg.append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);

      const metricName = document.getElementById("metricName");
      const cumulativeEl = document.getElementById("cumulative");
      const cumulativeMilitaryEl = document.getElementById("cumulativeMilitary");
      const cumulativeCivilianEl = document.getElementById("cumulativeCivilian");
      const countryNameEl = document.getElementById("countryName");
      const countryMetaEl = document.getElementById("countryMeta");
      const cityEqEl = document.getElementById("cityEq");
      const progressEl = document.getElementById("progress");
      metricName.textContent = metricTitle;

      const x = d3.scaleLinear().range([0, innerW]);
      const y = d3.scaleBand().range([0, innerH]).padding(0.16);

      const xAxis = g.append("g").attr("class", "axis").attr("transform", `translate(0,${{innerH}})`);
      const yAxis = g.append("g").attr("class", "axis");

      const grid = g.append("g").attr("opacity", 0.18);
      const uncertaintyLayer = g.append("g");
      const militaryLayer = g.append("g");
      const civilianLayer = g.append("g");
      const labelsLayer = g.append("g");

      let visible = [];
      let idx = 0;
      let timer = null;
      let isPlaying = false;
      let lastPickedCityName = "";

      function fmtMode(value) {{
        if (narrativeMode === "Absolute deaths") return d3.format(",.0f")(value);
        if (narrativeMode === "Deaths per 100k people") return d3.format(",.1f")(value);
        return `${{d3.format(".2f")(value)}}%`;
      }}

      function fmtAbs(value) {{
        return d3.format(",.0f")(value || 0);
      }}

      function pickDynamicCity(totalAbs, stepNo) {{
        const nonSpokane = usCities.filter(c => c.name !== "Spokane");
        if (!nonSpokane.length) return baseTargetCity;
        // Vary target multiplier by step so city label changes while staying scale-relevant.
        const targets = [2, 3, 4, 6, 8, 12, 18, 25];
        const target = targets[Math.max(0, (stepNo - 1) % targets.length)];
        const ranked = nonSpokane
          .slice()
          .sort((a, b) => Math.abs(totalAbs / a.pop - target) - Math.abs(totalAbs / b.pop - target));
        // Avoid repeating the same city too many steps in a row.
        const next = ranked.find(c => c.name !== lastPickedCityName) || ranked[0] || baseTargetCity;
        lastPickedCityName = next.name;
        return next;
      }}

      function cityEquivalence(totalAbs, stepNo) {{
        const mainCity = pickDynamicCity(totalAbs, stepNo);
        const mainEq = totalAbs / mainCity.pop;
        const spokaneEq = totalAbs / spokanePop;
        return `Equivalent to about ${{mainEq.toFixed(1)}} x ${{mainCity.name}} | Spokane: ${{spokaneEq.toFixed(1)}} x`;
      }}

      function computeDelay(lastItem) {{
        const baseDelay = Math.max(minStepGap, stepMs / Math.max(0.1, paceMultiplier));
        if (realtimeSecPer100k <= 0) return baseDelay;
        const deaths = lastItem.total_avg || 0;
        const realtimeDelay = (deaths / 100000.0) * realtimeSecPer100k * 1000;
        return Math.max(baseDelay, realtimeDelay);
      }}

      function updateSidePanel(lastItem) {{
        const totalScaledSum = d3.sum(visible, d => d.total_scaled || 0);
        const militaryScaledSum = d3.sum(visible, d => d.military_scaled || 0);
        const civilianScaledSum = d3.sum(visible, d => d.civilian_scaled || 0);
        const totalAbsSum = d3.sum(visible, d => d.total_avg || 0);
        cumulativeEl.textContent = fmtMode(totalScaledSum);
        cumulativeMilitaryEl.textContent = fmtMode(militaryScaledSum);
        cumulativeCivilianEl.textContent = fmtMode(civilianScaledSum);
        if (lastItem) {{
          const lossPct = lastItem.pop_1939 ? (100 * (lastItem.total_avg || 0) / lastItem.pop_1939) : null;
          const survivedPct = lossPct !== null ? Math.max(0, 100 - lossPct) : null;
          countryNameEl.textContent = lastItem.country;
          countryMetaEl.innerHTML =
            `Military: ${{lastItem.military_range_label}}<br/>` +
            `Total: ${{lastItem.total_range_label}}<br/>` +
            `Civilian (derived): ${{lastItem.civilian_range_label}}` +
            (lossPct !== null
              ? `<br/>Population impact: ${{lossPct.toFixed(2)}}% lost, ${{survivedPct.toFixed(2)}}% survived`
              : "");
          cityEqEl.textContent = cityEquivalence(lastItem.total_avg || 0, visible.length);
        }}
        progressEl.textContent =
          `Progress: ${{visible.length}} / ${{allData.length}} countries | absolute cumulative: ${{fmtAbs(totalAbsSum)}}`;
      }}

      function render(lastItem = null) {{
        const local = visible.slice().sort((a, b) => b.metric_value - a.metric_value);
        const maxValue = d3.max(local, d => d.total_scaled || 0) || 1;

        x.domain([0, maxValue * 1.08]);
        y.domain(local.map(d => d.country));

        xAxis
          .transition()
          .duration(repositionAnim)
          .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format(",")));

        yAxis
          .transition()
          .duration(repositionAnim)
          .call(d3.axisLeft(y));

        const gridLines = grid.selectAll("line").data(x.ticks(6), d => d);
        gridLines.enter()
          .append("line")
          .merge(gridLines)
          .attr("x1", d => x(d))
          .attr("x2", d => x(d))
          .attr("y1", 0)
          .attr("y2", innerH)
          .attr("stroke", "#cbd5e1");
        gridLines.exit().remove();

        const uncertainty = uncertaintyLayer.selectAll("line").data(local, d => d.country);
        uncertainty.enter()
          .append("line")
          .attr("class", "uncertainty")
          .merge(uncertainty)
          .transition()
          .duration(repositionAnim)
          .attr("x1", d => x(d.total_scaled_min || d.total_scaled || 0))
          .attr("x2", d => x(d.total_scaled_max || d.total_scaled || 0))
          .attr("y1", d => (y(d.country) || 0) + y.bandwidth() / 2)
          .attr("y2", d => (y(d.country) || 0) + y.bandwidth() / 2);
        uncertainty.exit().remove();

        const militaryBars = militaryLayer.selectAll("rect").data(local, d => d.country);
        militaryBars.enter()
          .append("rect")
          .attr("class", "military")
          .attr("x", 0)
          .attr("y", d => y(d.country))
          .attr("height", y.bandwidth())
          .attr("width", 0)
          .attr("rx", 5)
          .attr("fill", "#f97316")
          .attr("opacity", 0.92)
          .merge(militaryBars)
          .transition()
          .delay(d => (lastItem && d.country === lastItem.country ? repositionAnim : 0))
          .duration(d => (lastItem && d.country === lastItem.country ? militaryAnim : repositionAnim))
          .attr("y", d => y(d.country))
          .attr("height", y.bandwidth())
          .attr("width", d => x(d.military_scaled || 0));
        militaryBars.exit().remove();

        const civilianBars = civilianLayer.selectAll("rect").data(local, d => d.country);
        civilianBars.enter()
          .append("rect")
          .attr("class", "civilian")
          .attr("x", d => x(d.military_scaled || 0))
          .attr("y", d => y(d.country))
          .attr("height", y.bandwidth())
          .attr("width", 0)
          .attr("fill", "#38bdf8")
          .attr("opacity", 0.9)
          .merge(civilianBars)
          .transition()
          .delay(d => (
            lastItem && d.country === lastItem.country
              ? repositionAnim + militaryAnim
              : 0
          ))
          .duration(d => (
            lastItem && d.country === lastItem.country
              ? civilianAnim
              : repositionAnim
          ))
          .attr("x", d => x(d.military_scaled || 0))
          .attr("y", d => y(d.country))
          .attr("height", y.bandwidth())
          .attr("width", d => Math.max(0, x(d.total_scaled || 0) - x(d.military_scaled || 0)));
        civilianBars.exit().remove();

        const labels = labelsLayer.selectAll("text").data(local, d => d.country);
        labels.enter()
          .append("text")
          .attr("class", "bar-label")
          .attr("x", 6)
          .attr("y", d => (y(d.country) || 0) + y.bandwidth() / 2 + 4)
          .text("")
          .merge(labels)
          .transition()
          .delay(d => (
            lastItem && d.country === lastItem.country
              ? repositionAnim + militaryAnim + Math.floor(civilianAnim * 0.4)
              : 0
          ))
          .duration(d => (
            lastItem && d.country === lastItem.country
              ? Math.floor(civilianAnim * 0.6)
              : repositionAnim
          ))
          .attr("x", d => x(d.total_scaled || 0) + 8)
          .attr("y", d => (y(d.country) || 0) + y.bandwidth() / 2 + 4)
          .tween("text", function(d) {{
            const current = Number(this.textContent.replace(/,/g, "").replace("%", "")) || 0;
            const i = d3.interpolateNumber(current, d.total_scaled || 0);
            return function(t) {{
              this.textContent = fmtMode(i(t));
            }};
          }});
        labels.exit().remove();

        updateSidePanel(lastItem);
      }}

      function step() {{
        if (idx >= allData.length) {{
          pause();
          return null;
        }}
        visible.push(allData[idx]);
        const last = allData[idx];
        idx += 1;
        render(last);
        return last;
      }}

      function loop() {{
        if (!isPlaying) return;
        const last = step();
        if (!last) {{
          isPlaying = false;
          return;
        }}
        timer = window.setTimeout(loop, computeDelay(last));
      }}

      function play() {{
        if (isPlaying) return;
        isPlaying = true;
        loop();
      }}

      function pause() {{
        isPlaying = false;
        if (!timer) return;
        clearTimeout(timer);
        timer = null;
      }}

      function restart() {{
        pause();
        visible = [];
        idx = 0;
        lastPickedCityName = "";
        render();
      }}

      document.getElementById("playBtn").addEventListener("click", play);
      document.getElementById("pauseBtn").addEventListener("click", pause);
      document.getElementById("restartBtn").addEventListener("click", restart);

      render();
    </script>
  </body>
</html>
"""
