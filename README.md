# Risk Score Calculator — Join39 App

A mock portfolio risk scoring API for the Join39 Agent Store.
Takes a stock ticker and portfolio weight %, returns a composite risk score
with breakdown across volatility, sector, and concentration risk.

---

## Deploy to Vercel (5 minutes)

### Prerequisites
- A GitHub account
- A Vercel account (free — sign up at vercel.com with your GitHub)

### Steps

1. **Create a GitHub repo**
   - Go to github.com → New Repository
   - Name it `join39-risk-score` (or whatever you like)
   - Set it to Public
   - Do NOT initialize with README (we'll push our own files)

2. **Push this code to GitHub**
   ```bash
   cd join39-risk-score
   git init
   git add .
   git commit -m "Initial commit: risk score calculator"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/join39-risk-score.git
   git push -u origin main
   ```

3. **Deploy on Vercel**
   - Go to vercel.com/new
   - Click "Import" next to your `join39-risk-score` repo
   - Leave all settings as default
   - Click "Deploy"
   - Wait ~30 seconds. You'll get a URL like:
     `https://join39-risk-score.vercel.app`

4. **Test it**
   ```
   https://join39-risk-score.vercel.app/api/risk?ticker=NVDA&weight=15
   ```
   You should see a JSON response with the risk score.

---

## Submit to Join39

Go to https://join39.org/apps/submit and fill in:

| Field | Value |
|-------|-------|
| Name | `risk-score-calculator` |
| Display Name | Risk Score Calculator |
| Description | Calculate portfolio risk scores for any stock ticker. Returns a composite risk score (0–100) with breakdown across volatility, sector risk, and concentration risk. Useful for portfolio construction and risk management. |
| Category | `finance` |
| API Endpoint | `https://YOUR-VERCEL-URL.vercel.app/api/risk` |
| HTTP Method | `GET` |
| Auth Type | `none` |

### Function Definition (paste this in the form):

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

### Response Mapping (optional):
```json
{
  "resultPath": "interpretation"
}
```
(This makes the agent receive just the human-readable interpretation string.
 Omit this if you want the agent to get the full JSON with breakdown.)

---

## API Reference

### GET /api/risk

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| ticker    | string | Yes      | Stock ticker symbol |
| weight    | number | No       | Portfolio weight % (default: 10) |

### Example Response

```json
{
  "ticker": "NVDA",
  "portfolio_weight_pct": 15.0,
  "sector": "Semiconductors",
  "risk_score": 62.3,
  "risk_label": "Elevated",
  "breakdown": {
    "volatility_component": 45.2,
    "sector_risk_component": 81.0,
    "concentration_risk_component": 42.1
  },
  "interpretation": "NVDA in the Semiconductors sector carries elevated risk at a 15.0% portfolio weight. Composite score: 62.3/100."
}
```
