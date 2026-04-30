"""
Agent Workflow Diagram Generator
Creates a visual architecture diagram for the Beaver's Choice Paper Company multi-agent system
using NetworkX and matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

def create_agent_workflow_diagram():
    # Create directed graph
    G = nx.DiGraph()

    # Define node categories with styling
    node_styles = {
        'customer': {'color': '#FFB6C1', 'shape': 's'},      # Pink square
        'orchestrator': {'color': '#87CEEB', 'shape': 'o'}, # Sky blue circle
        'agent': {'color': '#98FB98', 'shape': 'o'},        # Pale green circle
        'database': {'color': '#DDA0DD', 'shape': 'd'},     # Plum diamond
        'external': {'color': '#F0E68C', 'shape': 's'},     # Khaki square
    }

    # =========================================================================
    # ADD NODES - External/Customer Layer
    # =========================================================================
    G.add_node("Customer\nRequest", category='customer')

    # =========================================================================
    # ADD NODES - Orchestrator
    # =========================================================================
    G.add_node("Orchestrator\nAgent", category='orchestrator',
               description="Receives customer requests\nDelegates tasks to workers\nSynthesizes final response")

    # =========================================================================
    # ADD NODES - Worker Agents
    # =========================================================================
    G.add_node("Inventory\nAgent", category='agent',
               description="check_stock()\nget_all_inventory()\nget_stock_level()\nassess_restock_needs()")

    G.add_node("Quoting\nAgent", category='agent',
               description="generate_quote()\nsearch_quote_history()\napply_discounts()\nget_supplier_delivery_date()")

    G.add_node("Order\nFulfillment", category='agent',
               description="process_order()\ncreate_transaction()\nupdate_inventory()\ngenerate_financial_report()")

    # =========================================================================
    # ADD NODES - Database Layer
    # =========================================================================
    G.add_node("SQLite DB\n(Transactions)", category='database')
    G.add_node("SQLite DB\n(Inventory)", category='database')
    G.add_node("SQLite DB\n(Quotes)", category='database')
    G.add_node("SQLite DB\n(Quote Requests)", category='database')

    # =========================================================================
    # ADD NODES - External Services
    # =========================================================================
    G.add_node("Supplier\nSystem", category='external')
    G.add_node("LLM\n(GPT-4)", category='external')

    # =========================================================================
    # ADD EDGES - Data Flow with Labels
    # =========================================================================

    # Customer to Orchestrator
    G.add_edge("Customer\nRequest", "Orchestrator\nAgent",
               label="1. Customer Inquiry\n    (text request)",
               color='#8B4513', style='solid')

    # Orchestrator to LLM
    G.add_edge("Orchestrator\nAgent", "LLM\n(GPT-4)",
               label="2. Analyze intent\n    Extract items/needs",
               color='#4A90D9', style='dashed')

    # LLM to Orchestrator
    G.add_edge("LLM\n(GPT-4)", "Orchestrator\nAgent",
               label="3. Parsed request\n    (structured data)",
               color='#4A90D9', style='dashed')

    # Orchestrator to Inventory Agent
    G.add_edge("Orchestrator\nAgent", "Inventory\nAgent",
               label="4a. Check stock for\n    requested items",
               color='#2E8B57', style='solid')

    # Inventory Agent to Inventory DB
    G.add_edge("Inventory\nAgent", "SQLite DB\n(Inventory)",
               label="get_all_inventory()\nget_stock_level()",
               color='#9370DB', style='dotted')

    # Inventory DB to Inventory Agent
    G.add_edge("SQLite DB\n(Inventory)", "Inventory\nAgent",
               label="Current stock levels",
               color='#9370DB', style='dotted')

    # Orchestrator to Quoting Agent
    G.add_edge("Orchestrator\nAgent", "Quoting\nAgent",
               label="4b. Generate quote\n    for request",
               color='#2E8B57', style='solid')

    # Quoting Agent to Quotes DB
    G.add_edge("Quoting\nAgent", "SQLite DB\n(Quotes)",
               label="search_quote_history()",
               color='#9370DB', style='dotted')

    # Quotes DB to Quoting Agent
    G.add_edge("SQLite DB\n(Quotes)", "Quoting\nAgent",
               label="Historical pricing",
               color='#9370DB', style='dotted')

    # Quoting Agent to Supplier System
    G.add_edge("Quoting\nAgent", "Supplier\nSystem",
               label="get_supplier_delivery_date()",
               color='#FF8C00', style='dashed')

    # Supplier System to Quoting Agent
    G.add_edge("Supplier\nSystem", "Quoting\nAgent",
               label="Delivery timeline",
               color='#FF8C00', style='dashed')

    # Orchestrator to Order Fulfillment
    G.add_edge("Orchestrator\nAgent", "Order\nFulfillment",
               label="4c. Process order\n    if stock available",
               color='#2E8B57', style='solid')

    # Order Fulfillment to Transactions DB
    G.add_edge("Order\nFulfillment", "SQLite DB\n(Transactions)",
               label="create_transaction()",
               color='#9370DB', style='dotted')

    # Order Fulfillment to Inventory DB
    G.add_edge("Order\nFulfillment", "SQLite DB\n(Inventory)",
               label="Update stock levels",
               color='#9370DB', style='dotted')

    # Order Fulfillment to Cash Balance
    G.add_edge("Order\nFulfillment", "Cash\nBalance",
               label="get_cash_balance()\ngenerate_financial_report()",
               color='#9370DB', style='dotted')

    # Cash Balance node
    G.add_node("Cash\nBalance", category='database')

    # Quote Requests DB to Quoting Agent
    G.add_edge("SQLite DB\n(Quote Requests)", "Quoting\nAgent",
               label="Reference previous\nsimilar requests",
               color='#9370DB', style='dotted')

    # Order Fulfillment to Orchestrator
    G.add_edge("Order\nFulfillment", "Orchestrator\nAgent",
               label="5. Order confirmation\n    or rejection reason",
               color='#2E8B57', style='solid')

    # Orchestrator to Customer
    G.add_edge("Orchestrator\nAgent", "Customer\nRequest",
               label="6. Final response\n    (quote/fulfillment)",
               color='#8B4513', style='solid')

    # =========================================================================
    # CREATE THE VISUALIZATION
    # =========================================================================

    # Use Graphviz layout if available, otherwise use spring layout
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except:
        # Manual positioned layout for better control
        pos = {
            "Customer\nRequest": (0, 4),
            "Orchestrator\nAgent": (3, 4),
            "LLM\n(GPT-4)": (6, 5),
            "Inventory\nAgent": (1, 2),
            "Quoting\nAgent": (3, 2),
            "Order\nFulfillment": (5, 2),
            "SQLite DB\n(Inventory)": (1, 0),
            "SQLite DB\n(Quotes)": (3, 0),
            "SQLite DB\n(Transactions)": (5, 0),
            "SQLite DB\n(Quote Requests)": (7, 0),
            "Supplier\nSystem": (7, 2),
            "Cash\nBalance": (5, -1),
        }

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    fig.patch.set_facecolor('#FAFAFA')

    # Draw nodes by category
    categories = ['customer', 'orchestrator', 'agent', 'database', 'external']
    colors = {
        'customer': '#FFB6C1',
        'orchestrator': '#87CEEB',
        'agent': '#90EE90',
        'database': '#DDA0DD',
        'external': '#F0E68C'
    }

    for category in categories:
        nodes = [n for n, d in G.nodes(data=True) if d.get('category') == category]
        if nodes:
            nx.draw_networkx_nodes(G, pos,
                                   nodelist=nodes,
                                   node_color=colors[category],
                                   node_size=4500,
                                   alpha=0.9,
                                   ax=ax)

    # Draw edges
    edge_colors = [G.edges[e]['color'] if 'color' in G.edges[e] else '#333333'
                   for e in G.edges()]
    edge_styles = [G.edges[e]['style'] if 'style' in G.edges[e] else 'solid'
                   for e in G.edges()]

    # Convert styles for matplotlib
    nx.draw_networkx_edges(G, pos,
                           edge_color='#555555',
                           arrows=True,
                           arrowsize=20,
                           connectionstyle="arc3,rad=0.1",
                           width=1.5,
                           alpha=0.7,
                           ax=ax)

    # Draw node labels
    label_pos = {k: (v[0], v[1] + 0.15) for k, v in pos.items()}
    nx.draw_networkx_labels(G, pos,
                            font_size=9,
                            font_weight='bold',
                            font_color='#1a1a1a',
                            ax=ax)

    # Draw edge labels
    edge_labels = {(u, v): G.edges[u, v].get('label', '')
                   for u, v in G.edges() if 'label' in G.edges[u, v]}

    # Offset edge labels
    nx.draw_networkx_edge_labels(G, pos,
                                 edge_labels=edge_labels,
                                 font_size=7,
                                 font_color='#333333',
                                 bbox=dict(boxstyle='round,pad=0.2',
                                           facecolor='white',
                                           edgecolor='none',
                                           alpha=0.8),
                                 ax=ax)

    # Add title
    ax.set_title("Beaver's Choice Paper Company\nMulti-Agent System Architecture",
                 fontsize=16, fontweight='bold', pad=20)

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='#FFB6C1', edgecolor='black', label='Customer'),
        mpatches.Patch(facecolor='#87CEEB', edgecolor='black', label='Orchestrator Agent'),
        mpatches.Patch(facecolor='#90EE90', edgecolor='black', label='Worker Agents'),
        mpatches.Patch(facecolor='#DDA0DD', edgecolor='black', label='Database Layer'),
        mpatches.Patch(facecolor='#F0E68C', edgecolor='black', label='External Services'),
    ]
    ax.legend(handles=legend_elements,
              loc='upper left',
              fontsize=9,
              framealpha=0.9,
              title='Component Types',
              title_fontsize=10)

    # Add flow number annotations
    flow_notes = [
        (1.5, 4.4, "① Customer sends text request"),
        (4.2, 4.6, "② Orchestrator analyzes via LLM"),
        (0.8, 3.0, "④a Inventory check"),
        (2.8, 3.0, "④b Quote generation"),
        (4.6, 3.0, "④c Order fulfillment"),
        (2.5, 1.8, "⑤ Results returned to orchestrator"),
        (1.5, 4.7, "⑥ Final response to customer"),
    ]

    for x, y, text in flow_notes:
        ax.annotate(text, xy=(x, y), fontsize=8,
                    style='italic', color='#444444',
                    bbox=dict(boxstyle='round,pad=0.3',
                              facecolor='#ffffcc',
                              edgecolor='gray',
                              alpha=0.8))

    # Remove axes
    ax.axis('off')

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    output_path = "agent_workflow_diagram.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Diagram saved to: {output_path}")

    # Also create a detailed text-based diagram
    create_text_diagram()

    plt.show()

    return G

def create_text_diagram():
    """Generate a detailed text-based architecture document."""

    text_diagram = """
