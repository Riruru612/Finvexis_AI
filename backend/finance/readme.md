# Finvexis AI — Finance Department

**Module owner:** Finance Team  
**LLM Provider:** Groq (`llama-3.1-8b-instant`)  
**Data Layer:** `dummy_data.py` (in-memory, pre-loaded Q1 2026)  
**Python:** 3.10+

---

## Overview

Finvexis AI is a multi-agent finance intelligence system. A master orchestrator receives natural language queries and file uploads from the Streamlit interface, decides which agents to call (including multi-agent for cross-domain queries), dispatches them in priority order, and synthesises all outputs into a single unified response.

The system contains four specialised finance agents, each with its own deterministic engine layer and a tightly constrained LLM narrative layer. The LLM only restates pre-computed facts — all financial decisions, risk scores, and verdicts are made in Python.

---

## Project Structure

```
finance/
├── __init__.py
├── dummy_data.py               # Shared in-memory data (invoices, vendors, budgets)
├── orchestrator.py             # Master orchestrator — routes + synthesises
├── app.py                      # Streamlit interface — run this
├── invoice_generator.py        # Dev utility — generates test PDF invoices
├── readme.md
│
├── agents/
│   ├── __init__.py
│   ├── invoiceAgent.py         # Invoice Agent entry point
│   ├── auditorAgent.py         # Corporate Auditor entry point
│   ├── vendorIntelligenceAgent.py  # Vendor Intelligence entry point
│   └── fpaAgent.py             # FP&A Agent entry point
│
└── engines/
    ├── __init__.py
    ├── invoice_extractor.py    # PDF parsing + LLM structured extraction
    ├── invoice_tax_engine.py   # GST routing + TDS calculation + risk scoring
    ├── invoice_writer.py       # Writes processed invoices to INVOICE_LEDGER
    ├── budget_engine.py        # Budget vs actual, burn rate, forecast, what-if
    ├── alert_engine.py         # FP&A alert detection + insight building
    ├── narrative_engine.py     # FP&A LLM narrative generation + caching
    ├── vendor_profiler.py      # Vendor transaction profile builder
    └── vendor_behaviors.py     # Behavioral pattern detection + risk scoring
```

---

## Quick Start

```bash
pip install streamlit langchain langchain-groq pdfplumber pydantic python-dotenv
```

Create `.env` in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Run from the project root (one level above `finance/`):

```bash
streamlit run finance/app.py
```

> **Import path note:** All internal imports use `finance.` as the root prefix (e.g. `from finance.engines.budget_engine import ...`). Always run from the project root, not from inside the `finance/` folder.

---

## Architecture

### How a query flows through the system

```
User (Streamlit)
    │
    ▼
finance/app.py
    │  query: str
    │  file_bytes: bytes | None
    ▼
finance/orchestrator.py — run_orchestrator()
    │
    ├── 1. route_query()
    │       LLM reads query + file presence
    │       Returns list of agents to call
    │
    ├── 2. dispatch_agents()
    │       Calls each agent in priority order:
    │       invoice_agent → auditor_agent → vendor_agent → fpa_agent
    │       Each wrapped in try/except — one failure won't kill the response
    │
    ├── 3. synthesise_narrative()
    │       Final LLM call combines all agent narratives
    │       LLM only connects and organises — no new reasoning
    │
    └── Returns unified dict to app.py
```

### Agent priority order

Invoice always runs first because it writes new invoices to `INVOICE_LEDGER`. If the Auditor or Vendor agent ran before Invoice, they would not see the newly processed invoice in their analysis.

```
invoice_agent → auditor_agent → vendor_agent → fpa_agent
```

### LLM role — what it does and does not do

Every agent follows the same rule: the LLM is a narrator, not an analyst.

