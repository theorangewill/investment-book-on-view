import streamlit as st
from streamlit_option_menu import option_menu
from my_story.index import my_story_view
from new_intake.index import new_intake_view
from add_new_trades.index import add_new_trades_view
from my_profits.index import my_profits_view

st.set_page_config(page_title="My investments")

with st.sidebar:
    menu_option = option_menu(
        menu_title=None,
        options=["My story", "New intake", "Add new trades", "My profits"],
        icons=['book', 'cart', 'clipboard-check', 'book', 'cash-coin'],
        default_index=0,
        styles={
            "icon": {"color": "#1ba5cf", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "16px",
                "margin":"0px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#91d2e6"},
        }
    )


if menu_option == "My story":
    my_story_view()
elif menu_option == "New intake":
    new_intake_view()
elif menu_option == "Add new trades":
    add_new_trades_view()
elif menu_option == "My profits":
    my_profits_view()