================================================================================
        BEAVER'S CHOICE PAPER COMPANY - MULTI-AGENT SYSTEM ARCHITECTURE
================================================================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CUSTOMER LAYER                                   │
│  ┌─────────────────┐                                                         │
│  │  Customer Req   │ ←── Text-based inquiry (e.g., "I need 500 sheets...")   │
│  └────────┬────────┘                                                         │
└───────────┼─────────────────────────────────────────────────────────────────┘
            │
            │ ① Customer Inquiry
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATOR AGENT                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Responsibilities:                                                   │  │
│  │  • Receive and parse customer requests                                  │  │
│  │  • Delegate tasks to appropriate worker agents                          │  │
│  │  • Coordinate data flow between agents                                  │  │
│  │  • Synthesize final response to customer                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│           │                    │                    │                         │
│           │ ④a Check Stock    │ ④b Generate Quote  │ ④c Process Order      │
│           ▼                    ▼                    ▼                        │
└───────────┼────────────────────┼────────────────────┼─────────────────────────┘
            │                    │                    │
┌───────────┼────────────────────┼────────────────────┼─────────────────────────┐
│           │      WORKER AGENTS │                    │                         │
│           │                    │                    │                         │
│  ┌────────┴───────┐  ┌─────────┴───────┐  ┌────────┴───────┐                 │
│  │ INVENTORY     │  │ QUOTING         │  │ ORDER           │                 │
│  │ AGENT         │  │ AGENT           │  │ FULFILLMENT     │                 │
│  ├───────────────┤  ├─────────────────┤  ├─────────────────┤                 │
│  │ Tools:        │  │ Tools:          │  │ Tools:          │                 │
│  │ • check_stock │  │ • generate_quote│  │ • process_order │                 │
│  │ • get_all_    │  │ • search_       │  │ • create_       │                 │
│  │   inventory   │  │   quote_history │  │   transaction   │                 │
│  │ • get_stock   │  │ • apply_        │  │ • update_       │                 │
│  │   _level      │  │   discounts     │  │   inventory     │                 │
│  │ • assess_     │  │ • get_supplier_ │  │ • generate_     │                 │
│  │   restock     │  │   delivery_date │  │   financial_    │                 │
│  └───────┬───────┘  └────────┬────────┘  │   report       │                 │
│          │                   │            └────────┬───────┘                 │
│          └───────────────────┼────────────────────┘                          │
│                              │                                               │
│                              ▼                                               │
└──────────────────────────────┼────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼────────────────────────────────────────────────┐
│                         DATABASE LAYER                                        │
│                                                                               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│   │  Inventory   │  │   Quotes     │  │ Transactions │  │Quote Requests│       │
│   ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤       │
│   │ current_stock│  │ total_amount│  │ stock_orders│  │   response   │       │
│   │ min_stock    │  │ quote_      │  │ sales        │  │    job       │       │
│   │ unit_price   │  │ explanation │  │ units        │  │   event      │       │
│   │ category     │  │ job_type    │  │ price        │  │              │       │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                               │
│         ▲                 ▲                  ▲                  ▲              │
│         │                 │                  │                  │              │
│   get_stock_level   search_quote    create_transaction  reference            │
│   get_all_inventory history        generate_financial     data                │
│                              _report                                          │
└────────────────────────────────────────────────────────────────────────────────┘
                               │