| Layer                  | Owner                            | LLM involved?                      |
| ---------------------- | -------------------------------- | ---------------------------------- |
| Data extraction (PDF)  | `invoice_extractor.py`           | Yes — structured output only       |
| Tax calculation        | `invoice_tax_engine.py`          | No                                 |
| Risk/anomaly detection | All engine files                 | No                                 |
| Risk scoring           | `vendor_behaviors.py`            | No                                 |
| Budget calculations    | `budget_engine.py`               | No                                 |
| Alert generation       | `alert_engine.py`                | No                                 |
| What-if simulation     | `budget_engine.py`               | No                                 |
| Vendor resolution      | `vendorIntelligenceAgent.py`     | Yes — fuzzy name matching only     |
| Query parsing          | `fpaAgent.py`, `auditorAgent.py` | Yes — intent/scope extraction only |
| Narrative generation   | All agent entry points           | Yes — restatement only             |
| Synthesis              | `orchestrator.py`                | Yes — connecting only              |

The LLM system prompts explicitly prohibit: speculative language ("likely", "probably", "deliberate"), adding recommendations not already computed in Python, re-interpreting or contradicting severity ratings, and calculating or inferring any numbers.

---

## Orchestrator

**File:** `finance/orchestrator.py`  
**Entry point:** `run_orchestrator(query, file_bytes, filename) -> dict`

### Input

| Parameter    | Type            | Description                                                    |
| ------------ | --------------- | -------------------------------------------------------------- |
| `query`      | `str`           | Natural language query from the user                           |
| `file_bytes` | `bytes \| None` | Raw PDF bytes if user uploaded a file                          |
| `filename`   | `str`           | Original filename for logging (default: `"uploaded_file.pdf"`) |

### Routing examples

| Query                                   | File | Agents called                                |
| --------------------------------------- | ---- | -------------------------------------------- |
| `"Process this invoice"`                | PDF  | `invoice_agent`                              |
| `"Audit Q1 2026"`                       | None | `auditor_agent`                              |
| `"Tell me about TechServe"`             | None | `vendor_agent`                               |
| `"Are we over budget in IT?"`           | None | `fpa_agent`                                  |
| `"Process invoice and check IT budget"` | PDF  | `invoice_agent`, `fpa_agent`                 |
| `"Audit Q1 and check TechServe risk"`   | None | `auditor_agent`, `vendor_agent`              |
| `"Full financial overview"`             | None | `auditor_agent`, `vendor_agent`, `fpa_agent` |
| `"Give me everything"`                  | PDF  | All 4 agents                                 |

### Output

```python
{
    "query":         str,          # original query
    "agents_called": list[str],    # agents that were invoked
    "results":       dict,         # per-agent raw output keyed by agent name
    "narrative":     str,          # unified synthesis narrative
    "has_file":      bool,         # whether a PDF was processed
    "error":         str | None    # None if successful
}
```

---

## Streamlit Interface

**File:** `finance/app.py`  
**Run:** `streamlit run finance/app.py`

### Features

- **Chat interface** with persistent history across the session
- **PDF file uploader** in sidebar — bytes passed directly to orchestrator
- **Agent badges** (colour coded) shown under each response
  -  Invoice Agent
  -  Corporate Auditor
  -  Vendor Intelligence
  -  FP&A Agent
- **Expandable structured data** per agent below each narrative
  - Invoice: metrics, line items, risk flags, ledger write status
  - Auditor: period totals, anomaly list with severity
  - Vendor: risk score + behaviors or full vendor ranking table
  - FP&A: budget bar chart per department, alerts, what-if result
- **Example queries** as clickable sidebar buttons
- **Clear chat** button to reset session

---

## Agent 1 — Invoice Agent

**File:** `finance/agents/invoiceAgent.py`  
**Entry point:** `run_invoice_pipeline(file_bytes: bytes, filename: str) -> dict`  
**Trigger:** User uploads a PDF invoice

### What it does

Accepts raw PDF bytes, extracts structured invoice data using LLM structured output, calculates Indian GST routing and TDS obligations, scores four compliance risks, writes the processed invoice to `INVOICE_LEDGER`, and generates a factual narrative.

