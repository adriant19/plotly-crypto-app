from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

from app import app, server
import scraper

app.layout = html.Div([

    html.Div(  # webapp title
        children=[
            html.H4("Crypto Price App", style={"font-family": "Helvetica", "fontSize": 30, "marginBottom": 10}),
            html.Hr(style=dict(marginBottom=30)),
        ],
        style=dict(align="center")
    ),

    html.Div(  # filters
        className="row",
        style=dict(display="flex", align="center"),  # split side by side
        children=[
            dcc.Dropdown(
                id="currency-selected",
                options=[{"label": x, "value": x} for x in ["USD", "BTC", "ETH"]],
                value="USD", clearable=False,
                style={"width": 700}
            ),
            dcc.Dropdown(
                id="timeframe-selected",
                options=[{"label": x.title() if x == "price" else x, "value": x} for x in ["1h%", "24h%", "7d%", "price"]],
                value="1h%", clearable=False,
                style={"width": 700}
            )
        ]
    ),

    html.Div(  # secondary filter
        className="filter-row",
        children=[
            dcc.Slider(
                id="range-slider",
                min=0, max=100, value=50,
                tooltip={"placement": "bottom", "always_visible": True},
            )
        ],
        style=dict(width=1400, marginTop=20)
    ),

    html.Div(  # charts
        className="chart-row",
        style=dict(display="flex"),
        children=[
            dcc.Graph(id="bar-chart", figure={}),
            dcc.Graph(id="table-chart", figure={})
        ]
    )

])


@ app.callback(
    Output("bar-chart", "figure"), Output("table-chart", "figure"),
    Input("currency-selected", "value"), Input("timeframe-selected", "value"), Input("range-slider", "value")
)
def update_chart(currency_selected, timeframe_selected, num_coins):

    df = scraper.load_data(currency_selected).sort_values(
        by=[timeframe_selected],
        ascending=False
    )

    df_filtered = df[["name", "symbol", "price", "1h%", "24h%", "7d%"]][:num_coins].copy()
    df_filtered.index = np.arange(1, len(df_filtered) + 1)

    df_filtered["color"] = np.where(
        df_filtered[timeframe_selected] >= np.where(timeframe_selected == "price", df_filtered[timeframe_selected].mean(), 0),
        "green",
        "red"
    )

    # horizontal bar chart

    fig = go.Figure(
        go.Bar(
            x=df_filtered[timeframe_selected],
            y=df_filtered["symbol"],
            marker_color=df_filtered["color"],
            orientation="h"
        ),
        layout=go.Layout(
            title="Bar Plot of % Price Changes",
            font_family="Helvetica",
            xaxis={"tickformat": ",.0f" if timeframe_selected == "price" else ",.0%"},
            yaxis={"categoryorder": "total ascending"},
            width=500,
            height=600,
            hovermode="y unified"
        )
    )

    # table chart

    table = go.Figure(
        go.Table(
            columnwidth=[150, 400],
            header=dict(
                values=["#"] + [f"<b>{c.upper()}</b>" for c in df_filtered.columns],
                font=dict(size=15), align="left",
                fill_color="paleturquoise", line_color="darkslategray",
                height=40
            ),
            cells=dict(
                values=[df_filtered.index.tolist()] + [df_filtered[k].tolist() for k in df_filtered.columns],
                font=dict(size=13), align="right",
                fill_color="lavender", line_color="darkslategray",
                format=["", "", "", ",.2f", ",.0%", ",.0%", ",.0%"],
                height=25
            )
        ),
        layout=go.Layout(
            title="Table of Crypto Data",
            font_family="Helvetica",
            height=600,
            width=1000
        )
    )

    return fig, table


if __name__ == "__main__":
    app.run_server(debug=True)
