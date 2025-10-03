from config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY
import requests
import os
from pathlib import Path
import json
import re
from typing import Dict, Optional, List, Any
import time
import pandas as pd
import yfinance as yf
import requests
import sys
import platform
import socket
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

_session = None 
MODULE_DIR = Path(__file__).resolve().parent
CACHE_PATH = MODULE_DIR / "symbol_cache.json"

JUNK_SYMBOL_PAT = re.compile(r'.*\b(WT|WS|W|U|UNIT|ADR|PRA|PRB|PRC|RIGHTS)\b', re.IGNORECASE)
JUNK_NAME_PAT = re.compile(r'\b(warrant|units?|right|preferred|preference|etf|fund)\b', re.IGNORECASE)

GLOBAL_EXCHANGE_PRIORITY: Dict[str, float] = {
    # US
    "NYSE": 1.0, "NASDAQ": 1.0, "NYSE ARCA": 0.85, "AMEX": 0.9, "NYSE MKT": 0.9,
    "OTC": 0.3, "PINK": 0.2,
    # UK/EU
    "LSE": 1.0, "AIM": 0.8, "XETRA": 1.0, "FWB": 0.95, "FRA": 0.9,
    "Euronext Paris": 1.0, "Euronext Amsterdam": 1.0, "Euronext Brussels": 0.95, "SIX": 0.95,
    # DE regional you mapped
    "SWB": 0.6,
    # AT / BR
    "VIE": 0.7, "B3": 0.8,
    # APAC
    "TSE": 1.0, "HKEX": 1.0, "ASX": 1.0, "SGX": 1.0,
    "NSE": 1.0, "BSE": 0.9, "KRX": 1.0
}

REGION_EXCHANGE_PREFS = {
    None: ["NYSE", "NASDAQ", "LSE", "XETRA", "Euronext Paris", "Euronext Amsterdam", "SIX"],
    "US": ["NYSE", "NASDAQ"],
    "Europe": ["LSE", "XETRA", "Euronext Paris", "Euronext Amsterdam", "Euronext Brussels", "SIX", "FRA", "FWB", "SWB", "VIE"],
    "UK": ["LSE"],
    "DE": ["XETRA", "FRA", "FWB", "SWB"],
    "FR": ["Euronext Paris"],
}

EXCHANGE_ALIASES: Dict[str, str] = {
    # US
    "NASDAQ": "NASDAQ", "NASDAQGS": "NASDAQ", "NASDAQGM": "NASDAQ", "NASDAQCM": "NASDAQ",
    "NYSE": "NYSE",
    "NYSE ARCA": "NYSE ARCA", "NYSEARCA": "NYSE ARCA",
    "NYSE AMERICAN": "AMEX", "AMEX": "AMEX", "NYSE MKT": "AMEX",
    "OTC": "OTC", "OTC MARKETS": "OTC", "OTC PINK": "PINK", "PINK SHEETS": "PINK", "PINK": "PINK",

    # UK/EU
    "LSE": "LSE", "LONDON": "LSE",
    "XETRA": "XETRA", "XETR": "XETRA", "XET": "XETRA",
    "FWB": "FWB", "FRANKFURT": "FRA", "FRA": "FRA",
    "HANOVER": "FWB",   # often grouped with FWB for scoring
    "STUTTGART": "SWB",
    "VIENNA": "VIE",
    "PARIS": "Euronext Paris", "EURONEXT PARIS": "Euronext Paris",
    "AMSTERDAM": "Euronext Amsterdam", "EURONEXT AMSTERDAM": "Euronext Amsterdam",
    "BRUSSELS": "Euronext Brussels", "EURONEXT BRUSSELS": "Euronext Brussels",
    "SIX": "SIX", "SIX SWISS EXCHANGE": "SIX",

    # APAC
    "HKEX": "HKEX", "HKSE": "HKEX",
    "TSE": "TSE", "JPX": "TSE", "TOKYO": "TSE",
    "ASX": "ASX",
    "SGX": "SGX",
    "NSE": "NSE", "NSEI": "NSE",
    "BSE": "BSE",
    "KRX": "KRX", "KSE": "KRX", "KOSPI": "KRX",

    # LATAM
    "SAO PAULO": "B3", "SÃO PAULO": "B3", "BOVESPA": "B3",
}

NON_LISTABLE_KEYWORDS = {
    "government","ministry","department","agency",
    "ishares","etf","index","fund",
    "partners","llp","ltd.","limited","incubator"
}

symbol_cache = {}
try:
    if CACHE_PATH.exists():
        symbol_cache = json.loads(CACHE_PATH.read_text())
except Exception:
    symbol_cache = {}

def _get_session():
    """
    One shared Session with a real UA and sane retries.
    """
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })
        # Retry throttle-ish errors
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=50)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        _session = s
    return _session