### Pipeline

```
file_bytes
    │
    ▼
engines/invoice_extractor.py — extract_invoice()
    Writes bytes to temp file → pdfplumber extracts text + tables
    LLM structured output → InvoiceData model
    Temp file cleaned up in finally block
    │
    ▼
engines/invoice_tax_engine.py — calculate_tax()
    GST routing: compare first 2 chars of vendor/client GSTIN (state code)
    TDS 194J: subtotal > ₹30,000 + service keywords in line items
    │
    ▼
engines/invoice_tax_engine.py — score_risks()
    4 deterministic rules — no LLM
    │
    ▼
engines/invoice_writer.py — write_to_ledger()
    Appends to INVOICE_LEDGER in dummy_data
    Skips if invoice_number == "UNKNOWN"
    │
    ▼
invoiceAgent.py — generate_narrative()
    LLM restates extracted facts + tax + risks as prose
```

### Input

```python
from finance.agents.invoiceAgent import run_invoice_pipeline

with open("invoice.pdf", "rb") as f:
    result = run_invoice_pipeline(file_bytes=f.read(), filename="invoice.pdf")
```

### Output

```python
{
    "invoice": {
        "invoice_number":   str,
        "vendor_name":      str,
        "vendor_gstin":     str | None,   # 15-character GSTIN
        "client_name":      str,
        "client_gstin":     str | None,
        "date_issued":      str,
        "currency":         str,
        "subtotal":         float,
        "tax_amount":       float,
        "total_amount":     float,
        "line_items":       list[dict],   # [{description, quantity, unit_price, amount}]
        "confidence_score": float         # 0.0 – 1.0, penalised if math doesn't balance
    },
    "tax": {
        "estimated_gst":  float,
        "gst_type":       str,            # e.g. "Intra-State: 9% CGST + 9% SGST"
        "tds_applicable": bool,
        "tds_amount":     float,
        "tds_section":    str | None      # "Section 194J (10%)" or None
    },
    "risks": [
        {
            "id":       str,              # risk type ID
            "severity": str,              # "CRITICAL" | "HIGH" | "MEDIUM"
            "desc":     str
        }
    ],
    "narrative":    str,
    "ledger_write": {
        "written": bool,
        "record":  dict,                  # ledger record if written
        "reason":  str                    # only present if written=False
    }
}
```

### Risk IDs

| ID                  | Severity | Trigger                                               |
| ------------------- | -------- | ----------------------------------------------------- |
| `DUPLICATE_INVOICE` | CRITICAL | Invoice number already in processed set               |
| `TAX_MISSING`       | HIGH     | Invoice shows ₹0 tax but GST is applicable            |
| `INVALID_GSTIN`     | MEDIUM   | Vendor GSTIN present but not 15 characters            |
| `TDS_REQUIRED`      | MEDIUM   | Subtotal > ₹30,000 on professional/technical services |

### Ledger write behaviour

New invoices are always written with `status: "PENDING"` and `source: "INVOICE_AGENT"`. Department is set to `"UNASSIGNED"` — requires manual assignment. To upgrade from in-memory to a real database, only `invoice_writer.py` needs to change.

---

## Agent 2 — Corporate Auditor

**File:** `finance/agents/auditorAgent.py`  
**Entry point:** `run_auditor(query: str) -> dict`  
**Trigger:** Audit requests, anomaly queries, period reports

### What it does

Parses a time scope from natural language (full ledger, quarter, or month), filters `INVOICE_LEDGER` to that scope, aggregates financial metrics, runs six deterministic anomaly detection rules, and generates a factual audit summary.

### Input

```python
from finance.agents.auditorAgent import run_auditor

result = run_auditor("Audit Q1 2026")
result = run_auditor("Anything suspicious in March?")
result = run_auditor("Give me a full audit report")
result = run_auditor("What happened last quarter?")
```

