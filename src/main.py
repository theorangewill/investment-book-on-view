from investment_portfolio.investment_portfolio import InvestmentPortfolio
from companies.companies import get_companies
from brokers.brokers import get_brokers
from utils.utils import read_trade_confirmation
from os.path import dirname, realpath

HOME = dirname(realpath(__file__))
COMPANIES_FILE = HOME + "/../data/companies.json"
BROKERS_FILE = HOME + "/../data/brokers.json"
TC_DIR = HOME + "/../data/trade-confirmation/"
IP_DIR = HOME + "/../data/investment-portfolio/"

if __name__ == "__main__":
    trade_confirmations = read_trade_confirmation(TC_DIR)
    companies = get_companies(COMPANIES_FILE, trade_confirmations)
    brokers = get_brokers(BROKERS_FILE, trade_confirmations)
    
    investment_portfolio = InvestmentPortfolio(IP_DIR, trade_confirmations)

