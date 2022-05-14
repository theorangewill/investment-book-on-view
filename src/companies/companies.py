import json
from typing import Dict

def get_companies(file: str, trade_confirmations: Dict) -> Dict:
    """
    This function reads the file of companies
    """
    print(f"[COMPANIES] I am reading the companies from {file}")
    f = open(file)
    companies = json.load(f)
    f.close()
    # Validate companies
    for date in trade_confirmations:
        for tc in trade_confirmations[date]:
            companies_ = [
                operation["symbol"]
                    for operation in tc.operations
            ]
            validate_companies(companies, companies_)
    return companies

def validate_companies(companies: Dict, tc_companies: list
) -> None:
    list_companies = [company["symbol"] for company in companies]
    for company in tc_companies:
        if not company in list_companies:
            raise ValueError(
                f"The company {company} does not exist in "\
                " companies.json. Please, add this company."
            )
