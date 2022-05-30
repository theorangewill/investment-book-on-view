import json
from typing import Dict
import numpy as np

import pandas as pd
import streamlit as st
from os.path import dirname, realpath
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

HOME = dirname(realpath(__file__))
COMPANIES_FILE = HOME + "/../../data/companies.json"
BROKERS_FILE = HOME + "/../../data/brokers.json"
TC_DIR = HOME + "/../../data/trade-confirmation/"

@st.cache
def get_brokers() -> Dict:
    f = open(BROKERS_FILE)
    brokers = json.load(f)
    f.close()
    brokers = [ b["id"] for b in brokers ]
    return brokers

def can_eval(dic: str) -> bool:
    try:
        eval(dic)
    except Exception as e:
        print(e)
        return False
    else:
        return True

@st.cache
def get_companies() -> Dict:
    f = open(COMPANIES_FILE)
    companies = json.load(f)
    f.close()
    companies = [ c["symbol"] for c in companies ]
    return companies

@st.cache
def get_operations() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": [],
        "amount": [],
        "price": [],
        "value": []
    })



def add_new_trades_view():
    st.title("Add new trades")
    st.caption("Here you can add a new trade confirmation")
    c1, c2 = st.columns(2)
    with c1:
        broker = st.selectbox("Broker", get_brokers())
        date = st.date_input("Date")
    with c2:
        operations_value = st.number_input("Operations Value")
        settlement_amount = st.number_input("Settlement Amount")
    
    fees = st.text_area("Fees", value="{}")
    try:
        fees_dict = eval(fees)
    except:
        fees_dict = {}
        st.exception("Fees must be a .json")

    if 'df_operations' not in st.session_state:
        st.session_state.df_operations = get_operations()
    
    st.write("Operation")
    c1, c2, c3, c4, c5 = st.columns([3,3,3,3,1])
    symbol = c1.selectbox("Symbol", get_companies())
    amount = c2.number_input("Amount", min_value=1)
    price = c3.number_input("Price", min_value=0.01)
    value = c4.number_input("Value", min_value=0.01)
    add = c5.button(label="add")
    if add:
        st.session_state.df_operations = pd.concat([
        st.session_state.df_operations,
            pd.DataFrame({
            "symbol": [symbol],
            "amount": [amount],
            "price": [price],
            "value": [value]
        })]).reset_index(drop=True)
    st.session_state.df_operations["id"] = np.array(
        range(1, len(st.session_state.df_operations) + 1)
    )
    st.session_state.df_operations = st.session_state.df_operations[[
        "id", "symbol", "amount", "price", "value"
    ]]

    gb = GridOptionsBuilder.from_dataframe(
        st.session_state.df_operations
    )
    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True
    )
    gb.configure_column(
        "amount",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        editable=True
    )
    gb.configure_column(
        "price",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        valueFormatter="'R$' + x.toLocaleString()",
        editable=True
    )
    gb.configure_column(
        "value",
        type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
        valueFormatter="'R$' + x.toLocaleString()",
        editable=True
    )
    go = gb.build()
    re = AgGrid(
        st.session_state.df_operations,
        fit_columns_on_grid_load=True,
        gridOptions=go,
        update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED
    )
    c1, _, _, c2 = st.columns(4)
    update = c1.button(label="update operations")
    st.session_state.df_operations = pd.DataFrame(re["data"])
        #st.experimental_rerun()
    delete = c2.button(label="delete selected rows")
    if delete:
        df_selected = pd.DataFrame(re['selected_rows'])
        if not df_selected.empty:
            list_ids = list(df_selected["id"])
            st.session_state.df_operations = st.session_state.df_operations.loc[
                ~(st.session_state.df_operations["id"].isin(list_ids))
            ]
            st.experimental_rerun()

        
    operations = st.session_state.df_operations.to_dict("index")
    operations = [
        dict((k, v) for k, v in operations[op].items() if k != 'id')
            for op in operations
    ]
    print(st.session_state)
    trade_confirmation = {
        "broker": broker,
        "date": date.strftime("%Y-%m-%d"),
        "operations_value": operations_value,
        "settlement_amount": settlement_amount,
        "fees": fees_dict,
        "operations": operations
    }
    st.json(trade_confirmation)

    upload = st.button(label="Upload trade confirmation")
    if upload:
        error = False
        # if operations_value <= 0:
        #     st.error("Operations value must be grater than zero")
        #     error = True
        # if settlement_amount <= 0:
        #     st.error("Settlement amount must be grater than zero")
        #     error = True
        # if not can_eval(fees):
        #     st.error("Fees must be a valid .json")
        #     error = True
        # if len(operations) == 0:
        #     st.error("At least one operation, please")
        #     error = True
        if not error:
            filename = (
                TC_DIR 
                    + f"trade-confirmation-{broker}-{date.strftime('%Y%m%d')}"
                    + ".json"
            )
            with open(filename, 'w') as fp:
                json.dump(
                    trade_confirmation,
                    fp
                )
            st.success(f"Your trade confirmation has been saved in {filename}")
