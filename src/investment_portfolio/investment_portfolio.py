from typing import Dict
from utils.utils import save_to_file
import pandas as pd

class InvestmentPortfolio:
    def __init__(self, dir: str, trade_confirmations: Dict) -> None:
        self.dir = dir
        for date in sorted(trade_confirmations.keys()):
            for tc in trade_confirmations[date]:
                #self.add_fees(tc.name, tc.date, tc.broker, tc.fees)
                #self.add_spent_values(
                #    tc.name, tc.date, tc.operations_value, tc.settlement_amount
                #)
                for operation in tc.operations:
                    self.add_operation(
                        tc.name, tc.date, tc.broker, operation
                    )
                    pass
    
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