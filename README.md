# Risk Score Calculator — Join39 Agent Store App

A serverless API that calculates mock portfolio risk scores for stock tickers. Built as an app for the [Join39 Agent Store](https://join39.org), where AI agents can discover and call it during conversations to evaluate stock risk.

---

## What It Does

Give it a stock ticker (like `NVDA`) and an optional portfolio weight (like `15%`), and it returns:

- A **composite risk score** from 0 to 100
- A **risk label**: Low / Moderate / Elevated / High
- A **breakdown** across three risk components:
  - **Volatility** — how much the stock price tends to swing (derived from a hash of the ticker)
  - **Sector risk** — inherent risk of the stock's sector (e.g., Semiconductors = 0.81, Healthcare = 0.42)
  - **Concentration risk** — how dangerous it is to hold too much of one stock (increases nonlinearly with weight)
- A **human-readable interpretation** string

> **Note:** This is a mock/demo API. Risk scores are deterministic (same input = same output) but not based on real market data. It's designed to demonstrate how agent-callable tools work on Join39.

---

## Live API

**Base URL:** `https://join39-risk-score.vercel.app`

### GET /api/risk

| Parameter | Type   | Required | Default | Description                        |
|-----------|--------|----------|---------|------------------------------------|
| `ticker`  | string | Yes      | —       | Stock ticker symbol (e.g., NVDA)   |
| `weight`  | number | No       | 10      | Portfolio weight as a % (0.1–100)  |

### Example Request

```
GET https://join39-risk-score.vercel.app/api/risk?ticker=NVDA&weight=15
```

### Example Response

```json
{
  "ticker": "NVDA",
  "portfolio_weight_pct": 15.0,
  "sector": "Semiconductors",
  "risk_score": 58.8,
  "risk_label": "Elevated",
  "breakdown": {
    "volatility_component": 62.5,
    "sector_risk_component": 81.0,
    "concentration_risk_component": 31.8
  },
  "interpretation": "NVDA in the Semiconductors sector carries elevated risk at a 15.0% portfolio weight. Composite score: 58.8/100."
}
```

### POST /api/risk

Also supports POST with a JSON body:

```bash
curl -X POST https://join39-risk-score.vercel.app/api/risk \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TSLA", "weight": 25}'
```

### Error Response (400)

```json
{
  "error": "Missing required parameter: ticker"
}
```

---

## Project Structure

```
join39-risk-score/
├── api/
│   └── risk.py          # Serverless function (the entire app logic)
├── vercel.json          # Vercel routing and build config
├── pyproject.toml       # Python project metadata (required by Vercel)
├── requirements.txt     # Dependencies (none — pure Python stdlib)
└── README.md
```

### File Breakdown

- **`api/risk.py`** — The serverless function. Contains:
  - `SECTOR_MAP` — maps 18 well-known tickers to their sectors
  - `SECTOR_RISK` — assigns a base risk multiplier (0.0–1.0) to each sector
  - `compute_risk()` — the core algorithm that produces a deterministic risk score
  - `handler` class — a Vercel-compatible HTTP handler that processes GET and POST requests

- **`vercel.json`** — Tells Vercel to build `api/risk.py` using the `@vercel/python` runtime and route `/api/risk` requests to it

- **`pyproject.toml`** — Required by Vercel's Python builder (uses `uv` under the hood). Declares Python >=3.9 and zero dependencies

- **`requirements.txt`** — Empty. The app uses only Python standard library modules (`json`, `hashlib`, `http.server`, `urllib.parse`)

---

## How the Risk Algorithm Works

### Step 1: Deterministic Volatility

```python
h = int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16)
base_volatility = 0.15 + (h % 100) / 200  # Range: 0.15 to 0.65
```

The ticker string is MD5-hashed to produce a deterministic number. This gives every ticker a unique but repeatable "volatility" between 0.15 and 0.65. The same ticker always produces the same value.

### Step 2: Sector Risk Lookup

```python
sector = SECTOR_MAP.get(ticker, "Unknown")
sector_risk = SECTOR_RISK.get(sector, 0.50 + (h % 30) / 100)
```

Known tickers are mapped to sectors with predefined risk levels. Unknown tickers get a fallback sector risk derived from their hash.

| Sector                  | Risk Factor |
|-------------------------|-------------|
| Healthcare              | 0.42        |
| Financials              | 0.55        |
| Energy                  | 0.63        |
| Communication Services  | 0.65        |
| Consumer Discretionary  | 0.68        |
| Technology              | 0.72        |
| Semiconductors          | 0.81        |

### Step 3: Concentration Risk

```python
concentration_risk = min(1.0, (weight / 100) ** 0.7 * 1.2)
```

This models the idea that putting too many eggs in one basket is risky. The `** 0.7` exponent means risk grows quickly at first (going from 5% to 20% weight is a big jump) but flattens out near 100%. The result is capped at 1.0.

### Step 4: Composite Score

```python
composite = (
    base_volatility * 0.40 +
    sector_risk * 0.30 +
    concentration_risk * 0.30
) * 100
```

The three components are combined as a weighted average:
- 40% volatility
- 30% sector risk
- 30% concentration risk

The result is scaled to 0–100 and clamped between 1 and 99.

### Step 5: Risk Label

| Score Range | Label     |
|-------------|-----------|
| 0–29        | Low       |
| 30–54       | Moderate  |
| 55–74       | Elevated  |
| 75–99       | High      |

---

## How to Test It Yourself

### 1. Browser

Just open these URLs in your browser:

- [NVDA at 15% weight](https://join39-risk-score.vercel.app/api/risk?ticker=NVDA&weight=15)
- [AAPL at default 10%](https://join39-risk-score.vercel.app/api/risk?ticker=AAPL)
- [TSLA at 50% weight](https://join39-risk-score.vercel.app/api/risk?ticker=TSLA&weight=50)
- [A made-up ticker](https://join39-risk-score.vercel.app/api/risk?ticker=FAKE&weight=5)
- [Missing ticker (error)](https://join39-risk-score.vercel.app/api/risk)

### 2. curl (Terminal)

```bash
# Basic GET request
curl "https://join39-risk-score.vercel.app/api/risk?ticker=NVDA&weight=15"

# Pretty-print the JSON
curl -s "https://join39-risk-score.vercel.app/api/risk?ticker=NVDA&weight=15" | python3 -m json.tool

# POST request with JSON body
curl -X POST "https://join39-risk-score.vercel.app/api/risk" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "JPM", "weight": 20}'

# Test error handling (no ticker)
curl "https://join39-risk-score.vercel.app/api/risk"

# Test with invalid weight (falls back to 10.0)
curl "https://join39-risk-score.vercel.app/api/risk?ticker=AAPL&weight=abc"
```

### 3. Python

```python
import requests

resp = requests.get("https://join39-risk-score.vercel.app/api/risk", params={
    "ticker": "NVDA",
    "weight": 15
})
data = resp.json()

print(f"Risk Score: {data['risk_score']}/100 ({data['risk_label']})")
print(f"Sector: {data['sector']}")
print(f"Breakdown:")
for k, v in data['breakdown'].items():
    print(f"  {k}: {v}")
```

### 4. Things to Verify

- **Determinism**: Call the same ticker+weight combo multiple times — you should always get the exact same score
- **Weight sensitivity**: Try NVDA at weight=5, 15, 50, 90 — the concentration risk component should increase
- **Unknown tickers**: Try `ticker=ZZZZ` — it should return sector "Unknown" with a hash-derived risk
- **Error handling**: Omit the ticker parameter — you should get a 400 error with a clear message
- **Weight clamping**: Try weight=0 (gets clamped to 0.1) or weight=999 (gets clamped to 100)

---

## How an AI Agent Interacts With This App

### The Join39 Agent Store

Join39 is a platform where AI agents can discover and use tools (apps) during conversations. When you submit an app to the Agent Store, you provide:

1. **A function definition** — tells the AI *when* and *how* to call your app
2. **An API endpoint** — the URL the agent hits
3. **A response mapping** — which part of the JSON to show the user

### The Flow

```
User: "How risky is NVDA if I put 15% of my portfolio in it?"
  │
  ▼
AI Agent (reads function definitions of installed apps)
  │
  ▼
Agent decides: "This matches risk-score-calculator"
  │
  ▼
Agent extracts parameters: ticker="NVDA", weight=15
  │
  ▼
Agent calls: GET https://join39-risk-score.vercel.app/api/risk?ticker=NVDA&weight=15
  │
  ▼
API returns JSON with risk_score=58.8, risk_label="Elevated", etc.
  │
  ▼
Agent reads the "interpretation" field (via result path mapping):
  "NVDA in the Semiconductors sector carries elevated risk at a 15.0% portfolio weight.
   Composite score: 58.8/100."
  │
  ▼
Agent formulates a natural language response to the user
```

### The Function Definition (What the Agent Sees)

This is what we submitted to Join39. The AI reads this to decide when to call the app:

```json
{
  "name": "risk-score-calculator",
  "description": "Calculate the portfolio risk score for a stock. Returns a composite risk score from 0 (lowest risk) to 100 (highest risk) with breakdown into volatility, sector risk, and concentration risk components. Call this when the user asks about the risk of a stock, how risky a position is, or wants to evaluate portfolio risk.",
  "parameters": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol (e.g., NVDA, AAPL, TSLA, JPM)"
      },
      "weight": {
        "type": "number",
        "description": "Portfolio weight as a percentage (e.g., 10 for 10%). Defaults to 10 if not specified."
      }
    },
    "required": ["ticker"]
  }
}
```

The key parts:
- **`description`** — The AI reads this to decide if this tool is relevant to the user's question. It includes trigger phrases like "risk of a stock" and "evaluate portfolio risk"
- **`parameters`** — Tells the AI exactly what arguments to extract from the user's message and what format they should be in
- **`required`** — Only `ticker` is required; `weight` is optional and defaults to 10

### Result Path Mapping

We set `resultPath: "interpretation"` — this tells Join39 to extract just the `interpretation` string from the full JSON response and pass it to the agent. This gives the agent a clean, human-readable summary instead of raw data.

---

## How It Was Built and Deployed

### Architecture Decision

This app uses **Vercel Serverless Functions** — meaning there's no server running 24/7. Vercel spins up a Python process only when a request comes in, runs the function, returns the response, and shuts down. This is:
- **Free** on Vercel's hobby plan
- **Zero maintenance** — no servers to manage
- **Auto-scaling** — handles traffic spikes automatically

### The Build Process

1. **Wrote `api/risk.py`** — A single Python file using only stdlib modules. Vercel's Python runtime expects a `handler` class that extends `BaseHTTPRequestHandler` with `do_GET` / `do_POST` methods.

2. **Configured `vercel.json`** — Maps the URL path `/api/risk` to the Python file. Uses `@vercel/python` as the build runtime.

3. **Created `pyproject.toml`** — Vercel's Python builder uses `uv` (a fast Python package manager) which requires this file, even if you have zero dependencies.

4. **Pushed to GitHub** — Created a public repo at `github.com/marcnasrisme/join39-risk-score`.

5. **Connected to Vercel** — Imported the GitHub repo on Vercel. Every push to `main` triggers an automatic redeploy.

6. **Submitted to Join39** — Filled out the app submission form with the function definition, API endpoint, and response mapping.

---

## Known Tickers

These tickers have predefined sector mappings. Any other ticker still works but gets sector "Unknown" with a hash-derived risk.

| Ticker | Sector                  |
|--------|-------------------------|
| AAPL   | Technology              |
| MSFT   | Technology              |
| GOOGL  | Technology              |
| META   | Technology              |
| NVDA   | Semiconductors          |
| AMD    | Semiconductors          |
| INTC   | Semiconductors          |
| AMZN   | Consumer Discretionary  |
| TSLA   | Consumer Discretionary  |
| JPM    | Financials              |
| GS     | Financials              |
| BAC    | Financials              |
| JNJ    | Healthcare              |
| PFE    | Healthcare              |
| UNH    | Healthcare              |
| XOM    | Energy                  |
| CVX    | Energy                  |
| NFLX   | Communication Services  |

---

## Tech Stack

- **Runtime:** Python 3.9+ (stdlib only — no pip packages)
- **Hosting:** Vercel Serverless Functions
- **Agent Platform:** Join39 Agent Store
- **CI/CD:** Automatic deploys on push to `main` via Vercel + GitHub integration