┌───────────────────────────────┼────────────────────────────────────────────────┐
│                               │    EXTERNAL SERVICES                           │
│                               ▼                                                 │
│                    ┌──────────────────────┐                                    │
│                    │   Supplier System    │  ← get_supplier_delivery_date()    │
│                    │  Delivery lead time:  │    ≤10: same day                   │
│                    │  • 1-10 units: 0d    │    11-100: 1 day                   │
│                    │  • 11-100 units: 1d   │    101-1000: 4 days                │
│                    │  • 101-1000 units: 4d │    >1000: 7 days                  │
│                    │  • >1000 units: 7d    │                                    │
│                    └──────────────────────┘                                    │
│                                                                                │
│                    ┌──────────────────────┐                                    │
│                    │   LLM (GPT-4)        │  ← Intent analysis, text generation │
│                    │   OpenAI API         │    Customer request parsing        │
│                    └──────────────────────┘    Response synthesis             │
└─────────────────────────────────────────────────────────────────────────────────┘

================================================================================
                              DATA FLOW SEQUENCE
================================================================================

Step 1: Customer sends text-based request
         ↓
Step 2: Orchestrator receives request → sends to LLM for intent analysis
         ↓
Step 3: LLM returns parsed request (items, quantities, event type, etc.)
         ↓