| Scope phrase                         | What gets analysed      |
| ------------------------------------ | ----------------------- |
| "full audit", no time mentioned      | Entire invoice ledger   |
| "Q1", "this quarter", "last quarter" | Jan–Mar or Apr–Jun 2026 |
| "March", "this month", "last month"  | Single month            |

### Output

```python
{
    "scope": str,                       # e.g. "Q1 2026", "March 2026", "Full Ledger"

    "period_report": {
        "invoice_count":         int,
        "total_subtotal":        float,
        "total_tax_collected":   float,
        "total_amount_payable":  float,
        "expected_gst":          float,
        "estimated_missing_gst": float,
        "by_department":         dict,  # {dept: {subtotal, tax, total, count}}
        "by_vendor":             dict,
        "by_month":              dict,
        "by_status":             dict   # {"PAID": int, "PENDING": int}
    },

    "anomalies": [
        {
            "id":              str,
            "severity":        str,     # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
            "vendor":          str,
            "invoice_numbers": list[str],
            "amount":          float,
            "description":     str
        }
    ],

    "narrative": str
}
```

### Anomaly IDs

| ID                     | Severity                 | Trigger                                                |
| ---------------------- | ------------------------ | ------------------------------------------------------ |
| `DUPLICATE_INVOICE`    | CRITICAL                 | Same invoice number appears more than once             |
| `MISSING_GST`          | CRITICAL / HIGH / MEDIUM | Vendor invoices with ₹0 tax (escalates if systemic)    |
| `SPENDING_SPIKE`       | HIGH                     | Any month 40%+ above period average                    |
| `TDS_THRESHOLD_GAMING` | HIGH                     | Vendor subtotals consistently within ₹1,500 of ₹30,000 |
| `VENDOR_RATE_HIKE`     | MEDIUM                   | Unit price increased ≥10% across invoices              |
| `LATE_INVOICING`       | LOW                      | Invoice submitted well after work period               |

---

## Agent 3 — Vendor Intelligence

**File:** `finance/agents/vendorIntelligenceAgent.py`  
**Entry point:** `run_vendor_intelligence(query: str) -> dict`  
**Trigger:** Vendor name mentioned, risk queries, vendor comparisons

### What it does

Two modes in a single entry point. LLM resolves fuzzy vendor names automatically — partial names, abbreviations, and descriptions all match.

**Single vendor mode:** Builds a complete transaction profile, runs six deterministic behavioral pattern detectors, calculates a 0–100 risk score, and generates a factual vendor intelligence report.

**All-vendor mode:** Scores and ranks all 8 vendors when the query asks for a comparison or ranking.

### Pipeline

```
query
    │
    ▼
vendorIntelligenceAgent.py — resolve_vendor()
    LLM fuzzy-matches vendor name to VENDOR_MASTER
    Returns vendor_id + query_type (single_vendor | all_vendors)
    │
    ▼
engines/vendor_profiler.py — build_vendor_profile()
    Computes: financials, GST compliance rate, monthly spend, invoice history
    Determines intra/inter-state GST by comparing state codes
    │
    ▼
engines/vendor_behaviors.py — detect_vendor_behaviors()
    6 deterministic checks — no LLM
    │
    ▼
engines/vendor_behaviors.py — calculate_risk_score()
    Severity-weighted scoring — capped at 100
    │
    ▼
vendorIntelligenceAgent.py — generate_vendor_narrative()
    LLM restates profile + behaviors + score as prose
```

### Input

```python
from finance.agents.vendorIntelligenceAgent import run_vendor_intelligence

result = run_vendor_intelligence("Tell me about Cloud Data Dynamics")
result = run_vendor_intelligence("Is TechServe a risky vendor?")
result = run_vendor_intelligence("Which vendor should I be most worried about?")
result = run_vendor_intelligence("Compare all vendors by risk")
```

### Output — Single Vendor

