# Beaver's Choice Paper Company - Multi-Agent System

A multi-agent system for automating inventory checks, quote generation, and order fulfillment for a paper supply company.

## Overview

This project implements a 4-agent system using [smolagents](https://github.com/huggingface/smolagents) that:

- Processes customer text requests for paper supplies
- Checks inventory availability
- Generates price quotes with bulk discounts
- Calculates delivery estimates
- Processes and fulfills orders
- Updates financial records

## Architecture

```
Layer 0: Customer Request
Layer 1: Orchestrator Agent
Layer 2: Worker Agents (Inventory, Quoting, Fulfillment)
Layer 3: Database Layer (SQLite)
Layer 4: External Services (LLM, Supplier System)
```

### Agents

| Agent            | Role                                                    |
| ---------------- | ------------------------------------------------------- |
| **Orchestrator** | Central coordinator, parses requests, delegates tasks   |
| **Inventory**    | Checks stock levels, assesses restock needs             |
| **Quoting**      | Generates prices, applies discounts, estimates delivery |
| **Fulfillment**  | Processes orders, records transactions                  |

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
python project_starter.py
```

This processes all requests in `quote_requests_sample.csv` and outputs results to `test_results.csv`.

## Project Structure

.

├── project\_starter.py       # Main multi-agent implementation

├── generate\_diagram.py      # Architecture diagram generator

├── paper\_company\_db.db     # SQLite database

├── quote\_requests\_sample.csv  # Test requests

├── test\_results.csv         # Output results

├── agent\_workflow\_diagram.png # Visual diagram

├── agent\_architecture\_diagram.txt # ASCII diagram

├── Reflection\_Report.md   # Architecture reflection

├── requirements.txt  # installed libraries

└── design\_notes.txt       # Technical design notes

## Features

- **Automated Inventory Checking**: Real-time stock level verification
- **Dynamic Pricing**: 10% bulk discount for orders over $500
- **Delivery Estimates**: Based on quantity tiers (same day to 7 days)
- **Transaction Recording**: Full sales and inventory tracking
- **Financial Reporting**: Cash balance and inventory value tracking

## Helper Functions

All 7 required helper functions are utilized:

| Function                                           | Purpose                       |
| -------------------------------------------------- | ----------------------------- |
| `get_all_inventory(date)`                          | Returns all stock levels      |
| `get_stock_level(item, date)`                      | Returns specific item stock   |
| `get_cash_balance(date)`                           | Returns current cash position |
| `get_supplier_delivery_date(date, qty)`            | Estimates delivery lead time  |
| `search_quote_history(terms, limit)`               | Searches historical quotes    |
| `create_transaction(item, type, qty, price, date)` | Records transactions          |
| `generate_financial_report(date)`                  | Returns financial summary     |

## Testing

The system processes 20 test requests and demonstrates:

- 8+ successfully fulfilled orders
- 12 unfulfilled (insufficient stock)
- Cash balance changes from transactions
- Proper discount application
- Customer-friendly output formatting

## Tech Stack

- **Framework**: smolagents (ToolCallingAgent)
- **Model**: GPT-4o-mini via OpenAI API
- **Database**: SQLite
- **Language**: Python 3.x

## License

This project is for educational purposes as part of the Udacity AI Masters program.