Step 4a: Orchestrator delegates to INVENTORY AGENT
         → Checks stock levels via get_all_inventory(), get_stock_level()
         → Assesses if restocking is needed
         ↓
Step 4b: Orchestrator delegates to QUOTING AGENT
         → Searches historical quotes via search_quote_history()
         → Calculates pricing with bulk discounts
         → Checks delivery timeline via get_supplier_delivery_date()
         ↓
Step 4c: If stock available, delegates to ORDER FULFILLMENT
         → Creates transaction via create_transaction()
         → Updates inventory
         → Generates financial report via generate_financial_report()
         ↓
Step 5: Worker agents return results to Orchestrator
         ↓
Step 6: Orchestrator synthesizes final response → Customer

================================================================================
                           HELPER FUNCTIONS MAPPING
================================================================================

┌─────────────────────────────┬───────────────────────────────────────────────┐
│       Helper Function       │              Usage in Agents                   │
├─────────────────────────────┼───────────────────────────────────────────────┤
│ init_database()             │ Initialize DB with inventory & quotes         │
│ get_all_inventory(date)     │ Inventory Agent: Get all stock levels         │
│ get_stock_level(item, date) │ Inventory Agent: Check specific item stock     │
│ get_cash_balance(date)      │ Fulfillment Agent: Verify payment capacity    │
│ get_supplier_delivery_date() │ Quoting Agent: Estimate delivery lead time   │
│ search_quote_history(terms) │ Quoting Agent: Find similar historical quotes │
│ create_transaction(...)     │ Fulfillment Agent: Record sales/stock orders │
│ generate_financial_report()  │ Fulfillment Agent: Report final state         │
└─────────────────────────────┴───────────────────────────────────────────────┘

================================================================================
                           CONSTRAINTS & REQUIREMENTS
================================================================================

• Maximum 5 agents total (1 orchestrator + 4 workers maximum)
• All communication must be text-based
• Must use smolagents, pydantic-ai, or npcsh framework
• All 7 helper functions must be utilized in at least one tool
• Quotes must include bulk discounts
• Exact item names from paper_supplies must be used
• Dates must be included in inter-agent communication