```python
{
    "query_type":  "single_vendor",
    "vendor_id":   str,
    "vendor_name": str,
    "risk_score":  int,              # 0–100
    "risk_rating": str,              # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    "profile": {
        "gst_type":            str,
        "invoice_count":       int,
        "total_subtotal":      float,
        "total_tax_paid":      float,
        "missing_gst_amount":  float,
        "gst_compliance_rate": float,
        "status_breakdown":    dict,
        "monthly_spend":       dict,
        "invoice_history":     list[dict]
    },
    "behaviors": [
        {
            "behavior": str,         # behavior ID
            "severity": str,
            "evidence": list[str],   # specific data points
            "summary":  str          # factual description — no inferred intent
        }
    ],
    "narrative": str
}
```

### Output — All Vendors

```python
{
    "query_type": "all_vendors",
    "rankings": [
        {
            "vendor_id":           str,
            "vendor_name":         str,
            "risk_score":          int,
            "risk_rating":         str,
            "behavior_count":      int,
            "top_behaviors":       list[str],
            "total_spend":         float,
            "gst_compliance_rate": float
        }
        # sorted highest risk first
    ],
    "narrative": str
}
```

### Behavior IDs

| ID                             | Severity        | Trigger                                                        |
| ------------------------------ | --------------- | -------------------------------------------------------------- |
| `DUPLICATE_INVOICE_SUBMISSION` | CRITICAL        | Vendor submitted same invoice number twice                     |
| `GST_NON_COMPLIANCE`           | CRITICAL / HIGH | ≥1 invoice with ₹0 GST; CRITICAL if all invoices non-compliant |
| `TDS_THRESHOLD_GAMING`         | HIGH            | ≥2 invoices within ₹1,500 of ₹30,000 TDS threshold             |
| `RATE_HIKE_TRAJECTORY`         | HIGH / MEDIUM   | Unit price increased ≥10% across invoices                      |
| `HIGH_SPEND_CONCENTRATION`     | MEDIUM          | Vendor accounts for ≥25% of total ledger spend                 |
| `CHRONIC_LATE_INVOICING`       | MEDIUM / LOW    | Invoice(s) submitted after the work period                     |

### Risk Score Calculation

| Behavior Severity               | Points       |
| ------------------------------- | ------------ |
| CRITICAL                        | +35          |
| HIGH                            | +20          |
| MEDIUM                          | +10          |
| LOW                             | +5           |
| Zero GST compliance rate        | +15 bonus    |
| More PENDING than PAID invoices | +5 bonus     |
| Maximum                         | 100 (capped) |

| Score  | Rating   |
| ------ | -------- |
| 70–100 | CRITICAL |
| 45–69  | HIGH     |
| 20–44  | MEDIUM   |
| 0–19   | LOW      |

---

## Agent 4 — FP&A Agent

**File:** `finance/agents/fpaAgent.py`  
**Entry point:** `run_fpa(query: str) -> dict`  
**Trigger:** Budget queries, burn rate, forecast, what-if simulations

### What it does

Four query modes in a single entry point. All calculations exclude duplicate invoices automatically. Query intent is parsed deterministically first (regex/keyword matching) with LLM as fallback only.

### Pipeline

```
query
    │
    ▼
fpaAgent.py — smart_parse_query()
    Deterministic keyword matching → FPAQuery
    Falls back to LLM parse only if no pattern matches
    │
    ▼
engines/budget_engine.py — build_budget_vs_actual()
    Variance per department — deduplicates invoice numbers
    │
    ▼
engines/budget_engine.py — build_monthly_burn()
    Month-over-month spend + MoM change %
    │
    ▼
engines/budget_engine.py — forecast_quarter_end()
    Projects quarter-end spend from avg monthly burn
    │
    ▼
engines/alert_engine.py — detect_fpa_alerts()
    5 deterministic alert rules — pre-written action text
    │
    ▼
engines/budget_engine.py — run_what_if()   [what_if queries only]
    Simulates additional spend → APPROVE | REJECT verdict
    │
    ▼
engines/narrative_engine.py — cached_narrative()
    LLM restates pre-computed insights as prose
    lru_cache avoids repeated LLM calls for identical inputs
```

