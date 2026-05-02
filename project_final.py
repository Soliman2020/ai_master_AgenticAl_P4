import pandas as pd
import numpy as np
import os
import ast
import json
import re
import time
from dataclasses import dataclass
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional
from sqlalchemy import create_engine, Engine
from dotenv import load_dotenv

# ==================== ENVIRONMENT ====================
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

db_engine = create_engine("sqlite:///paper_company_db.db")

# ==================== CATALOG ====================
paper_supplies = [
    {"item_name": "A4 paper", "category": "paper", "unit_price": 0.05},
    {"item_name": "Letter-sized paper", "category": "paper", "unit_price": 0.06},
    {"item_name": "Cardstock", "category": "paper", "unit_price": 0.15},
    {"item_name": "Colored paper", "category": "paper", "unit_price": 0.10},
    {"item_name": "Glossy paper", "category": "paper", "unit_price": 0.20},
    {"item_name": "Matte paper", "category": "paper", "unit_price": 0.18},
    {"item_name": "Recycled paper", "category": "paper", "unit_price": 0.08},
    {"item_name": "Eco-friendly paper", "category": "paper", "unit_price": 0.12},
    {"item_name": "Poster paper", "category": "paper", "unit_price": 0.25},
    {"item_name": "Banner paper", "category": "paper", "unit_price": 0.30},
    {"item_name": "Kraft paper", "category": "paper", "unit_price": 0.10},
    {"item_name": "Construction paper", "category": "paper", "unit_price": 0.07},
    {"item_name": "Wrapping paper", "category": "paper", "unit_price": 0.15},
    {"item_name": "Glitter paper", "category": "paper", "unit_price": 0.22},
    {"item_name": "Decorative paper", "category": "paper", "unit_price": 0.18},
    {"item_name": "Letterhead paper", "category": "paper", "unit_price": 0.12},
    {"item_name": "Legal-size paper", "category": "paper", "unit_price": 0.08},
    {"item_name": "Crepe paper", "category": "paper", "unit_price": 0.05},
    {"item_name": "Photo paper", "category": "paper", "unit_price": 0.25},
    {"item_name": "Uncoated paper", "category": "paper", "unit_price": 0.06},
    {"item_name": "Butcher paper", "category": "paper", "unit_price": 0.10},
    {"item_name": "Heavyweight paper", "category": "paper", "unit_price": 0.20},
    {"item_name": "Standard copy paper", "category": "paper", "unit_price": 0.04},
    {"item_name": "Bright-colored paper", "category": "paper", "unit_price": 0.12},
    {"item_name": "Patterned paper", "category": "paper", "unit_price": 0.15},
    {"item_name": "Paper plates", "category": "product", "unit_price": 0.10},
    {"item_name": "Paper cups", "category": "product", "unit_price": 0.08},
    {"item_name": "Paper napkins", "category": "product", "unit_price": 0.02},
    {"item_name": "Disposable cups", "category": "product", "unit_price": 0.10},
    {"item_name": "Table covers", "category": "product", "unit_price": 1.50},
    {"item_name": "Envelopes", "category": "product", "unit_price": 0.05},
    {"item_name": "Sticky notes", "category": "product", "unit_price": 0.03},
    {"item_name": "Notepads", "category": "product", "unit_price": 2.00},
    {"item_name": "Invitation cards", "category": "product", "unit_price": 0.50},
    {"item_name": "Flyers", "category": "product", "unit_price": 0.15},
    {"item_name": "Party streamers", "category": "product", "unit_price": 0.05},
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},
    {"item_name": "Paper party bags", "category": "product", "unit_price": 0.25},
    {"item_name": "Name tags with lanyards", "category": "product", "unit_price": 0.75},
    {"item_name": "Presentation folders", "category": "product", "unit_price": 0.50},
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},
    {"item_name": "100 lb cover stock", "category": "specialty", "unit_price": 0.50},
    {"item_name": "80 lb text paper", "category": "specialty", "unit_price": 0.40},
    {"item_name": "250 gsm cardstock", "category": "specialty", "unit_price": 0.30},
    {"item_name": "220 gsm poster paper", "category": "specialty", "unit_price": 0.35},
]

