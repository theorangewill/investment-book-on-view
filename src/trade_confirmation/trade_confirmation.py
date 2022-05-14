import json
from os.path import basename
from typing import Dict
from trade_confirmation.utils import (
    validate_date,
    calculate_fees,
    validate_operations_value,
    validate_settlement_amount
)

class TradeConfirmation:
    def __init__(self, file_path: str) -> None:
        self.name = basename(file_path)
        # Read json
        print(f"[TRADE CONFIRMATION] I am analyzing the paper {file_path}")
        f = open(file_path)
        paper = json.load(f)
        f.close()
        # Read broker
        self.broker = paper['broker']
        # Read date
        self.date = validate_date(paper['date'])
        # Read fees
        self.fees = paper['fees']
        fees_cost = calculate_fees(self.fees)
        # Read operations
        self.operations = paper['operations']
        self.operations_value = paper['operations_value']
        validate_operations_value(
            self.operations_value,
            self.operations
        )
        # Check if the values match
        self.settlement_amount = paper['settlement_amount']
        validate_settlement_amount(
            self.settlement_amount,
            fees_cost,
            self.operations_value
        )
        # Calculate the price with the fees
        self.calculate_price_with_fees(self.operations_value, fees_cost)

    def calculate_price_with_fees(
        self,
        operations_value: float,
        fees_cost: float
    ) -> Dict:
        count = 1
        for operation in self.operations:
            percentage = operation["value"] / operations_value
            fees_cost_ = fees_cost * percentage
            operation["cost_of_fees"] = fees_cost_
            operation["value_without_fees"] = operation["value"]
            operation["value"] = operation["value"] + fees_cost_
            operation["price_without_fees"] = operation["price"]
            operation["price"] = (
                operation["price"] + fees_cost_ / operation["amount"]
            )
            operation["counter"] = str(count)
            count += 1