### Input

```python
from finance.agents.fpaAgent import run_fpa

result = run_fpa("Full FP&A report for Q1")
result = run_fpa("How is IT tracking against budget?")
result = run_fpa("Which departments are going to overrun?")
result = run_fpa("What if IT spends another ₹1,00,000?")
```

### Query modes

| Mode              | `query_type`  | Example queries                                            |
| ----------------- | ------------- | ---------------------------------------------------------- |
| Full report       | `full_report` | "Full FP&A report", "How are we tracking?"                 |
| Single department | `single_dept` | "IT burn rate", "How is Marketing doing?"                  |
| Forecast          | `forecast`    | "Which depts will overrun?", "Will IT stay within budget?" |
| What-if           | `what_if`     | "What if IT spends another ₹1 lakh?"                       |

### Output

```python
{
    "query_type": str,
    "scope":      str,                    # e.g. "All Departments — Q1 2026"

    "budget_vs_actual": {
        "IT": {
            "q1_budget":        float,
            "actual_spend":     float,
            "variance":         float,    # positive = over budget
            "utilization_pct":  float,
            "budget_remaining": float,    # negative = over budget
            "invoice_count":    int,
            "amount_paid":      float,
            "amount_pending":   float,
            "status":           str       # OVER_BUDGET | AT_RISK | ON_TRACK | UNDER_UTILIZED
        }
        # one entry per department
    },

    "monthly_burn": {
        "IT": {
            "monthly_breakdown": [
                {"month": str, "spend": float, "mom_change": float, "mom_pct": float}
            ],
            "avg_monthly_burn": float,
            "peak_month":       str
        }
    },

    "forecasts": {
        "IT": {
            "projected_quarter_total":   float,
            "projected_variance":        float,
            "projected_utilization_pct": float,
            "forecast_status":           str  # WILL_OVERRUN | AT_RISK | WILL_STAY_WITHIN_BUDGET
        }
    },

    "alerts": [
        {
            "id":              str,
            "severity":        str,
            "department":      str,
            "department_head": str,
            "description":     str,
            "actions":         list[str]  # pre-written action text — not generated by LLM
        }
    ],

    # Only present for what_if queries:
    "what_if_result": {
        "department":              str,
        "additional_spend":        float,
        "current_actual":          float,
        "new_actual":              float,
        "q1_budget":               float,
        "new_variance":            float,
        "new_utilization_pct":     float,
        "budget_remaining_after":  float,
        "budget_impact":           str,   # WITHIN_BUDGET | CROSSES_BUDGET | ALREADY_OVER_BUDGET
        "already_over_budget":     bool,
        "new_status":              str
    },

    "narrative": str
}
```

### Status values

| `status`         | Condition         |
| ---------------- | ----------------- |
| `OVER_BUDGET`    | actual > budget   |
| `AT_RISK`        | utilization ≥ 85% |
| `ON_TRACK`       | utilization ≥ 50% |
| `UNDER_UTILIZED` | utilization < 50% |

| `forecast_status`         | Condition                   |
| ------------------------- | --------------------------- |
| `WILL_OVERRUN`            | projected total > budget    |
| `AT_RISK`                 | projected utilization ≥ 90% |
| `WILL_STAY_WITHIN_BUDGET` | projected total ≤ budget    |

### Alert IDs

| ID                      | Severity | Trigger                               |
| ----------------------- | -------- | ------------------------------------- |
| `BUDGET_OVERRUN`        | CRITICAL | Department already exceeded Q1 budget |
| `BUDGET_AT_RISK`        | HIGH     | Utilization ≥ 85%                     |
| `FORECAST_OVERRUN`      | HIGH     | Within budget but projected to breach |
| `ACCELERATING_BURN`     | MEDIUM   | Month-over-month burn jumped ≥ 30%    |
| `BUDGET_UNDER_UTILIZED` | LOW      | Utilization < 60%                     |

