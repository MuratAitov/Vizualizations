import json
import os

import kagglehub
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    local_path = os.path.join(os.getcwd(), "top_rated_movies.csv")
    if os.path.exists(local_path):
        file_path = local_path
    else:
        path = kagglehub.dataset_download(
            "shraddha4ever20/top-rated-movies-from-tmdb-19902025"
        )
        file_path = os.path.join(path, "top_rated_movies.csv")
    df = pd.read_csv(file_path)
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year
    df = df.dropna(
        subset=["release_year", "popularity", "vote_average", "vote_count", "title"]
    )
    df["release_year"] = df["release_year"].astype(int)
    return df


def render_hw2() -> None:
    st.subheader("Showing Data")

    df = load_data()

    st.markdown(
        """
**Dataset description:** Top-rated movies from TMDB (via Kaggle), including title,
overview, release date, popularity, average rating, and vote counts.

**Question:** How do ratings and popularity interact across release years, and which
movies stand out as both highly rated and widely popular?

**Interpretation:** Focus on points high in both rating and popularity; clusters by year
show whether certain eras produce more standout films.
"""
    )

    min_year = int(df["release_year"].min())
    max_year = int(df["release_year"].max())
    default_low = max(min_year, 1990)
    default_high = max_year
    year_range = st.slider(
        "Release year range",
        min_value=min_year,
        max_value=max_year,
        value=(default_low, default_high),
    )

    min_votes = st.slider(
        "Minimum vote count",
        min_value=0,
        max_value=int(df["vote_count"].max()),
        value=1000,
        step=100,
    )

    max_points = st.slider(
        "Max points (performance)",
        min_value=200,
        max_value=3000,
        value=1200,
        step=100,
    )

    bin_size = st.selectbox("Year grouping", options=[5, 10], index=0)

    filtered = df[
        (df["release_year"].between(year_range[0], year_range[1]))
        & (df["vote_count"] >= min_votes)
    ].copy()

    filtered = filtered.sort_values("vote_count", ascending=False).head(max_points)
    filtered["year_bin_start"] = (filtered["release_year"] // bin_size) * bin_size
    filtered["year_bin_label"] = (
        filtered["year_bin_start"].astype(int).astype(str)
        + "-"
        + (filtered["year_bin_start"] + bin_size - 1).astype(int).astype(str)
    )

    chart_data = filtered[
        [
            "title",
            "release_year",
            "vote_average",
            "popularity",
            "vote_count",
            "year_bin_label",
        ]
    ].to_dict(orient="records")

    data_json = json.dumps(chart_data)

    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
      .chart-wrap {
        background: linear-gradient(180deg, #ffffff 0%, #f6f7fb 100%);
        border: 1px solid #e1e1e1;
        border-radius: 16px;
        padding: 16px;
        padding-bottom: 24px;
      }
      .info-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 12px;
      }
      .info-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        font: 12px/1.4 Arial, sans-serif;
        color: #111827;
      }
      .side-title {
        font: 700 13px/1.2 Arial, sans-serif;
        margin-bottom: 8px;
      }
      .detail-row {
        margin-bottom: 6px;
      }
      .legend {
        margin-top: 10px;
      }
      .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        cursor: pointer;
      }
      .legend-swatch {
        width: 12px;
        height: 12px;
        border-radius: 3px;
        border: 1px solid #e5e7eb;
      }
      .title {
        font: 700 18px/1.2 Arial, sans-serif;
        margin-bottom: 8px;
      }
      .tooltip {
        position: absolute;
        pointer-events: none;
        background: #111827;
        color: #f9fafb;
        padding: 8px 10px;
        border-radius: 8px;
        font: 12px/1.2 Arial, sans-serif;
        opacity: 0;
      }
      .axis text {
        font: 12px Arial, sans-serif;
        fill: #374151;
      }
      .axis path,
      .axis line {
        stroke: #cbd5e1;
      }
    </style>
  </head>
  <body>
    <div class="chart-wrap">
      <div class="title">Top Rated Movies: Rating vs Popularity</div>
      <svg id="chart" width="100%" height="700" viewBox="0 0 900 700"></svg>
      <div class="info-row">
        <div class="info-card">
          <div class="side-title">Movie Details (click a point)</div>
          <div id="details">
            Click a point to pin a movie here.
          </div>
        </div>
        <div class="info-card">
          <div class="side-title">Year Groups</div>
          <div id="legend" class="legend"></div>
        </div>
      </div>
    </div>
    <div id="tooltip" class="tooltip"></div>
    <script>
      const data = __DATA__;
      const svg = d3.select("#chart");
      const width = 900;
      const height = 700;
      const margin = { top: 30, right: 24, bottom: 60, left: 70 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;

      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      const x = d3.scaleLinear()
        .domain(d3.extent(data, d => d.vote_average))
        .nice()
        .range([0, innerW]);

      const y = d3.scaleLinear()
        .domain(d3.extent(data, d => d.popularity))
        .nice()
        .range([innerH, 0]);

      const r = d3.scaleSqrt()
        .domain(d3.extent(data, d => d.vote_count))
        .range([3, 18]);

      const bins = Array.from(new Set(data.map(d => d.year_bin_label))).sort();
      const c = d3.scaleOrdinal()
        .domain(bins)
        .range(d3.schemeTableau10.concat(d3.schemeSet3).slice(0, bins.length));

      const details = d3.select("#details");
      function renderDetails(d) {
        details.html(
          `<div class="detail-row"><strong>${d.title}</strong></div>` +
          `<div class="detail-row">Year: ${d.release_year}</div>` +
          `<div class="detail-row">Group: ${d.year_bin_label}</div>` +
          `<div class="detail-row">Rating: ${d.vote_average.toFixed(2)}</div>` +
          `<div class="detail-row">Popularity: ${d.popularity.toFixed(2)}</div>` +
          `<div class="detail-row">Votes: ${d.vote_count}</div>`
        );
      }

      g.append("g").attr("class", "axis")
        .attr("transform", `translate(0,${innerH})`)
        .call(d3.axisBottom(x));

      g.append("g").attr("class", "axis")
        .call(d3.axisLeft(y));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 45)
        .attr("text-anchor", "middle")
        .attr("fill", "#111827")
        .style("font", "13px Arial, sans-serif")
        .text("Average Rating");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -50)
        .attr("text-anchor", "middle")
        .attr("fill", "#111827")
        .style("font", "13px Arial, sans-serif")
        .text("Popularity");

      const tooltip = d3.select("#tooltip");
      let activeGroup = null;

      const circles = g.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.vote_average))
        .attr("cy", d => y(d.popularity))
        .attr("r", d => r(d.vote_count))
        .attr("fill", d => c(d.year_bin_label))
        .attr("fill-opacity", 0.85)
        .attr("stroke", "#111827")
        .attr("stroke-opacity", 0.2)
        .style("cursor", "pointer")
        .on("click", (event, d) => {
          renderDetails(d);
        })
        .on("mousemove", (event, d) => {
          tooltip
            .style("opacity", 1)
            .style("left", (event.pageX + 12) + "px")
            .style("top", (event.pageY - 28) + "px")
            .html(
              `<strong>${d.title}</strong><br/>` +
              `Year: ${d.release_year}<br/>` +
              `Group: ${d.year_bin_label}<br/>` +
              `Rating: ${d.vote_average.toFixed(2)}<br/>` +
              `Popularity: ${d.popularity.toFixed(2)}<br/>` +
              `Votes: ${d.vote_count}`
            );
        })
        .on("mouseleave", () => {
          tooltip.style("opacity", 0);
        });

      const legend = d3.select("#legend");
      const legendItems = legend.selectAll("div")
        .data(bins)
        .enter()
        .append("div")
        .attr("class", "legend-item");

      legendItems.append("span")
        .attr("class", "legend-swatch")
        .style("background", d => c(d));

      legendItems.append("span")
        .text(d => d);

      function updateOpacity() {
        circles
          .attr("fill-opacity", d => !activeGroup ? 0.85 : (d.year_bin_label === activeGroup ? 0.9 : 0.12))
          .attr("stroke-opacity", d => !activeGroup ? 0.2 : (d.year_bin_label === activeGroup ? 0.5 : 0.1));
        legendItems.style("opacity", d => !activeGroup ? 1 : (d === activeGroup ? 1 : 0.35));
      }

      legendItems.on("click", (event, d) => {
        activeGroup = activeGroup === d ? null : d;
        updateOpacity();
      });

    </script>
  </body>
</html>
"""

    html = html.replace("__DATA__", data_json)
    components.html(html, height=1050)
