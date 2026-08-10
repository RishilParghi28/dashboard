import os
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

DATA_PATH = os.getenv("SUPERSTORE_CSV", "Superstore_Clean.csv")


def load_csv(path):
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            pass
    try:
        return pd.read_csv(path, encoding="latin1", encoding_errors="replace")
    except TypeError:
        return pd.read_csv(path, encoding="latin1")


df = load_csv(DATA_PATH)

df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True, errors="coerce")

df["Order Year"] = df["Order Date"].dt.year
df["Order Month"] = df["Order Date"].dt.to_period("M").astype(str)
df["Order Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

df["Profit Margin"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"], 0.0)

df = df.dropna(subset=["Order Date"])

min_date = df["Order Date"].min()
max_date = df["Order Date"].max()

regions = sorted(df["Region"].dropna().unique().tolist())
segments = sorted(df["Segment"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())
ship_modes = sorted(df["Ship Mode"].dropna().unique().tolist())


def money(x):
    return "${:,.0f}".format(x)


def pct(x):
    return "{:.1%}".format(x)


def polish_dark(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial",
            size=12,
            color="#e5e7eb",
        ),
        title_font=dict(size=16, color="#f3f4f6"),
        legend_title_font=dict(color="#e5e7eb"),
        legend_font=dict(color="#e5e7eb"),
        margin=dict(l=12, r=12, t=48, b=12),
    )
    fig.update_xaxes(
        gridcolor="rgba(148,163,184,0.12)",
        zerolinecolor="rgba(148,163,184,0.12)",
    )
    fig.update_yaxes(
        gridcolor="rgba(148,163,184,0.12)",
        zerolinecolor="rgba(148,163,184,0.12)",
    )
    return fig


def apply_filters(d, start_date, end_date, region, segment, category, shipmode):
    out = d[(d["Order Date"] >= pd.to_datetime(start_date)) & (d["Order Date"] <= pd.to_datetime(end_date))]
    if region != "__ALL__":
        out = out[out["Region"] == region]
    if segment != "__ALL__":
        out = out[out["Segment"] == segment]
    if category != "__ALL__":
        out = out[out["Category"] == category]
    if shipmode != "__ALL__":
        out = out[out["Ship Mode"] == shipmode]
    return out


app = Dash(__name__)
app.title = "Superstore — Plotly Dash"


app.layout = html.Div(
    style={
        "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial",
        "background": "radial-gradient(1200px 600px at 15% 0%, rgba(168,85,247,0.22) 0%, rgba(17,24,39,0) 60%),"
        "radial-gradient(900px 520px at 85% 10%, rgba(99,102,241,0.18) 0%, rgba(17,24,39,0) 60%),"
        "linear-gradient(180deg, #0b1020 0%, #070a14 100%)",
        "minHeight": "100vh",
        "padding": "22px",
        "color": "#e5e7eb",
    },
    children=[
        

        html.Div(
            style={"maxWidth": "1200px", "margin": "0 auto"},
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "gap": "12px",
                        "marginBottom": "14px",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    "Superstore",
                                    style={
                                        "fontSize": "13px",
                                        "color": "#a78bfa",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.06em",
                                        "textTransform": "uppercase",
                                    },
                                ),
                                html.H2(
                                    "Executive Dashboard",
                                    style={
                                        "margin": "4px 0 0 0",
                                        "fontWeight": "900",
                                        "letterSpacing": "-0.02em",
                                        "color": "#f3f4f6",
                                    },
                                ),
                            ]
                        ),
                        html.Div(
                            id="record-count",
                            style={
                                "padding": "8px 12px",
                                "border": "1px solid rgba(148,163,184,0.18)",
                                "borderRadius": "999px",
                                "background": "rgba(255,255,255,0.06)",
                                "backdropFilter": "blur(8px)",
                                "color": "#e5e7eb",
                                "fontWeight": "700",
                                "fontSize": "13px",
                            },
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, 1fr)",
                        "gap": "12px",
                        "marginBottom": "12px",
                    },
                    children=[
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "14px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[
                                html.Div(
                                    "Total Sales",
                                    style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                ),
                                html.Div(
                                    id="kpi-sales",
                                    style={
                                        "fontSize": "28px",
                                        "fontWeight": "950",
                                        "marginTop": "6px",
                                        "color": "#f3f4f6",
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "14px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[
                                html.Div(
                                    "Total Profit",
                                    style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                ),
                                html.Div(
                                    id="kpi-profit",
                                    style={
                                        "fontSize": "28px",
                                        "fontWeight": "950",
                                        "marginTop": "6px",
                                        "color": "#f3f4f6",
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "14px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[
                                html.Div(
                                    "Profit Margin",
                                    style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                ),
                                html.Div(
                                    id="kpi-margin",
                                    style={
                                        "fontSize": "28px",
                                        "fontWeight": "950",
                                        "marginTop": "6px",
                                        "color": "#f3f4f6",
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "14px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[
                                html.Div(
                                    "Orders",
                                    style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                ),
                                html.Div(
                                    id="kpi-orders",
                                    style={
                                        "fontSize": "28px",
                                        "fontWeight": "950",
                                        "marginTop": "6px",
                                        "color": "#f3f4f6",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "background": "rgba(255,255,255,0.06)",
                        "border": "1px solid rgba(148,163,184,0.14)",
                        "borderRadius": "16px",
                        "padding": "12px",
                        "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                        "marginBottom": "12px",
                    },
                    children=[
                        html.Div(
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "1.6fr 1fr 1fr 1fr 1fr",
                                "gap": "10px",
                                "alignItems": "end",
                            },
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Order Date Range",
                                            style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                        ),
                                        dcc.DatePickerRange(
                                            id="date-range",
                                            min_date_allowed=min_date,
                                            max_date_allowed=max_date,
                                            start_date=min_date,
                                            end_date=max_date,
                                            display_format="YYYY-MM-DD",
                                            style={"marginTop": "6px"},
                                            className="dark-date",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Region",
                                            style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                        ),
                                        dcc.Dropdown(
                                            id="region",
                                            options=[{"label": "All", "value": "__ALL__"}]
                                            + [{"label": r, "value": r} for r in regions],
                                            value="__ALL__",
                                            clearable=False,
                                            style={"marginTop": "6px"},
                                            className="dark-input",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Segment",
                                            style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                        ),
                                        dcc.Dropdown(
                                            id="segment",
                                            options=[{"label": "All", "value": "__ALL__"}]
                                            + [{"label": s, "value": s} for s in segments],
                                            value="__ALL__",
                                            clearable=False,
                                            style={"marginTop": "6px"},
                                            className="dark-input",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Category",
                                            style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                        ),
                                        dcc.Dropdown(
                                            id="category",
                                            options=[{"label": "All", "value": "__ALL__"}]
                                            + [{"label": c, "value": c} for c in categories],
                                            value="__ALL__",
                                            clearable=False,
                                            style={"marginTop": "6px"},
                                            className="dark-input",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Ship Mode",
                                            style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                        ),
                                        dcc.Dropdown(
                                            id="shipmode",
                                            options=[{"label": "All", "value": "__ALL__"}]
                                            + [{"label": m, "value": m} for m in ship_modes],
                                            value="__ALL__",
                                            clearable=False,
                                            style={"marginTop": "6px"},
                                            className="dark-input",
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "gap": "12px",
                                "marginTop": "10px",
                                "paddingTop": "10px",
                                "borderTop": "1px solid rgba(148,163,184,0.16)",
                            },
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(
                                            "Metric",
                                            style={"color": "#cbd5e1", "fontSize": "12px", "fontWeight": "800"},
                                        ),
                                        dcc.RadioItems(
                                            id="metric",
                                            options=[
                                                {"label": "Sales", "value": "Sales"},
                                                {"label": "Profit", "value": "Profit"},
                                            ],
                                            value="Sales",
                                            inline=True,
                                            style={"marginTop": "6px"},
                                        ),
                                    ]
                                ),
                                html.Div(
                                    "Tip: Click legends to isolate • Hover for details",
                                    style={"color": "#94a3b8", "fontSize": "12px", "fontWeight": "700"},
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "12px", "marginBottom": "12px"},
                    children=[
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "10px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[dcc.Graph(id="trend", config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "10px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[dcc.Graph(id="region-segment", config={"displayModeBar": False})],
                        ),
                    ],
                ),
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"},
                    children=[
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "10px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[dcc.Graph(id="top-subcats", config={"displayModeBar": False})],
                        ),
                        html.Div(
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "border": "1px solid rgba(148,163,184,0.14)",
                                "borderRadius": "16px",
                                "padding": "10px",
                                "boxShadow": "0 10px 24px rgba(0,0,0,0.35)",
                            },
                            children=[dcc.Graph(id="discount-profit", config={"displayModeBar": False})],
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "marginTop": "12px",
                        "textAlign": "center",
                        "color": "#94a3b8",
                        "fontSize": "12px",
                        "fontWeight": "700",
                    },
                    children="Built with Plotly Dash • Superstore Dataset",
                ),
            ],
        )
    ],
)