---

## Data Layer — `dummy_data.py`

**File:** `finance/dummy_data.py`  
Shared by all agents. Contains pre-loaded Q1 2026 data with embedded patterns designed to trigger every agent's detection logic.

### Contents

| Object               | Type         | Used by                                           |
| -------------------- | ------------ | ------------------------------------------------- |
| `INVOICE_LEDGER`     | `list[dict]` | All agents                                        |
| `VENDOR_MASTER`      | `dict`       | Auditor, Vendor Intelligence                      |
| `DEPARTMENT_BUDGETS` | `dict`       | Auditor, FP&A                                     |
| `CLIENT`             | `dict`       | Vendor Intelligence                               |
| `EMBEDDED_PATTERNS`  | `dict`       | Reference — documents what each agent should find |

19 invoices, 8 vendors, 5 departments, Q1 2026 (January–March).

### Helper functions

```python
from finance.dummy_data import (
    get_invoices_by_department,
    get_invoices_by_vendor,
    get_invoices_by_month,
    get_total_spend_by_department,
    get_total_tax_collected,
    get_total_missing_tax,
)
```

### Embedded patterns

| Pattern                     | Detected by                  | Details                                                             |
| --------------------------- | ---------------------------- | ------------------------------------------------------------------- |
| Duplicate invoice           | Auditor, Vendor Intelligence | INV-CDD-001 resubmitted as INV-CDD-007                              |
| Systemic missing GST        | Auditor, Vendor Intelligence | Cloud Data Dynamics — ₹0 GST all 3 months, ₹81,000 unpaid           |
| Rate hike trajectory        | Auditor, Vendor Intelligence | Cloud Data Dynamics — ₹1,50,000 → ₹1,62,000 → ₹1,80,000 (+20%)      |
| TDS threshold gaming        | Auditor, Vendor Intelligence | TechServe — ₹28,500 / ₹28,800 / ₹29,700 (always just under ₹30,000) |
| Spending spike              | Auditor                      | March total significantly above Jan/Feb average                     |
| Late invoicing              | Auditor, Vendor Intelligence | LegalEdge — invoices 4–6 weeks after work period                    |
| IT budget overrun           | FP&A                         | IT actual ~₹8.7L vs ₹6L budget (~45% over)                          |
| Marketing under-utilization | FP&A                         | Marketing at ~75% of ₹3L budget                                     |

### Upgrading to a real database

Only `invoice_writer.py` needs to change for DB writes. For DB reads across all agents, replace the `INVOICE_LEDGER` list references in each engine with the appropriate query. The function signatures and output schemas stay the same.

---

## CLI Testing

Each agent can be tested independently. Run from the **project root** (one level above `finance/`):

```bash
python finance/dummy_data.py                         # confirm data loads + prints summary

python finance/agents/auditorAgent.py                # 3 test audit queries
python finance/agents/vendorIntelligenceAgent.py     # 3 vendor profiles + ranking
python finance/agents/fpaAgent.py                    # full report, dept drill, what-if

# Invoice agent requires a PDF path:
python finance/agents/invoiceAgent.py path/to/invoice.pdf

# Orchestrator multi-agent test (no file):
python finance/orchestrator.py
```

> **Before handing off to backend:** Remove or comment out all `if __name__ == "__main__":` blocks in every agent file. In production, all agents are called through `run_orchestrator()`.

---

## Environment

| Variable       | Required | Description                                             |
| -------------- | -------- | ------------------------------------------------------- |
| `GROQ_API_KEY` | Yes      | Groq API key — all LLM calls use `llama-3.1-8b-instant` |

All agents raise `ValueError` immediately on startup if `GROQ_API_KEY` is missing.