================================================================================
"""

    with open("agent_architecture_diagram.txt", "w", encoding="utf-8") as f:
        f.write(text_diagram)

    print("Text diagram saved to: agent_architecture_diagram.txt")
    print(text_diagram)


def create_agent_roles_summary():
    """Create a summary document of agent roles and responsibilities."""

    summary = """
================================================================================
                    AGENT ROLES AND RESPONSIBILITIES
================================================================================

1. ORCHESTRATOR AGENT
   ────────────────────
   Primary Role: Central coordinator and task dispatcher

   Responsibilities:
   • Receive customer text requests
   • Parse and interpret customer intent (via LLM)
   • Determine which worker agents need to be invoked
   • Coordinate parallel and sequential agent execution
   • Aggregate results from worker agents
   • Generate final customer-facing response

   Input: Customer text request (with date)
   Output: Synthesized response (quote confirmation, order status, etc.)


2. INVENTORY AGENT
   ─────────────────
   Primary Role: Stock management and restocking decisions

   Tools:
   • get_all_inventory(date) → Dict of {item: stock_level}
   • get_stock_level(item_name, date) → DataFrame with current_stock
   • check_availability(requested_items) → Availability report
   • assess_restock_needs(stock_levels) → Reorder recommendations

   Responsibilities:
   • Query current inventory levels from SQLite database
   • Determine if requested items are in stock
   • Identify items below minimum stock threshold
   • Recommend restocking quantities
   • Flag items that cannot be fulfilled

   Input: List of requested items and quantities
   Output: Stock availability report with quantities


3. QUOTING AGENT
   ───────────────
   Primary Role: Price generation with strategic discounting

   Tools:
   • search_quote_history(search_terms, limit) → Historical quotes
   • calculate_price(item, quantity, unit_price) → Line item cost
   • apply_bulk_discount(subtotal, quantity) → Discounted price
   • get_supplier_delivery_date(request_date, quantity) → Delivery date

   Responsibilities:
   • Search historical quotes for similar requests
   • Calculate base pricing from unit prices
   • Apply bulk discounts strategically (10-20% typical)
   • Estimate delivery dates based on quantity
   • Generate itemized quote with explanation

   Input: Customer request with items, quantities, event type
   Output: Detailed quote with pricing and delivery timeline


4. ORDER FULFILLMENT AGENT
   ─────────────────────────
   Primary Role: Transaction processing and inventory updates

   Tools:
   • create_transaction(item_name, type, qty, price, date) → Transaction ID
   • get_cash_balance(date) → Current cash float
   • generate_financial_report(date) → Full financial summary
   • validate_order(inventory_check, cash_check) → Validation result

   Responsibilities:
   • Validate order against inventory and cash constraints
   • Create sales transaction records
   • Update inventory (decrement stock)
   • Process payment/cash operations
   • Generate financial reports
   • Handle order rejections with reasons

   Input: Approved quote, inventory validation result
   Output: Transaction confirmation, updated financial state


================================================================================
                         DATA DEPENDENCIES MATRIX
================================================================================

                    ┌─────────────┬─────────────┬─────────────┬─────────────┐
                    │ Orchestrator│  Inventory  │   Quoting   │  Fulfillment│
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Customer Req    │     ←←←     │             │             │             │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Inventory DB    │             │    ←←←      │      →      │      →      │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Quotes DB       │             │             │     ←←←     │             │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Transactions    │             │             │             │     ←←←     │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Quote Requests  │             │             │      →      │             │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Supplier API    │             │             │     ←→      │             │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    LLM (GPT-4)     │     ←→      │             │             │             │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
    Cash Balance    │             │             │             │     ←←←     │
    ────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤

    ←←← = Primary data source/consumer
    → = Reads from / writes to

================================================================================
"""

    with open("agent_roles_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print("Agent roles summary saved to: agent_roles_summary.txt")


if __name__ == "__main__":
    print("Generating Multi-Agent System Architecture Diagram...")
    print("=" * 60)

    # Create the visual diagram
    graph = create_agent_workflow_diagram()

    # Create text-based diagrams
    create_text_diagram()

    # Create agent roles summary
    create_agent_roles_summary()

    print("=" * 60)
    print("All diagrams generated successfully!")
    print("\nGenerated files:")
    print("  1. agent_workflow_diagram.png - Visual architecture diagram")
    print("  2. agent_architecture_diagram.txt - ASCII text diagram")
    print("  3. agent_roles_summary.txt - Detailed agent responsibilities")