@app.callback(
    Output("kpi-sales", "children"),
    Output("kpi-profit", "children"),
    Output("kpi-margin", "children"),
    Output("kpi-orders", "children"),
    Output("trend", "figure"),
    Output("region-segment", "figure"),
    Output("top-subcats", "figure"),
    Output("discount-profit", "figure"),
    Output("record-count", "children"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("region", "value"),
    Input("segment", "value"),
    Input("category", "value"),
    Input("shipmode", "value"),
    Input("metric", "value"),
)
def update(start_date, end_date, region, segment, category, shipmode, metric):
    dff = apply_filters(df, start_date, end_date, region, segment, category, shipmode)

    total_sales = float(dff["Sales"].sum())
    total_profit = float(dff["Profit"].sum())
    margin = float(total_profit / total_sales) if total_sales != 0 else 0.0
    orders = int(dff["Order ID"].nunique())

    monthly = (
        dff.assign(Month=dff["Order Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)[["Sales", "Profit"]]
        .sum()
        .sort_values("Month")
    )
    trend_fig = px.line(monthly, x="Month", y=["Sales", "Profit"], markers=True)
    trend_fig.update_layout(title="Monthly Trend (Sales & Profit)", legend_title_text="Metric")

    rs = dff.groupby(["Region", "Segment"], as_index=False)[["Sales", "Profit"]].sum()
    rs_fig = px.bar(rs, x="Region", y=metric, color="Segment", barmode="group")
    rs_fig.update_layout(title=f"{metric} by Region & Segment")

    sub = dff.groupby("Sub-Category", as_index=False)[["Sales", "Profit"]].sum()
    sub["Metric"] = sub[metric]
    sub = sub.sort_values("Metric", ascending=False).head(10)
    sub_fig = px.bar(sub, x="Metric", y="Sub-Category", orientation="h")
    sub_fig.update_layout(title=f"Top 10 Sub-Categories by {metric}", yaxis_title="", xaxis_title=metric)

    dp_fig = px.scatter(
        dff,
        x="Discount",
        y="Profit",
        size="Sales",
        color="Category",
        hover_data=["Sub-Category", "Region", "Segment"],
    )
    dp_fig.update_layout(title="Discount vs Profit (size = Sales)")

    trend_fig = polish_dark(trend_fig)
    rs_fig = polish_dark(rs_fig)
    sub_fig = polish_dark(sub_fig)
    dp_fig = polish_dark(dp_fig)

    rc = f"Rows: {len(dff):,} | Orders: {orders:,}"

    return (
        money(total_sales),
        money(total_profit),
        pct(margin),
        f"{orders:,}",
        trend_fig,
        rs_fig,
        sub_fig,
        dp_fig,
        rc,
    )


if __name__ == "__main__":
    app.run(debug=True)
