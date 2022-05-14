import json
from typing import Dict

def get_brokers(file: str, trade_confirmations: Dict) -> Dict:
    """
    This function reads the file of brokers
    """
    print(f"[BROKERS] I am reading the brokers from {file}")
    f = open(file)
    brokers = json.load(f)
    f.close()
    # Validate brokers
    for date in trade_confirmations:
        for tc in trade_confirmations[date]:
            validate_broker(brokers, tc.broker)
    return brokers

def validate_broker(brokers: list, broker_tc: str) -> None:
    list_brokers = [broker["id"] for broker in brokers]
    if not broker_tc in list_brokers:
        raise ValueError(
            f"The broker {broker_tc} does not exist in "\
            " brokers file. Please, add this broker."
        )
