import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_echarts import st_echarts

from streamlit_option_menu import option_menu
from os.path import dirname, realpath


def new_intake_view():
    HOME = dirname(realpath(__file__))
    @st.cache(allow_output_mutation=True)
    def get_portfolio():
        df_ = pd.read_csv(HOME + '/../data/investment-portfolio/portfolio.csv', sep=';')
        for ticker in df_["symbol"]:
            ticker_ = yf.Ticker(ticker + ".SA")
            summary = ticker_.history(period="1d")
            df_.loc[(df_["symbol"] == ticker), "curr_price"] = float(summary.iloc[0]["Close"])
        df_ = df_[["symbol", "amount", "avg_price", "investment", "perc", "curr_price"]]
        df_["avg_price"] = np.round(df_["avg_price"], 2)
        df_["investment"] = np.round(df_["investment"], 2)
        df_["curr_price"] = np.round(df_["curr_price"], 2)
        df_["new_perc"] = 0
        df_["total"] = 0
        df_["intake"] = 0
        return df_



    # Get the portfolio
    df_i = get_portfolio()

    st.title("New intakes")
    st.caption("Preview how your potfolio will change with your new intakes")

    # Set options for the intake table
    gb_i = GridOptionsBuilder.from_dataframe(
        df_i[["symbol", "curr_price", "total"]]
    )
    gb_i.configure_column(
        "intake",
        editable=True,
        singleClickEdit=True,
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=0
    )
    gb_i.configure_column(
        'total',
        cellClass="grid-cell-centered",
        valueFormatter="'R$ ' + x.toLocaleString()",
        valueGetter="Number(data.intake) * Number(data.curr_price)",
        cellRenderer='agAnimateShowChangeCellRenderer',
        editable=True,
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat']
    )
    gb_i.configure_column(
        'curr_price',
        cellClass="grid-cell-centered",
        valueFormatter="'R$ ' + x.toLocaleString()",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        editable=True
    )
    go_i = gb_i.build()

    # Print the table
    ag_i = AgGrid(
        df_i,
        fit_columns_on_grid_load=True,
        theme="blue",
        gridOptions=go_i
    )

    # Get the data from intakes and calculate percentages
    df_p = ag_i['data']
    df_p["total"] = df_p["intake"] * df_p["curr_price"]
    new_total_investment = df_p["total"].sum()
    old_total_investment = df_p["investment"].sum()
    st.write(new_total_investment)

    df_p["new_investment"] = np.round(df_p["total"] + df_p["investment"], 2)
    df_p["new_perc"] = (
        np.round(
            (df_p["new_investment"]) / (new_total_investment + old_total_investment)
            * 100, 2
        )
    )
    df_p["new_avg_price"] = (
        np.round((df_p["new_investment"]) / (df_p["intake"] + df_p["amount"]), 2)
    )
    df_p = df_p.drop(columns=["amount", "curr_price", "intake", "total"])

    df_p = df_p[
        ["symbol", "avg_price", "investment", "perc", "new_avg_price",
        "new_investment", "new_perc"]
    ]

    # Set options for the old portfolio table
    gb_po = GridOptionsBuilder.from_dataframe(
        df_p[["symbol", "avg_price", "investment", "perc"]]
    )
    gb_po.configure_column(
        "avg_price",
        cellClass="grid-cell-centered",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=2,
        valueFormatter="'R$ ' + x.toLocaleString()",
        cellRenderer='agAnimateShowChangeCellRenderer'
    )
    gb_po.configure_column(
        "investment",
        cellClass="grid-cell-centered",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=2,
        valueFormatter="'R$ ' + x.toLocaleString()",
        cellRenderer='agAnimateShowChangeCellRenderer'
    )
    gb_po.configure_column(
        "perc",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=2,
        valueFormatter="x.toLocaleString() + '%'",
        cellRenderer='agAnimateShowChangeCellRenderer'
    )
    go_po = gb_po.build()

    # Set options for the new portfolio table
    gb_pn = GridOptionsBuilder.from_dataframe(
        df_p[["symbol", "new_avg_price", "new_investment", "new_perc"]]
    )
    gb_pn.configure_column(
        "new_avg_price",
        cellClass="grid-cell-centered",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=2,
        valueFormatter="'R$ ' + x.toLocaleString()",
        cellRenderer='agAnimateShowChangeCellRenderer'
    )
    gb_pn.configure_column(
        "new_investment",
        cellClass="grid-cell-centered",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=2,
        valueFormatter="'R$ ' + x.toLocaleString()",
        cellRenderer='agAnimateShowChangeCellRenderer'
    )
    gb_pn.configure_column(
        "new_perc",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        precision=2,
        valueFormatter="x.toLocaleString() + '%'",
        cellRenderer='agAnimateShowChangeCellRenderer'
    )
    go_pn = gb_pn.build()

    # Set options for the pie charts
    pie_chart_options = {
        "legend": {
            "show": False
        },
        "tooltip": {
            "trigger": 'item',
            "formatter": '{b} : R${c} ({d}%)'
        },
        "series": [{
            "name": 'Access From',
            "type": 'pie',
            "radius": ['40%', '70%'],
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": '#fff',
                "borderWidth": 2
            },
            "label": {
                "fontSize": 11
            },
        }]
    }

    # Print the portfolios tables and pie charts
    c1, c2 = st.columns(2)
    with c1:
        st.text("Your current portfolio")
        pie_chart_options["series"][0]["data"] = [{
            "value": v["investment"], "name": v["symbol"]
            }
            for _, v in df_p.iterrows()
        ]
        st_echarts(options=pie_chart_options)

        grid_return1 = AgGrid(
            df_p[["symbol", "avg_price", "investment", "perc"]],
            fit_columns_on_grid_load=True,
            theme="dark",
            gridOptions=go_po
        )

    with c2:
        st.text("Your future portfolio")
        pie_chart_options["series"][0]["radius"] = ['39%', '70%']
        pie_chart_options["series"][0]["data"] = [{
            "value": v["new_investment"], "name": v["symbol"]
            }
            for _, v in df_p.iterrows()
        ]
        st_echarts(options=pie_chart_options)
        re = AgGrid(
            df_p[["symbol", "new_avg_price", "new_investment", "new_perc"]],
            fit_columns_on_grid_load=True,
            theme="dark",
            gridOptions=go_pn
        )


