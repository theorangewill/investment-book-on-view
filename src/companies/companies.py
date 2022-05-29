import json
from typing import Dict
from utils.dividends import download_bonus, download_dividends

def get_companies(
        file: str,
        trade_confirmations: Dict,
        dir_earnings: str,
    ) -> Dict:
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
    # Download earnings and actions
    for c in companies:
        print(f"[COMPANIES] I am getting earnings from {c['symbol']}")
        download_dividends(c["symbol"], dir_earnings)
        download_bonus(c["symbol"], dir_earnings)
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
