"""
Risk Score Calculator — Join39 App
Vercel Serverless Function (Python)

Takes a stock ticker and portfolio weight, returns a mock risk score
with breakdown across volatility, concentration, and sector risk.
"""

import json
import hashlib
from http.server import BaseHTTPRequestHandler

# ── Mock risk data (deterministic based on ticker hash) ─────
SECTOR_MAP = {
    "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
    "NVDA": "Semiconductors", "AMD": "Semiconductors", "INTC": "Semiconductors",
    "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
    "JPM": "Financials", "GS": "Financials", "BAC": "Financials",
    "JNJ": "Healthcare", "PFE": "Healthcare", "UNH": "Healthcare",
    "XOM": "Energy", "CVX": "Energy",
    "META": "Technology", "NFLX": "Communication Services",
}

SECTOR_RISK = {
    "Technology": 0.72, "Semiconductors": 0.81, "Consumer Discretionary": 0.68,
    "Financials": 0.55, "Healthcare": 0.42, "Energy": 0.63,
    "Communication Services": 0.65,
}


def compute_risk(ticker: str, weight: float) -> dict:
    """Generate a deterministic but realistic-looking risk score."""
    ticker = ticker.upper().strip()

    # Use hash for deterministic pseudo-randomness
    h = int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16)
    base_volatility = 0.15 + (h % 100) / 200  # 0.15 – 0.65

    sector = SECTOR_MAP.get(ticker, "Unknown")
    sector_risk = SECTOR_RISK.get(sector, 0.50 + (h % 30) / 100)

    # Concentration risk increases nonlinearly with weight
    concentration_risk = min(1.0, (weight / 100) ** 0.7 * 1.2)

    # Composite score (weighted average, 0–100)
    composite = (
        base_volatility * 0.40 +
        sector_risk * 0.30 +
        concentration_risk * 0.30
    ) * 100

    composite = round(min(99, max(1, composite)), 1)

    # Risk label
    if composite < 30:
        label = "Low"
    elif composite < 55:
        label = "Moderate"
    elif composite < 75:
        label = "Elevated"
    else:
        label = "High"

    return {
        "ticker": ticker,
        "portfolio_weight_pct": weight,
        "sector": sector,
        "risk_score": composite,
        "risk_label": label,
        "breakdown": {
            "volatility_component": round(base_volatility * 100, 1),
            "sector_risk_component": round(sector_risk * 100, 1),
            "concentration_risk_component": round(concentration_risk * 100, 1),
        },
        "interpretation": (
            f"{ticker} in the {sector} sector carries {label.lower()} risk "
            f"at a {weight}% portfolio weight. "
            f"Composite score: {composite}/100."
        ),
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with query parameters."""
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        ticker = params.get("ticker", [None])[0]
        weight_str = params.get("weight", ["10"])[0]

        if not ticker:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Missing required parameter: ticker"
            }).encode())
            return

        try:
            weight = float(weight_str)
            weight = max(0.1, min(100, weight))
        except ValueError:
            weight = 10.0

        result = compute_risk(ticker, weight)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_POST(self):
        """Handle POST requests with JSON body."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        ticker = data.get("ticker")
        weight = data.get("weight", 10)

        if not ticker:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Missing required parameter: ticker"
            }).encode())
            return

        try:
            weight = float(weight)
            weight = max(0.1, min(100, weight))
        except (ValueError, TypeError):
            weight = 10.0

        result = compute_risk(ticker, weight)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
