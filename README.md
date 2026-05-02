# Beaver's Choice Paper Company - Multi-Agent System

A multi-agent system for automating inventory checks, quote generation, and order fulfillment for a paper supply company.

## Overview

This project implements a **5-agent system** using [smolagents](https://github.com/huggingface/smolagents) that:

- Processes customer text requests for paper supplies
- Checks inventory availability
- Generates price quotes with bulk discounts
- Calculates delivery estimates
- Processes and fulfills orders
- Updates financial records

## Architecture

```
Layer 0: Customer Request (top)
Layer 1: Orchestrator Agent
Layer 2: Worker Agents (Inventory, Quoting, Fulfillment, Request Extraction)
Layer 3: Database Layer (SQLite)
Layer 4: External Services (LLM, Supplier System)
```

### Agents

| Agent                     | Role                                                                                     |
|---------------------------|------------------------------------------------------------------------------------------|
| **Orchestrator**          | Central coordinator, parses intent, delegates tasks, enforces business rules            |
| **Request Extraction**    | Parses free-text customer requests into structured JSON (items and quantities)           |
| **Inventory**             | Checks stock levels, assesses restock needs, calculates delivery estimates              |
| **Quoting**               | Generates prices, applies discounts, searches historical quotes for context             |
| **Fulfillment**           | Processes orders, records validated sales transactions, ensures data integrity          |

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Configuration

Set your API key in `.env`:

```
OPENAI_API_KEY=your_api_key_here
```

The system uses the Vocareum proxy: `https://openai.vocareum.com/v1`

### Run the System

```bash
python project_final.py
```

This processes all requests in `quote_requests_sample.csv` and outputs results to `test_results.csv`.

## Project Structure

```
.
├── project_final.py            # Main multi-agent implementation (5 agents)
├── paper_company_db.db         # SQLite database
├── quote_requests_sample.csv   # Test requests
├── test_results.csv            # Output results
├── test_results_final.txt      # Full test run log
├── agent_diagram_final.png     # Visual diagram
├── agent_roles_summary.txt     # Detailed agent responsibilities
├── Reflection_Report.md        # Architecture reflection and evaluation
├── requirements.txt            # Installed libraries
└── design_notes.txt            # Technical design notes
```

## Features

- **5-Agent Architecture**: Clear separation of concerns with a dedicated Request Extraction Worker
- **Deterministic Business Logic**: Discounts, pricing, and fulfillment rules enforced in Python code
- **Accurate Item Resolution**: `normalize_item_name` maps customer descriptions to canonical catalog items
- **Transparent Communication**: Clear distinction between fulfilled, partially fulfilled, and unfulfillable items
- **Financial Integrity**: All transactions recorded in SQLite with cash balance tracking
- **Delivery Estimates**: Based on quantity tiers (same day to 7 days)
- **Historical Context**: Searches past quotes for pricing consistency

## Helper Functions

All 7 required helper functions are utilized:

| Function                                           | Purpose                                      |
|----------------------------------------------------|-----------------------------------------------|
| `get_all_inventory(date)`                          | Returns all stock levels                      |
| `get_stock_level(item, date)`                      | Returns specific item stock                   |
| `get_cash_balance(date)`                           | Returns current cash position                 |
| `get_supplier_delivery_date(date, qty)`            | Estimates delivery lead time                  |
| `search_quote_history(terms, limit)`               | Searches historical quotes for context        |
| `create_transaction(item, type, qty, price, date)` | Records validated transactions                |
| `generate_financial_report(date)`                  | Returns financial summary and top-selling items |

## Testing

The system processes 20 test requests and demonstrates:

- **12+ successfully fulfilled orders** (full or partial)
- **8 unfulfilled requests** (out of stock or not in catalog)
- **Cash balance changes** from transactions (+$2,011.00 in test run)
- **Proper discount application** (10% for orders > $500)
- **Customer-friendly output formatting** with clear status indicators
- **Accurate pricing** for out-of-stock items (shows actual unit price)

## Tech Stack

- **Framework**: smolagents (ToolCallingAgent)
- **Model**: GPT-4o-mini via OpenAI API (Vocareum proxy)
- **Database**: SQLite
- **Language**: Python 3.x
- **Key Libraries**: pandas, numpy, SQLAlchemy, python-dotenv

## License

This project is for educational purposes as part of the Udacity AI Masters program.