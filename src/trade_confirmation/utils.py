from datetime import datetime
from typing import Dict

def validate_date(date: str) -> str:
    """
    This function validates the date
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except:
        raise ValueError("The date must respect the format %Y-%m-%d")
    return date

def calculate_fees(fees: Dict) -> float:
    """
    This function calculates the fees
    """
    total = 0.0
    for fee in fees:
        total += fees[fee]
    return total

def validate_operations_value(
    operations_value: float,
    operations: Dict
) -> None:
    """
    This function validates the total of operations value with the value
    of each operation and validates the value of each operation with the price
    """
    total = 0.0
    for operation in operations:
        total += operation["value"]

    if operations_value != round(total, 2):
        raise ValueError(
            "The operations value is not matching "\
            f"({operations_value} != {total}). "\
            "Please, verify that you have not forgotten any operation or "\
            "the values are right."
        )

    for operation in operations:
        value = round(operation["price"] * operation["amount"], 2)
        if value != operation["value"]:
            raise ValueError(
                f"The operation value of {operation['symbol']} is not matching"\
                " with the amount and price "
                f"({operation['price']} * {operation['amount']} != "\
                f"{operation['value']}). "\
                "Please, verify that you have not forgotten any operation or "\
                "the values are right."
            )


def validate_settlement_amount(
    settlement_amount: float,
    fees_cost: float,
    operations_value: float,
) -> None:
    """
    This function validates the settlement amount with the total of fees cost
    and operations value
    """
    if settlement_amount != round(fees_cost + operations_value, 2):
        raise ValueError(
            "The settlement amount does not match with the fees cost and "\
            "the operations value. "\
            f"({settlement_amount} != {fees_cost} + {operations_value}). "\
            "Please, verify that you have not "\
            "forgotten any information."
        )