# ==================== DATABASE UTILITIES ====================
def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """Generate a random subset of inventory items from the catalog."""
    np.random.seed(seed)
    num_items = int(len(paper_supplies) * coverage)
    selected_indices = np.random.choice(range(len(paper_supplies)), size=num_items, replace=False)
    selected_items = [paper_supplies[i] for i in selected_indices]
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": int(np.random.randint(200, 800)),
            "min_stock_level": int(np.random.randint(50, 150)),
        })
    return pd.DataFrame(inventory)


def init_database(db_engine: Engine = None, seed: int = 137) -> Engine:
    """Initialize the database with inventory, quotes, and seed transactions."""
    if db_engine is None:
        db_engine = create_engine("sqlite:///paper_company_db.db")
    try:
        transactions_schema = pd.DataFrame({
            "id": [], "item_name": [], "transaction_type": [],
            "units": [], "price": [], "transaction_date": [],
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        initial_date = datetime(2025, 1, 1).isoformat()

        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", "") if isinstance(x, dict) else "")
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", "") if isinstance(x, dict) else "")
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", "") if isinstance(x, dict) else "")
        else:
            quotes_df["job_type"] = ""
            quotes_df["order_size"] = ""
            quotes_df["event_type"] = ""

        quotes_df = quotes_df[["request_id", "total_amount", "quote_explanation",
                                "order_date", "job_type", "order_size", "event_type"]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        initial_transactions = [{
            "item_name": None, "transaction_type": "sales",
            "units": None, "price": 50000.0, "transaction_date": initial_date,
        }]
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": int(item["current_stock"]),
                "price": float(item["current_stock"] * item["unit_price"]),
                "transaction_date": initial_date,
            })

        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)
        return db_engine
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def create_transaction(item_name: str, transaction_type: str, quantity: int,
                        price: float, date: Union[str, datetime]) -> int:
    """Insert a transaction record and return its row ID."""
    try:
        date_str = date.isoformat() if isinstance(date, datetime) else date
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")
        with db_engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO transactions (item_name, transaction_type, units, price, transaction_date)
                    VALUES (:item_name, :transaction_type, :units, :price, :transaction_date)
                """),
                {"item_name": item_name, "transaction_type": transaction_type,
                 "units": quantity, "price": price, "transaction_date": date_str}
            )
            inserted_id = conn.execute(text("SELECT last_insert_rowid() AS id")).scalar()
        return int(inserted_id)
    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise


def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """Return a dict of item_name -> stock level as of a given date."""
    query = """
        SELECT item_name,
            SUM(CASE WHEN transaction_type = 'stock_orders' THEN units
                     WHEN transaction_type = 'sales' THEN -units ELSE 0 END) AS stock
        FROM transactions
        WHERE item_name IS NOT NULL AND transaction_date <= :as_of_date
        GROUP BY item_name HAVING stock > 0
    """
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})
    return dict(zip(result["item_name"], result["stock"]))


def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """Return a DataFrame with the current stock level for a specific item."""
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()
    stock_query = """
        SELECT item_name,
            COALESCE(SUM(CASE WHEN transaction_type = 'stock_orders' THEN units
                              WHEN transaction_type = 'sales' THEN -units ELSE 0 END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name AND transaction_date <= :as_of_date
    """
    return pd.read_sql(stock_query, db_engine, params={"item_name": item_name, "as_of_date": as_of_date})


def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """Calculate estimated supplier delivery date based on order quantity."""
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date format: {input_date_str}")
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7
    return (input_date_dt + timedelta(days=days)).strftime("%Y-%m-%d")


def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """Calculate current cash balance as of a given date."""
    try:
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine, params={"as_of_date": as_of_date},
        )
        if transactions.empty:
            return 0.0
        total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
        total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
        return float(total_sales - total_purchases)
    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """Generate a full financial report including cash, inventory value, and top sales."""
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()
    cash = get_cash_balance(as_of_date)
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = int(stock_info["current_stock"].iloc[0]) if not stock_info.empty else 0
        item_value = float(stock * item["unit_price"])
        inventory_value += item_value
        inventory_summary.append({
            "item_name": item["item_name"], "stock": stock,
            "unit_price": float(item["unit_price"]), "value": item_value,
        })
    top_sales_query = """
        SELECT item_name, SUM(units) AS total_units, SUM(price) AS total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name ORDER BY total_revenue DESC LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    return {
        "as_of_date": as_of_date, "cash_balance": cash,
        "inventory_value": inventory_value, "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_sales.to_dict(orient="records"),
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """Search historical quotes by keyword terms."""
    safe_limit = max(1, min(int(limit), 20))
    conditions = []
    params = {}
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(f"(LOWER(qr.response) LIKE :{param_name} OR LOWER(q.quote_explanation) LIKE :{param_name})")
        params[param_name] = f"%{term.lower()}%"
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"""
        SELECT qr.response AS original_request, q.total_amount, q.quote_explanation,
               q.job_type, q.order_size, q.event_type, q.order_date
        FROM quotes q JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause} ORDER BY q.order_date DESC LIMIT {safe_limit}
    """
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

# ==================== ITEM NORMALIZATION ====================
ITEM_MAPPING = {
    "glossy paper": "Glossy paper", "a4 glossy paper": "Glossy paper",
    "glossy a4 paper": "Glossy paper", "cardstock": "Cardstock",
    "heavy cardstock": "Cardstock", "heavyweight cardstock": "Cardstock",
    "colored paper": "Colored paper", "assorted colored paper": "Colored paper",
    "colorful poster paper": "Poster paper", "poster paper": "Poster paper",
    "streamers": "Party streamers", "washi tape": "Decorative adhesive tape (washi tape)",
    "decorative washi tape": "Decorative adhesive tape (washi tape)",
    "construction paper": "Construction paper",
    "colorful construction paper": "Construction paper",
    "a4 paper": "A4 paper", "a4 printer paper": "A4 paper",
    "a4 white printer paper": "A4 paper", "a4 white paper": "A4 paper",
    "printer paper": "Standard copy paper", "standard printer paper": "Standard copy paper",
    "standard printing paper": "Standard copy paper", "white printer paper": "Standard copy paper",
    "matte paper": "Matte paper", "a4 matte paper": "Matte paper", "a3 matte paper": "Matte paper",
    "recycled paper": "Recycled paper", "a4 recycled paper": "Recycled paper",
    "recycled cardstock": "Recycled paper", "kraft paper": "Kraft paper",
    "recycled kraft paper": "Kraft paper", "envelopes": "Envelopes",
    "kraft envelopes": "Envelopes", "napkins": "Paper napkins",
    "paper napkins": "Paper napkins", "table napkins": "Paper napkins",
    "paper cups": "Paper cups", "disposable cups": "Disposable cups",
    "paper plates": "Paper plates",
    "poster board": "Large poster paper (24x36 inches)",
    "poster boards": "Large poster paper (24x36 inches)",
    "heavyweight paper": "Heavyweight paper", "flyers": "Flyers",
    "posters": "Flyers", "tickets": "Flyers",
}


def normalize_item_name(requested_item: str) -> str:
    """Normalize a customer-provided item name to the closest catalog item name."""
    requested_lower = requested_item.lower().strip()
    if requested_lower in ITEM_MAPPING:
        return ITEM_MAPPING[requested_lower]
    for key, value in ITEM_MAPPING.items():
        if key in requested_lower or requested_lower in key:
            return value
    for item in paper_supplies:
        catalog_name = item["item_name"].lower()
        if catalog_name in requested_lower or requested_lower in catalog_name:
            return item["item_name"]
    return requested_item.title()


def item_exists_in_catalog(item_name: str) -> bool:
    """Check whether a (possibly unnormalized) item name exists in the catalog."""
    normalized = normalize_item_name(item_name)
    return any(item["item_name"].lower() == normalized.lower() for item in paper_supplies)


def get_unit_price_internal(item_name: str) -> float:
    """Return the unit price for a catalog item, or 0.0 if not found."""
    for item in paper_supplies:
        if item["item_name"].lower() == item_name.lower():
            return float(item["unit_price"])
    return 0.0

# ==================== SMOLAGENTS SETUP ====================
from smolagents import ToolCallingAgent, OpenAIServerModel, tool

model = OpenAIServerModel(
    model_id="gpt-4o-mini",
    api_key=openai_api_key,
    api_base="https://openai.vocareum.com/v1"
)

# ==================== TOOLS ====================
@tool
def get_unit_price(item_name: str) -> float:
    """Get the unit price of a catalog item.

    Args:
        item_name: Exact or normalized item name.

    Returns:
        Unit price as a float, or 0.0 if not found.
    """
    return get_unit_price_internal(item_name)


@tool
def check_inventory(agent_date: str) -> Dict:
    """Get current inventory levels for all items as of a given date.

    Args:
        agent_date: Date in YYYY-MM-DD format.

    Returns:
        Dictionary mapping item names to stock and unit price details.
    """
    inventory = get_all_inventory(agent_date)
    return {
        item_name: {"current_stock": int(stock), "unit_price": get_unit_price_internal(item_name)}
        for item_name, stock in inventory.items()
    }


@tool
def check_item_stock(item_name: str, agent_date: str) -> Dict:
    """Check the stock level for a specific item.

    Args:
        item_name: Requested item name.
        agent_date: Date in YYYY-MM-DD format.

    Returns:
        Dict with normalized item_name, current_stock, and unit_price.
    """
    normalized = normalize_item_name(item_name)
    result = get_stock_level(normalized, agent_date)
    stock = int(result["current_stock"].iloc[0]) if not result.empty else 0
    return {"item_name": normalized, "current_stock": stock,
            "unit_price": get_unit_price_internal(normalized)}


@tool
def get_delivery_date(agent_date: str, quantity: int) -> str:
    """Get the estimated supplier delivery date based on quantity.

    Args:
        agent_date: Start date in YYYY-MM-DD format.
        quantity: Number of units being ordered.

    Returns:
        Estimated delivery date in YYYY-MM-DD format.
    """
    return get_supplier_delivery_date(agent_date, quantity)


@tool
def search_historical_quotes(search_terms: List[str]) -> List[Dict]:
    """Search historical quotes for similar past orders.

    Args:
        search_terms: List of keywords to search for.

    Returns:
        List of matching historical quote records.
    """
    return search_quote_history(search_terms, limit=3)


@tool
def get_financial_report(agent_date: str) -> Dict:
    """Generate a full financial report as of a given date.

    Args:
        agent_date: Date in YYYY-MM-DD format.

    Returns:
        Financial report dictionary with cash, inventory, and top sales.
    """
    return generate_financial_report(agent_date)


@tool
def get_cash(agent_date: str) -> float:
    """Get the current cash balance as of a given date.

    Args:
        agent_date: Date in YYYY-MM-DD format.

    Returns:
        Cash balance as a float.
    """
    return get_cash_balance(agent_date)


@tool
def create_sale_transaction(item_name: str, quantity: int, agent_date: str) -> Dict:
    """Record a validated sale transaction.

    Args:
        item_name: Item name to sell.
        quantity: Number of units to sell.
        agent_date: Date of sale in YYYY-MM-DD format.

    Returns:
        Transaction details including transaction_id and total_price.
    """
    normalized = normalize_item_name(item_name)
    if not item_exists_in_catalog(normalized):
        raise ValueError(f"Item not available in catalog: {item_name}")
    stock_info = check_item_stock(normalized, agent_date)
    current_stock = int(stock_info["current_stock"])
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")
    if current_stock < quantity:
        raise ValueError(f"Insufficient stock for {normalized}. Available={current_stock}, requested={quantity}")
    unit_price = get_unit_price_internal(normalized)
    total_price = round(unit_price * quantity, 2)
    transaction_id = create_transaction(normalized, "sales", quantity, total_price, agent_date)
    return {"transaction_id": transaction_id, "item_name": normalized,
            "quantity": quantity, "unit_price": unit_price, "total_price": total_price}


@tool
def create_stock_order(item_name: str, quantity: int, agent_date: str) -> Dict:
    """Record a validated stock replenishment order.

    Args:
        item_name: Item name to restock.
        quantity: Number of units to order.
        agent_date: Date of order in YYYY-MM-DD format.

    Returns:
        Transaction details including transaction_id and total_cost.
    """
    normalized = normalize_item_name(item_name)
    if not item_exists_in_catalog(normalized):
        raise ValueError(f"Item not available in catalog: {item_name}")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")
    unit_price = get_unit_price_internal(normalized)
    total_cost = round(unit_price * quantity, 2)
    cash = get_cash_balance(agent_date)
    if cash < total_cost:
        raise ValueError(f"Insufficient cash. Cash={cash:.2f}, required={total_cost:.2f}")
    transaction_id = create_transaction(normalized, "stock_orders", quantity, total_cost, agent_date)
    return {"transaction_id": transaction_id, "item_name": normalized,
            "quantity": quantity, "total_cost": total_cost}


@tool
def extract_request_items(request_text: str) -> Dict:
    """Extract requested items and quantities from a customer request as structured JSON.

    Uses an inner worker agent (RequestExtractionWorker) with an LLM call
    to parse free-text into a structured list of items and quantities.

    Args:
        request_text: Raw customer request text.

    Returns:
        Dict with key 'items', each containing 'requested_name' and 'quantity'.
    """
    # RequestExtractionWorker: 5th agent — dedicated purely to JSON extraction, no tools needed
    extraction_worker = ToolCallingAgent(
        tools=[],
        model=model,
        name="RequestExtractionWorker",
        description="Extracts requested items and quantities from customer text as JSON only."
    )
    prompt = f"""
You extract structured order lines from customer requests.
Return valid JSON only with this exact schema:
{{
  "items": [
    {{"requested_name": "string", "quantity": 1}}
  ]
}}

Rules:
- Extract only explicitly requested items.
- quantity must be an integer > 0.
- If quantity is missing but item is clearly requested, use 1.
- Do not calculate prices.
- Do not add commentary.
- Do not wrap the JSON in markdown fences.

Customer request:
{request_text}
"""
    raw = extraction_worker.run(prompt)
    if isinstance(raw, dict):
        return raw
    cleaned = str(raw).strip()
    match = re.search(r'\{.*\}', cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)
    data = json.loads(cleaned)
    if not isinstance(data, dict) or "items" not in data:
        raise ValueError("Invalid extraction payload")
    return data


@tool
def get_catalog_item_details(item_name: str, agent_date: str) -> Dict:
    """Get full catalog details and availability for an item.

    Args:
        item_name: Requested item name (raw or normalized).
        agent_date: Date in YYYY-MM-DD format.

    Returns:
        Dict with normalized_name, in_catalog flag, current_stock, and unit_price.
    """
    normalized = normalize_item_name(item_name)
    in_catalog = item_exists_in_catalog(item_name)
    stock_info = check_item_stock(normalized, agent_date) if in_catalog else {"current_stock": 0, "unit_price": 0.0}
    return {
        "requested_name": item_name, "normalized_name": normalized,
        "in_catalog": in_catalog,
        "current_stock": int(stock_info.get("current_stock", 0)),
        "unit_price": float(stock_info.get("unit_price", 0.0)),
    }

# ==================== AGENTS (exactly 5) ====================
class InventoryAgent(ToolCallingAgent):
    """Worker agent responsible for stock checks and replenishment orders."""
    def __init__(self, model_to_use: OpenAIServerModel):
        super().__init__(
            tools=[check_inventory, check_item_stock, get_delivery_date, create_stock_order],
            model=model_to_use,
            name="InventoryAgent",
            description="Checks stock levels and places restock orders."
        )


class QuotingAgent(ToolCallingAgent):
    """Worker agent responsible for generating prices and quote context."""
    def __init__(self, model_to_use: OpenAIServerModel):
        super().__init__(
            tools=[get_unit_price, get_delivery_date, search_historical_quotes, get_catalog_item_details],
            model=model_to_use,
            name="QuotingAgent",
            description="Generates item pricing and quote summaries."
        )


class FulfillmentAgent(ToolCallingAgent):
    """Worker agent responsible for processing and recording sales transactions."""
    def __init__(self, model_to_use: OpenAIServerModel):
        super().__init__(
            tools=[create_sale_transaction, check_item_stock],
            model=model_to_use,
            name="FulfillmentAgent",
            description="Processes validated sales and records transactions."
        )


class OrchestratorAgent(ToolCallingAgent):
    """Orchestrator agent that coordinates all worker agents and the full request pipeline."""
    def __init__(self, model_to_use: OpenAIServerModel):
        super().__init__(
            tools=[
                extract_request_items, get_catalog_item_details,
                check_inventory, check_item_stock, get_delivery_date,
                get_cash, get_financial_report,
                create_sale_transaction, create_stock_order,
                search_historical_quotes,
            ],
            model=model_to_use,
            name="OrchestratorAgent",
            description="Orchestrates the full request pipeline across worker agents."
        )


# Instantiate the 4 named agents
# (RequestExtractionWorker is the 5th agent, instantiated inside extract_request_items)
inventory_agent    = InventoryAgent(model)
quoting_agent      = QuotingAgent(model)
fulfillment_agent  = FulfillmentAgent(model)
orchestrator_agent = OrchestratorAgent(model)

# ==================== DATACLASSES ====================
@dataclass
class RequestItem:
    requested_name: str
    quantity: int


@dataclass
class QuoteLine:
    requested_name: str
    normalized_name: str
    quantity: int
    unit_price: float
    line_total: float
    in_catalog: bool
    available_stock: int
    fulfillable_qty: int
    status: str


@dataclass
class QuoteResult:
    lines: List[QuoteLine]
    subtotal: float
    discount: float
    total: float
    estimated_delivery_date: str
    historical_context: List[Dict]

# ==================== ORDER FLOW ====================
def _coerce_request_items(extracted: Dict) -> List[RequestItem]:
    """Convert raw extracted dict into a list of RequestItem dataclasses."""
    items = extracted.get("items", []) if isinstance(extracted, dict) else []
    request_items = []
    for item in items:
        try:
            requested_name = str(item.get("requested_name", "")).strip()
            quantity = int(item.get("quantity", 0))
            if requested_name and quantity > 0:
                request_items.append(RequestItem(requested_name=requested_name, quantity=quantity))
        except Exception:
            continue
    return request_items


def build_quote(request_items: List[RequestItem], agent_date: str) -> QuoteResult:
    """Build a deterministic QuoteResult from a list of RequestItems."""
    lines: List[QuoteLine] = []
    subtotal = 0.0
    max_requested_qty = 1
    search_terms = []

    for req in request_items:
        normalized = normalize_item_name(req.requested_name)
        search_terms.extend([req.requested_name.lower(), normalized.lower()])
        details = get_catalog_item_details(req.requested_name, agent_date)

        if not details["in_catalog"]:
            lines.append(QuoteLine(
                requested_name=req.requested_name, normalized_name=details["normalized_name"],
                quantity=req.quantity, unit_price=0.0, line_total=0.0,
                in_catalog=False, available_stock=0, fulfillable_qty=0,
                status="Item not available in our catalog",
            ))
            continue

        unit_price = float(details["unit_price"])
        available_stock = int(details["current_stock"])
        fulfillable_qty = min(req.quantity, available_stock)
        line_total = round(fulfillable_qty * unit_price, 2)
        subtotal += line_total
        max_requested_qty = max(max_requested_qty, req.quantity)

        if available_stock <= 0:
            status = "Currently out of stock"
        elif available_stock < req.quantity:
            status = f"Partially available ({fulfillable_qty}/{req.quantity})"
        else:
            status = "Available"

        lines.append(QuoteLine(
            requested_name=req.requested_name, normalized_name=details["normalized_name"],
            quantity=req.quantity, unit_price=unit_price, line_total=line_total,
            in_catalog=True, available_stock=available_stock,
            fulfillable_qty=fulfillable_qty, status=status,
        ))

    dedup_terms = list(dict.fromkeys([t for t in search_terms if t]))[:3]
    historical_context = search_historical_quotes(dedup_terms) if dedup_terms else []
    discount = round(subtotal * 0.10, 2) if subtotal > 500 else 0.0
    total = round(subtotal - discount, 2)
    estimated_delivery_date = get_delivery_date(agent_date, max_requested_qty)

    return QuoteResult(
        lines=lines, subtotal=round(subtotal, 2), discount=discount,
        total=total, estimated_delivery_date=estimated_delivery_date,
        historical_context=historical_context,
    )


def fulfill_quote(quote: QuoteResult, agent_date: str) -> List[Dict]:
    """Execute sale transactions for all fulfillable lines in a quote."""
    fulfillment_results = []
    for line in quote.lines:
        if not line.in_catalog:
            fulfillment_results.append({"item_name": line.requested_name,
                                         "action": "not_fulfilled",
                                         "reason": "Item not available in our catalog"})
            continue
        if line.fulfillable_qty <= 0:
            fulfillment_results.append({"item_name": line.normalized_name,
                                         "action": "not_fulfilled",
                                         "reason": "Currently out of stock"})
            continue
        tx = create_sale_transaction(
            item_name=line.normalized_name, quantity=line.fulfillable_qty, agent_date=agent_date
        )
        fulfillment_results.append({
            "item_name": line.normalized_name, "action": "fulfilled",
            "fulfilled_qty": line.fulfillable_qty, "transaction_id": tx["transaction_id"],
        })
        if line.fulfillable_qty < line.quantity:
            fulfillment_results.append({
                "item_name": line.normalized_name, "action": "partial_note",
                "reason": f"Short by {line.quantity - line.fulfillable_qty} units",
            })
    return fulfillment_results


def render_customer_response(quote: QuoteResult, fulfillment_results: List[Dict]) -> str:
    """Render a formatted customer-facing response from a quote and fulfillment result."""
    has_any_fulfilled = any(f["action"] == "fulfilled" for f in fulfillment_results)

    item_names = [line.normalized_name if line.in_catalog else line.requested_name
                  for line in quote.lines]
    subject_items = ", ".join(item_names[:3])
    if len(item_names) > 3:
        subject_items += f" and {len(item_names) - 3} more item(s)"

    lines = ["Dear Customer,", "",
             f"Thank you for your request! Here is the quote summary for {subject_items}:", ""]

    lines.append("| Item | Requested Qty | Unit Price | Line Total | Note |")
    lines.append("| --- | --- | --- | --- | --- |")

    for line in quote.lines:
        if not line.in_catalog:
            note = "Not fulfilled (Item not available in our catalog)"
            unit_price_str, line_total_str = "N/A", "N/A"
        elif line.available_stock <= 0:
            note = "Not fulfilled (Currently out of stock)"
            unit_price_str = f"${line.unit_price:.2f}"
            line_total_str = "$0.00"
        elif line.fulfillable_qty < line.quantity:
            note = f"Partially fulfilled ({line.fulfillable_qty}/{line.quantity} units shipped)"
            unit_price_str = f"${line.unit_price:.2f}"
            line_total_str = f"${line.line_total:.2f}"
        else:
            note = "Fulfilled"
            unit_price_str = f"${line.unit_price:.2f}"
            line_total_str = f"${line.line_total:.2f}"

        display_name = line.normalized_name if line.in_catalog else line.requested_name
        lines.append(f"| {display_name} | {line.quantity} | {unit_price_str} | {line_total_str} | {note} |")

    lines.append("")

    if has_any_fulfilled:
        lines.append(f"Subtotal:                ${quote.subtotal:.2f}")
        lines.append(f"Discount:                ${quote.discount:.2f}")
        lines.append(f"Total:                   ${quote.total:.2f}")
        lines.append(f"Estimated Delivery Date: {quote.estimated_delivery_date}")
        if quote.historical_context:
            lines.append("")
            lines.append("Similar Historical Quotes:")
            for h in quote.historical_context[:3]:
                amount = float(h.get("total_amount", 0.0))
                job_type = h.get("job_type", "")
                event_type = h.get("event_type", "")
                entry = f"  - Prior quote: ${amount:.2f}"
                if job_type:
                    entry += f" | Job: {job_type}"
                if event_type:
                    entry += f" | Event: {event_type}"
                lines.append(entry)
    else:
        lines.append(
            "Unfortunately, we cannot fulfill any of the items in your request "
            "as all are currently out of stock or unavailable in our catalog."
        )

    lines.extend(["", "We appreciate your business and look forward to serving you.",
                  "Best regards,", "The Paper Company Team"])
    return "\n".join(lines)


def process_request(request_text: str, agent_date: str) -> str:
    """Main entry point: extract items, build quote, fulfill, and render response."""
    try:
        extracted = extract_request_items(request_text)

        if isinstance(extracted, str):
            cleaned = extracted.strip()
            match = re.search(r'\{.*\}', cleaned, flags=re.DOTALL)
            if not match:
                return "Could not identify any valid items and quantities in the request."
            extracted = json.loads(match.group(0))

        request_items = _coerce_request_items(extracted)
        if not request_items:
            return "Could not identify any valid items and quantities in the request."

        quote = build_quote(request_items, agent_date)
        fulfillment = fulfill_quote(quote, agent_date)
        return render_customer_response(quote, fulfillment)

    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSONDecodeError in process_request: {e}")
        return "We could not parse the request details safely. Please rephrase the requested items and quantities."
    except Exception as e:
        print(f"[DEBUG] Exception in process_request: {e}")
        return f"We apologize, but we were unable to process your request at this time. Details: {e}"

# ==================== TEST SCENARIOS ====================
def run_test_scenarios():
    """Run all quote requests from quote_requests_sample.csv and save results to test_results.csv."""
    print("Initializing Database...")
    init_database()

    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        response = process_request(row["request"], request_date)

        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append({
            "request_id": idx + 1,
            "request_date": request_date,
            "cash_balance": current_cash,
            "inventory_value": current_inventory,
            "response": response,
        })

        time.sleep(1)

    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()