def print_system_and_network_info():
    """
    Print local environment clues + public IP + DNS resolution and quick HTTP probes.
    """
    print("\n===== SYSTEM INFO =====")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Hostname: {socket.gethostname()}")
    try:
        print(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
    except Exception as e:
        print(f"Local IP: <err> {e}")

    print("\n===== ENV HINTS =====")
    print(f"GITHUB_ACTIONS: {os.getenv('GITHUB_ACTIONS')}")
    print(f"RUNNER_NAME: {os.getenv('RUNNER_NAME')}")
    print(f"RUNNER_TRACKING_ID: {os.getenv('RUNNER_TRACKING_ID')}")
    print(f"CI: {os.getenv('CI')}")

    print("\n===== DNS LOOKUPS =====")
    for host in [
        "query1.finance.yahoo.com",
        "fc.yahoo.com",
        "api.ipify.org",
        "ifconfig.me",
        "finnhub.io",
    ]:
        try:
            ip = socket.gethostbyname(host)
            print(f"{host} -> {ip}")
        except Exception as e:
            print(f"{host} -> <DNS error> {e}")

    s = _get_session()

    def _safe_get(url, **kwargs):
        try:
            r = s.get(url, timeout=10, **kwargs)
            return r.status_code, (r.text[:200] if r.text else "")
        except Exception as e:
            return None, f"<exc {type(e).__name__}: {e}>"

    print("\n===== PUBLIC IP CHECK =====")
    for url in ["https://api.ipify.org", "https://ifconfig.me/ip"]:
        code, body = _safe_get(url)
        print(f"GET {url} -> {code} | {body.strip()}")

    print("\n===== YAHOO PROBE (search AAPL) =====")
    y_url = "https://query1.finance.yahoo.com/v1/finance/search"
    code, _ = _safe_get(y_url, params={"q": "AAPL", "quotesCount": 1, "newsCount": 0})
    print(f"GET {y_url} -> {code}")

    print("\n===== FINNHUB PROBE (ping-ish) =====")
    f_url = "https://finnhub.io/api/v1/search"
    code, _ = _safe_get(f_url, params={"q": "AAPL", "token": FINNHUB_API_KEY or ""})
    print(f"GET {f_url} -> {code}")
    print("========================\n")


# small tweak: ensure yfinance uses our session explicitly
def get_company_snapshot_yf(symbol: str):
    """
    Build a compact snapshot for a listed company using yfinance.
    Returns keys:
      - symbol
      - market_cap
      - pe
      - enterprise_value
      - ebitda
      - revenue
      - net_income
      - cap_bucket
      - as_of
    """
    s = _get_session()
    yf_ticker = yf.Ticker(symbol, session=s)  # <<< important: use our session

    # market cap
    market_capitalization = safe_get_fast_info(yf_ticker, "market_cap")
    if market_capitalization is None:
        market_capitalization = safe_get_info(yf_ticker, "marketCap")

    # P/E ratio
    price_to_earnings = safe_get_fast_info(yf_ticker, "pe")
    if price_to_earnings is None:
        price_to_earnings = (
            safe_get_info(yf_ticker, "trailingPE") or safe_get_info(yf_ticker, "forwardPE")
        )

    enterprise_value = safe_get_info(yf_ticker, "enterpriseValue")

    # Annual financials (fallback to quarterly if annual missing)
    annual_financials_df = getattr(yf_ticker, "financials", None)
    latest_annual_financials = latest_financial_row(annual_financials_df)

    if not latest_annual_financials:
        quarterly_financials_df = getattr(yf_ticker, "quarterly_financials", None)
        latest_annual_financials = latest_financial_row(quarterly_financials_df)

    # Extract revenue and net income using common alternate labels
    total_revenue_value = None
    for revenue_key in ("Total Revenue", "TotalRevenue", "Revenue"):
        if revenue_key in latest_annual_financials:
            total_revenue_value = latest_annual_financials[revenue_key]
            break

    net_income_value = None
    for net_income_key in ("Net Income", "NetIncome", "Net Income Applicable To Common Shares"):
        if net_income_key in latest_annual_financials:
            net_income_value = latest_annual_financials[net_income_key]
            break

    # EBITDA may be present in info or as 'Ebitda' in financials
    ebitda_value = safe_get_info(yf_ticker, "ebitda")
    if ebitda_value is None and "Ebitda" in latest_annual_financials:
        ebitda_value = latest_annual_financials["Ebitda"]

    company_snapshot: Dict[str, Any] = {
        "symbol": symbol,
        "market_cap": market_capitalization,
        "pe": price_to_earnings,
        "enterprise_value": enterprise_value,
        "ebitda": ebitda_value,
        "revenue": total_revenue_value,
        "net_income": net_income_value,
        "cap_bucket": cap_bucket(market_capitalization),
        "as_of": int(time.time()),
    }
    return company_snapshot


if __name__ == "__main__":
    print_system_and_network_info()

    tests = [
        ("Diamondback Energy", "US"),
        ("Tesco", "Europe"),
        ("ASML", "Europe"),
        ("HSBC Bank Malta", "Europe"),
    ]
    for nm, rg in tests:
        try:
            print(get_company_info(nm, rg), "\n")
        except Exception as e:
            print(nm, rg, "ERR:", e)
