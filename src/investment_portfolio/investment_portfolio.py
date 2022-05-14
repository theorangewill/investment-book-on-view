from dateutil.relativedelta import relativedelta
from typing import Dict
from utils.utils import save_to_file
from os import listdir
from os.path import isfile, join
import pandas as pd

class InvestmentPortfolio:
    def __init__(self, dir: str, trade_confirmations: Dict) -> None:
        self.dir = dir
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
                    pass

        self.create_portfolio()
        self.create_anual_amounts()

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
        file_path = self.dir + "/portfolio-" + operation["symbol"] + ".csv"
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
        portfolio_files = [
            join(self.dir, file)
                for file in listdir(self.dir)
                    if isfile(join(self.dir, file))
                        and file.startswith("portfolio-")
                        and file.endswith(".csv")
                        and not file.endswith("-yearly.csv")
        ]
        return portfolio_files

    def create_portfolio(self) -> None:
        """
        This function creates the consolidated portfolio of all tickers
        """
        file = self.dir + "/portfolio.csv"
        portfolio_files = self.get_portfolio_files()
        portfolio = pd.DataFrame({})
        for file in portfolio_files:
            df = pd.read_csv(file, sep=";")
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
        portfolio_files = self.get_portfolio_files()
        for file in portfolio_files:
            print(file)
            df = pd.read_csv(file, sep=";")
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
            df.to_csv(file.replace(".csv", "-yearly.csv"), sep=";", index=False)
