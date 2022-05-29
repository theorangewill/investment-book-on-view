from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from os.path import getmtime, exists
import pandas as pd
import json

def validate_date(date: str) -> datetime:
    try:
        date = datetime.strptime(date, "%d/%m/%Y")
        date = date.strftime("%Y-%m-%d")
    except:
        print(f"[VALIDATION] The date's format is wrong: {date}")
        date = ""
    return date

def timedelta_day(date: str, num: str) -> str:
    date = datetime.strptime(date, "%Y-%m-%d")
    date = date + timedelta(days=num)
    date = date.strftime("%Y-%m-%d")
    return date

def download_dividends(symbol: str, dir: str) -> pd.DataFrame:
    filename = dir + "dividends-" + symbol + ".csv"
    if exists(filename):
        file_creation = datetime.fromtimestamp(getmtime(filename)).date()
        if file_creation == datetime.today().date():
            return
    req = Request(
        'https://statusinvest.com.br/acoes/' + symbol,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    bs = BeautifulSoup(urlopen(req).read(), 'html.parser')
    section = bs.find_all('div', {"id": "earning-section"})
    input = section[0].findChildren("input", {"id": "results"})
    df = pd.DataFrame({})
    for row in json.loads(input[0]["value"]):
        prev_date = validate_date(row["ed"])
        ex_date = timedelta_day(prev_date, 1)
        payment_day = validate_date(row["pd"])
        value_without_tax = float(row["v"])
        earning_type = row["et"]
        if earning_type == "JCP" or earning_type == "Rend. Tributado":
            value = value_without_tax * (1 - 0.15)
        elif earning_type == "Dividendo" or earning_type == "Amortização":
            value = value_without_tax
        else:
            raise ValueError(
                f"[DIVIDENDS] Earning type not definied {earning_type}"
            )
        df = pd.concat([df, pd.DataFrame({
            "symbol": [symbol],
            "ex_date": [ex_date],
            "prev_date": [prev_date],
            "payment_day": [payment_day],
            "type": [earning_type],
            "value_without_tax": [value_without_tax],
            "value": [value],
        })])
    df.to_csv(filename, sep=";", index=False)


def download_bonus(symbol: str, dir: str) -> pd.DataFrame:
    filename = dir + "bonus-" + symbol + ".csv"
    if exists(filename):
        file_creation = datetime.fromtimestamp(getmtime(filename)).date()
        if file_creation == datetime.today().date():
            return
    df = pd.DataFrame(
        columns=[
            "symbol", "ex-date", "incorporation_date",
            "proportion", "value", "new_ticker"
        ]
    )
    req = Request(
        'https://statusinvest.com.br/acoes/' + symbol,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    bs = BeautifulSoup(urlopen(req).read(), 'html.parser')
    section = bs.find_all('h3', text="BONIFICAÇÃO")
    section = section[0].parent.parent
    section = section.findChildren("div", {"class": "card-body"})[0]
    section = section.findChildren("div")
    if len(section) != 0:
        section = section[0]
        section = section.findChildren(
            "div",
            {
            "class":
            "d-flex justify-between align-items-center flex-wrap flex-md-nowrap"
            }
        )
        for sec in section:
            sec = sec.findChildren("div")
            ex_date = validate_date(
                sec[2].findChildren("strong")[0].text
            )
            prev_date = timedelta_day(ex_date, -1)
            incorporation_date = validate_date(
                sec[3].findChildren("strong")[0].text
            )
            value = float((
                sec[5].findChildren("strong")[0].text
            ).replace("R$ ", "").replace(",", "."))
            proportion = float((
                sec[6].findChildren("strong")[0].text
            ).replace("%", "").replace(",", "."))
            new_ticker = (
                sec[7].findChildren("strong")[0].text
            ).strip()
            df = pd.concat([df, pd.DataFrame({
                "symbol": [symbol],
                "ex_date": [ex_date],
                "prev_date": [prev_date],
                "incorporation_date": [incorporation_date],
                "proportion": [proportion],
                "value": [value],
                "new_ticker": [new_ticker],
            })])
    df.to_csv(filename, sep=";", index=False)
