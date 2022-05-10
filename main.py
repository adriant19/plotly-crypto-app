from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

from app import app, server
import scraper

# ------------------------------------------------------------------------------
# setup layout

app.layout = html.Div([

    html.Div(  # webapp title
        style={"marginLeft": 20, "marginBottom": 30},
        children=[
            html.H4("CRYPTO PRICE APP", style={"font-family": "Helvetica", "fontSize": 30, "marginBottom": 10}),
            html.Hr(),
        ]
    ),

    html.Div(  # filters
        style={
            "marginLeft": 20,
            "width": 1400,
            "display": "grid",
            "grid-template-columns": "20% 20% 40%",
        },
        children=[
            html.Label("Price currency", style={"font-weight": "bold", "marginRight": 10}),
            html.Label("Timeframe sorting", style={"font-weight": "bold", "marginRight": 10}),
            html.Label("Number of Coins", style={"font-weight": "bold"}),
        ]
    ),

    html.Div(  # secondary filter
        style={
            "marginLeft": 20,
            "marginTop": 10,
            "width": 1400,
            "display": "grid",
            "grid-template-columns": "20% 20% 40%",
        },
        children=[
            dcc.Dropdown(
                id="currency-selected",
                style={"marginRight": 20},
                options=[{"label": x, "value": x} for x in ["USD", "BTC", "ETH"]],
                value="USD",
                clearable=False,
            ),
            dcc.Dropdown(
                id="timeframe-selected",
                style={"marginRight": 20},
                options=[{"label": x.title() if x == "price" else x, "value": x} for x in ["1h%", "24h%", "7d%", "price"]],
                value="1h%",
                clearable=False
            ),
            dcc.Slider(
                id="range-slider",
                min=0, max=100, value=50,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ]
    ),

    html.Div(  # charts
        style={
            "marginLeft": 20,
            "width": 1400,
            "display": "flex"
        },
        children=[
            dcc.Graph(id="bar-chart", figure={}),
            dcc.Graph(id="table-chart", figure={})
        ]
    ),

    html.Div(  # webapp title
        style={"marginLeft": 20, "align": "center"},
        children=[
            html.Hr(),
            html.Footer(
                "* by Adrian T.",
                style={
                    "marginLeft": 20,
                    "fontSize": 13,
                    "color": "gray",
                    "font-style": "italic"
                }
            )
        ]
    )

])


# ------------------------------------------------------------------------------
# callback function for interactive

@app.callback(
    Output("bar-chart", "figure"), Output("table-chart", "figure"),
    Input("currency-selected", "value"), Input("timeframe-selected", "value"), Input("range-slider", "value")
)
def update_chart(currency_selected, timeframe_selected, num_coins):

    df = scraper.load_data(currency_selected)[
        ["name", "symbol", "price", "1h%", "24h%", "7d%"]
    ].sort_values(
        by=[timeframe_selected],
        ascending=False
    )[:num_coins]

    df.index = np.arange(1, len(df) + 1)

    df["color"] = np.where(  # for price, color against avg
        df[timeframe_selected] >= np.where(timeframe_selected == "price", df[timeframe_selected].mean(), 0),
        "green",
        "red"
    )

    # horizontal bar chart
    # issue: points were reversed instead of using yaxis={"categoryorder": "total ascending"}
    # this is because the sorting somehow includes unfiltered yticks when using 24h% or 7d%

    fig = go.Figure(
        go.Bar(
            x=df[timeframe_selected][::-1],
            y=df["symbol"][::-1],
            marker_color=df["color"][::-1],
            customdata=df[["price", "1h%", "24h%", "7d%"]][::-1],
            hovertemplate="<br>".join([
                "<extra><b>price</b>: %{customdata[0]:,.2f}",
                "<b>1h%</b>: %{customdata[0]:,.0%}",
                "<b>24h%</b>: %{customdata[1]:,.0%}",
                "<b>7d%</b>: %{customdata[2]:,.0%}</extra>",
            ]),
            orientation="h"
        ),
        layout=go.Layout(
            title="Bar Plot of % Price Changes",
            font_family="Helvetica",
            xaxis={"tickformat": ",.0f" if timeframe_selected == "price" else ",.0%"},
            width=500, height=600,
            hovermode="y unified"
        )
    )

    # table chart

    table = go.Figure(
        go.Table(
            columnwidth=[150, 400],
            header=dict(
                values=["#"] + [f"<b>{c.upper()}</b>" for c in df.columns[:-1]],
                font=dict(size=15), align="left",
                fill_color="paleturquoise", line_color="darkslategray",
                height=40
            ),
            cells=dict(
                values=[df.index.tolist()] + [df[k].tolist() for k in df.columns[:-1]],
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
