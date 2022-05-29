from bisect import bisect, bisect_left, bisect_right
from datetime import timedelta
import re
from dateutil.relativedelta import relativedelta
from typing import Dict

import numpy as np
from utils.utils import save_to_file, create_folder
from utils.yf import get_dividends
from os import listdir
from os.path import isfile, join, basename
import pandas as pd

class InvestmentPortfolio:
    def __init__(self, dir: str, trade_confirmations: Dict) -> None:
        self.create_folders(dir)
        for date in sorted(trade_confirmations.keys()):
            for tc in trade_confirmations[date]:
                self.add_fees(tc.name, tc.date, tc.broker, tc.fees)
                self.add_spent_values(
                    tc.name, tc.date, tc.operations_value, tc.settlement_amount
                )
                for operation in tc.operations:
                    self.add_operation(
                        tc.name, tc.date, tc.broker, operation
                    )

        self.create_portfolio()
        self.create_anual_amounts()
        self.create_story()
        self.create_dividends_story()

    def create_folders(self, dir: str) -> None:
        self.dir = create_folder(dir)
        self.dir_portfolios = create_folder(dir + "portfolios/")
        self.dir_anual_amounts = create_folder(dir + "anual_amounts/")
        self.dir_stories = create_folder(dir + "stories/")
        self.dir_earnings = create_folder(dir + "../earnings-history/")

    def add_fees(
        self, tc_name: str, date: str, broker: str, fees: Dict
    ) -> None:
        """
        This function records the fees
        """
        file_path = self.dir + "/fees.csv"

        df = pd.DataFrame.from_dict(fees, orient="index").reset_index()
        df.columns = ["fee", "value"]
        df["tc_name"] = tc_name
        df["date"] = date
        df["broker"] = broker
        df = df[["date", "broker", "fee", "value", "tc_name"]]
        save_to_file("fees", df, file_path)

    def add_spent_values(
        self,
        tc_name: str,
        date: str,
        operations_value: float,
        settlement_amount: float
    ) -> None:
        """
        This function records the fees
        """
        file_path = self.dir + "/spent_values.csv"
        df = pd.DataFrame(
            {
                "tc_name": [tc_name],
                "date": [date],
                "operations_value": [operations_value],
                "settlement_amount": [settlement_amount]
            }
        )
        df = df[["date", "operations_value", "settlement_amount", "tc_name"]]
        save_to_file("spent_values", df, file_path)
    
    def add_operation(
        self, tc_name: str, date: str, broker: str, operation: Dict
    ) -> None:
        symbol = operation["symbol"]
        file_path = (
            self.dir_portfolios + "/portfolio-" + operation["symbol"] + ".csv"
        )
        df = pd.DataFrame(
            {
                "tc_name": [tc_name + "-" + operation["counter"]],
                "date": [date],
                "symbol": [symbol],
                "amount": [operation["amount"]],
                "price": [operation["price"]],
                "value": [operation["value"]],
                "cost_of_fees": [operation["cost_of_fees"]],
                "value_without_fees": [operation["value_without_fees"]],
                "price_without_fees": [operation["price_without_fees"]]
            }
        )
        df = df[[
            "date", "symbol", "amount", "price", "value", "cost_of_fees",
            "value_without_fees", "price_without_fees", "tc_name"
        ]]
        save_to_file("operation", df, file_path)
        
    def get_portfolio_files(self) -> list:
        portfolio_files = {
            re.split("-|\.", file)[1]: join(self.dir_portfolios, file)
                for file in listdir(self.dir_portfolios)
        }
        return portfolio_files

    def get_portfolio_story_files(self) -> list:
        story_files = {
            re.split("-|\.", file)[1]: join(self.dir_stories, file)
                for file in listdir(self.dir_stories) if "portfolio-" in file
        }
        return story_files

    def get_dividend_files(self) -> list:
        dividend_files = {
            re.split("-|\.", file)[1]: join(self.dir_earnings, file)
                for file in listdir(self.dir_earnings) if "dividends-" in file
        }
        return dividend_files
    
    def create_portfolio(self) -> None:
        """
        This function creates the consolidated portfolio of all tickers
        """
        file = self.dir + "consolidated_portfolio.csv"
        portfolio = pd.DataFrame({})
        portfolio_file = self.get_portfolio_files()
        for c in portfolio_file:
            df = pd.read_csv(portfolio_file[c], sep=";")
            df = df[["symbol", "amount", "value"]]
            df = df.rename(columns={"value": "investment"})
            df = df.groupby(
                    ["symbol"], as_index=False
                ).agg({"amount": "sum", "investment": "sum"})
            df["avg_price"] = df["investment"] / df["amount"]
            df = df[["symbol", "amount", "avg_price", "investment"]]
            portfolio = pd.concat([portfolio, df])
        amount_invested = sum(portfolio["investment"])
        portfolio["perc"] = round(
            portfolio["investment"] / amount_invested * 100, 2
        )
        portfolio = portfolio.sort_values(
            ["perc", "investment"], ascending=False
        )
        portfolio.to_csv(file, sep=";", index=False)

    def create_anual_amounts(self):
        portfolio_file = self.get_portfolio_files()
        for c in portfolio_file:
            df = pd.read_csv(portfolio_file[c], sep=";")
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
            df["year"] = df["date"].apply(lambda x: x.year)
            df = df[["year", "symbol", "amount", "value"]]
            df = df.rename(columns={"value": "investment"})
            df = df.groupby(
                    ["year", "symbol"], as_index=False
                ).agg({"amount": "sum", "investment": "sum"})
            df = df[["year", "symbol", "amount", "investment"]]
            df = pd.concat(
                [df, pd.DataFrame({
                        "year": [min(df["year"]) - 1],
                        "symbol": [list(df["symbol"].unique())[0]],
                        "amount": [0],
                        "investment": [0.0]
                    })
                ]
            )
            df = df.sort_values(["year"])
            df["accumulated"] = df['investment'].cumsum()
            df.to_csv(
                self.dir_anual_amounts + basename(portfolio_file[c]),
                sep=";",
                index=False
            )

    def create_story(self):
        portfolio_file = self.get_portfolio_files()
        for c in portfolio_file:
            df = pd.read_csv(portfolio_file[c], sep=";")
            df = df[["date", "symbol", "amount", "price", "value"]]
            # Groupby the trades made in the same day
            df = df.groupby(["date", "symbol"], as_index=False).agg({
                "amount": "sum",
                "value": "sum"
            })
            # Calculate the amount and value in each day
            df = df.sort_values(["date"])
            df["amount"] = df['amount'].cumsum()
            df["value"] = df['value'].cumsum()
            # Calculate the avg price in each day
            df["price"] = df["value"] / df["amount"]
            df.to_csv(
                self.dir_stories + basename(portfolio_file[c]),
                sep=";",
                index=False
            )

    def create_dividends_story(self):
        portfolio_story_files = self.get_portfolio_story_files()
        dividend_files = self.get_dividend_files()
        for c in portfolio_story_files:
            df_story = pd.read_csv(portfolio_story_files[c], sep=";")
            min_date = min(df_story["date"])
            df_dividend = pd.read_csv(dividend_files[c], sep=";")
            df_dividend = df_dividend.loc[
                (df_dividend["prev_date"] >= min_date)
            ]
            df_dividend = df_dividend.sort_values(["prev_date"])
            intake_dates = sorted(list(df_story["date"]))
            df_dividend["date"] = df_dividend["prev_date"].apply(
                lambda x: intake_dates[bisect_left(intake_dates, x) - 1]
            )
            df_dividend_story = df_dividend.merge(
                df_story, on=["date", "symbol"], how="left"
            )
            df_dividend_story = df_dividend_story[
                ["symbol", "prev_date", "payment_day", "type",
                "value_x", "amount", "value_y", "price"]
            ]
            df_dividend_story = df_dividend_story.rename(
                columns={
                    "value_x": "dividend_per_stock",
                    "value_y": "investment"
                }
            )
            df_dividend_story["dividend_received"] = (
                df_dividend_story["dividend_per_stock"] 
                * df_dividend_story["amount"]
            )
            df_dividend_story = df_dividend_story.sort_values(
                ["payment_day", "prev_date"], ascending=False
            )
            df_dividend_story.to_csv(
                self.dir_stories + basename(dividend_files[c]),
                sep=";",
                index=False
            )