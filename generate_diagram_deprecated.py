"""
Agent Workflow Diagram Generator
Creates a visual architecture diagram for the Beaver's Choice Paper Company multi-agent system
using NetworkX and matplotlib.

Fixed issues:
- Arrows now properly connect to node boundaries
- Edge labels positioned to avoid overlapping
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import networkx as nx
import numpy as np

def create_agent_workflow_diagram():
    # Create directed graph
    G = nx.DiGraph()

    # Define node categories with styling
    node_styles = {
        'customer': {'color': '#FFB6C1', 'shape': 's'},
        'orchestrator': {'color': '#87CEEB', 'shape': 'o'},
        'agent': {'color': '#98FB98', 'shape': 'o'},
        'database': {'color': '#DDA0DD', 'shape': 'd'},
        'external': {'color': '#F0E68C', 'shape': 's'},
    }

    # =========================================================================
    # ADD NODES
    # =========================================================================

    # External/Customer Layer
    G.add_node("Customer\nRequest", category='customer', layer=0)

    # Orchestrator Layer
    G.add_node("Orchestrator\nAgent", category='orchestrator', layer=1,
               description="Receives customer requests\nDelegates tasks to workers\nSynthesizes final response")

    # Worker Agents Layer
    G.add_node("Inventory\nAgent", category='agent', layer=2,
               description="check_stock()\nget_all_inventory()\nget_stock_level()")
    G.add_node("Quoting\nAgent", category='agent', layer=2,
               description="generate_quote()\nsearch_quote_history()")
    G.add_node("Order\nFulfillment", category='agent', layer=2,
               description="process_order()\ncreate_transaction()")

    # Database Layer
    G.add_node("Transactions\nDB", category='database', layer=3)
    G.add_node("Inventory\nDB", category='database', layer=3)
    G.add_node("Quotes\nDB", category='database', layer=3)
    G.add_node("Quote\nRequests DB", category='database', layer=3)

    # External Services
    G.add_node("LLM\n(GPT-4)", category='external', layer=4)
    G.add_node("Supplier\nSystem", category='external', layer=4)

    # =========================================================================
    # DEFINE CUSTOM POSITIONS - Clean layered layout
    # =========================================================================

    # Layer-based positions with proper spacing
    pos = {
        # Layer 0: Customer
        "Customer\nRequest": (4, 6),

        # Layer 1: Orchestrator
        "Orchestrator\nAgent": (4, 4.5),

        # Layer 2: Worker Agents
        "Inventory\nAgent": (1.5, 2.5),
        "Quoting\nAgent": (4, 2.5),
        "Order\nFulfillment": (6.5, 2.5),

        # Layer 3: Databases
        "Transactions\nDB": (6.5, 0.5),
        "Inventory\nDB": (4, 0.5),
        "Quotes\nDB": (1.5, 0.5),
        "Quote\nRequests DB": (-1.5, 0.5),

        # Layer 4: External Services
        "LLM\n(GPT-4)": (7, 4.5),
        "Supplier\nSystem": (7, 2.5),
    }

    # =========================================================================
    # ADD EDGES - Organized by flow type
    # =========================================================================

    # Main flow edges (solid, thick) - Customer → Orchestrator → Workers
    main_flow = [
        ("Customer\nRequest", "Orchestrator\nAgent", "① Customer Inquiry"),
        ("Orchestrator\nAgent", "Inventory\nAgent", "④a Check Stock"),
        ("Orchestrator\nAgent", "Quoting\nAgent", "④b Generate Quote"),
        ("Orchestrator\nAgent", "Order\nFulfillment", "④c Process Order"),
        ("Order\nFulfillment", "Orchestrator\nAgent", "⑤ Results Return"),
        ("Orchestrator\nAgent", "Customer\nRequest", "⑥ Final Response"),
    ]

    # LLM interaction edges (dashed)
    llm_flow = [
        ("Orchestrator\nAgent", "LLM\n(GPT-4)", "② Analyze Intent"),
        ("LLM\n(GPT-4)", "Orchestrator\nAgent", "③ Parsed Data"),
    ]

    # Database edges (dotted)
    db_flow = [
        ("Inventory\nAgent", "Inventory\nDB", "get_stock_level()"),
        ("Inventory\nDB", "Inventory\nAgent", "stock levels"),
        ("Quoting\nAgent", "Quotes\nDB", "search_quote_history()"),
        ("Quotes\nDB", "Quoting\nAgent", "historical pricing"),
        ("Quote\nRequests DB", "Quoting\nAgent", "reference similar"),
        ("Order\nFulfillment", "Transactions\nDB", "create_transaction()"),
        ("Transactions\nDB", "Order\nFulfillment", "confirm sale"),
        ("Order\nFulfillment", "Inventory\nDB", "update stock"),
    ]

    # Supplier edges
    supplier_flow = [
        ("Quoting\nAgent", "Supplier\nSystem", "check delivery"),
        ("Supplier\nSystem", "Quoting\nAgent", "timeline"),
    ]

    # Add all edges with attributes
    for u, v, label in main_flow:
        G.add_edge(u, v, label=label, flow_type='main')

    for u, v, label in llm_flow:
        G.add_edge(u, v, label=label, flow_type='llm')

    for u, v, label in db_flow:
        G.add_edge(u, v, label=label, flow_type='db')

    for u, v, label in supplier_flow:
        G.add_edge(u, v, label=label, flow_type='supplier')

    # =========================================================================
    # CREATE THE VISUALIZATION
    # =========================================================================

    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    # Node colors
    colors = {
        'customer': '#FFB6C1',
        'orchestrator': '#87CEEB',
        'agent': '#90EE90',
        'database': '#DDA0DD',
        'external': '#F0E68C'
    }

    # Node sizes
    node_sizes = {
        'customer': 4000,
        'orchestrator': 5000,
        'agent': 4500,
        'database': 3500,
        'external': 3500
    }

    # Draw nodes by category
    for category in colors.keys():
        nodes = [n for n, d in G.nodes(data=True) if d.get('category') == category]
        if nodes:
            nx.draw_networkx_nodes(G, pos,
                                   nodelist=nodes,
                                   node_color=colors[category],
                                   node_size=node_sizes[category],
                                   alpha=0.95,
                                   ax=ax,
                                   node_shape='o',
                                   edgecolors='black',
                                   linewidths=2)

    # Draw edges by type with different styles
    edge_configs = {
        'main': {'color': '#2E8B57', 'style': 'solid', 'width': 2.5},
        'llm': {'color': '#4169E1', 'style': 'dashed', 'width': 1.8},
        'db': {'color': '#9370DB', 'style': 'dotted', 'width': 1.2},
        'supplier': {'color': '#FF8C00', 'style': 'dashed', 'width': 1.5},
    }

    # Draw all edges
    for flow_type, config in edge_configs.items():
        edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('flow_type') == flow_type]
        if edges:
            nx.draw_networkx_edges(G, pos,
                                   edgelist=edges,
                                   edge_color=config['color'],
                                   width=config['width'],
                                   alpha=0.8,
                                   ax=ax,
                                   arrows=True,
                                   arrowsize=25,
                                   arrowstyle='-|>',
                                   connectionstyle="arc3,rad=0.0",
                                   min_source_margin=35,
                                   min_target_margin=35)

    # Draw node labels with better positioning
    node_labels = {node: node.replace('\n', '\n') for node in G.nodes()}
    nx.draw_networkx_labels(G, pos,
                            labels=node_labels,
                            font_size=9,
                            font_weight='bold',
                            font_color='#1a1a1a',
                            ax=ax)

    # Draw edge labels with smart positioning
    # Group labels by position to avoid overlap
    for u, v, data in G.edges(data=True):
        label = data.get('label', '')
        x = (pos[u][0] + pos[v][0]) / 2
        y = (pos[u][1] + pos[v][1]) / 2

        # Adjust label position based on edge direction
        dx = pos[v][0] - pos[u][0]
        dy = pos[v][1] - pos[u][1]

        # Offset perpendicular to the edge
        if abs(dx) > abs(dy):  # More horizontal
            offset_y = 0.25 if dy >= 0 else -0.25
            ha = 'center'
        else:  # More vertical
            offset_x = 0.3 if dx >= 0 else -0.3
            ha = 'left' if dx < 0 else 'right'

        # Apply offset
        if abs(dx) > abs(dy):
            label_x = x
            label_y = y + offset_y
        else:
            label_x = x + (0.3 if dx >= 0 else -0.3)
            label_y = y

        ax.annotate(label,
                   xy=(x, y),
                   xytext=(label_x, label_y),
                   fontsize=7,
                   color='#333333',
                   ha='center',
                   va='center',
                   bbox=dict(boxstyle='round,pad=0.15',
                            facecolor='white',
                            edgecolor='#CCCCCC',
                            alpha=0.9))

    # Add layer labels on the left
    layer_labels = [
        (6, "Customer Layer"),
        (4.5, "Orchestrator"),
        (2.5, "Worker Agents"),
        (0.5, "Database Layer"),
        (3.5, "External Services"),
    ]

    for y, label in layer_labels:
        ax.annotate(label,
                   xy=(-3, y),
                   fontsize=10,
                   fontweight='bold',
                   color='#555555',
                   ha='right',
                   va='center',
                   bbox=dict(boxstyle='round,pad=0.3',
                            facecolor='#E8E8E8',
                            edgecolor='none'))

    # Add title
    ax.set_title("Beaver's Choice Paper Company - Multi-Agent System Architecture",
                 fontsize=18, fontweight='bold', pad=25, color='#1a1a1a')

    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor='#FFB6C1', edgecolor='black', label='Customer'),
        mpatches.Patch(facecolor='#87CEEB', edgecolor='black', label='Orchestrator Agent'),
        mpatches.Patch(facecolor='#90EE90', edgecolor='black', label='Worker Agents'),
        mpatches.Patch(facecolor='#DDA0DD', edgecolor='black', label='Database Layer'),
        mpatches.Patch(facecolor='#F0E68C', edgecolor='black', label='External Services'),
    ]

    # Add flow type legend
    flow_legend = [
        mlines.Line2D([], [], color='#2E8B57', linewidth=2.5, label='Main Flow (Solid)'),
        mlines.Line2D([], [], color='#4169E1', linewidth=1.8, linestyle='dashed', label='LLM Interaction'),
        mlines.Line2D([], [], color='#9370DB', linewidth=1.2, linestyle='dotted', label='Database Access'),
        mlines.Line2D([], [], color='#FF8C00', linewidth=1.5, linestyle='dashed', label='Supplier API'),
    ]

    # First legend (node types)
    legend1 = ax.legend(handles=legend_elements,
                       loc='upper left',
                       fontsize=9,
                       framealpha=0.95,
                       title='Component Types',
                       title_fontsize=10,
                       bbox_to_anchor=(0.01, 0.99))
    ax.add_artist(legend1)

    # Second legend (flow types)
    ax.legend(handles=flow_legend,
              loc='upper left',
              fontsize=8,
              framealpha=0.95,
              title='Data Flow Types',
              title_fontsize=10,
              bbox_to_anchor=(0.01, 0.75))

    # Add step annotations on the right side
    steps = [
        (5.5, "Step 1: Customer sends text request"),
        (3.5, "Step 2: Orchestrator analyzes via LLM"),
        (3.0, "Step 4: Delegates to worker agents"),
        (5.0, "Step 5: Aggregate results"),
        (5.0, "Step 6: Return final response"),
    ]

    for dy, text in steps:
        ax.annotate(text,
                   xy=(8.5, dy),
                   fontsize=8,
                   style='italic',
                   color='#666666',
                   ha='left',
                   va='center',
                   bbox=dict(boxstyle='round,pad=0.2',
                            facecolor='#FFFACD',
                            edgecolor='#DDD',
                            alpha=0.9))

    # Remove axes
    ax.axis('off')

    # Set axis limits with padding
    ax.set_xlim(-5, 9.5)
    ax.set_ylim(-1, 7.5)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    output_path = "agent_workflow_diagram.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Diagram saved to: {output_path}")

    # Generate text diagram
    create_text_diagram()

    return G


def create_text_diagram():
    """Generate a detailed text-based architecture document."""

    text_diagram = """
================================================================================
        BEAVER'S CHOICE PAPER COMPANY - MULTI-AGENT SYSTEM ARCHITECTURE
================================================================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CUSTOMER LAYER                                  │
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
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│   │  Inventory   │  │   Quotes     │  │ Transactions │  │Quote Requests│    │
│   ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤    │
│   │ current_stock│  │ total_amount │  │ stock_orders │  │   response   │    │
│   │ min_stock    │  │ quote_       │  │ sales        │  │    job       │    │
│   │ unit_price   │  │ explanation  │  │ units        │  │   event      │    │
│   │ category     │  │ job_type     │  │ price        │  │              │    │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                               │
│         ▲                 ▲                  ▲                  ▲             │
│         │                 │                  │                  │             │
│   get_stock_level  search_quote    create_transaction  reference            │
│   get_all_inventory history       generate_financial     data                │
│                              _report                                          │
└────────────────────────────────────────────────────────────────────────────────┘
                               │
┌───────────────────────────────┼────────────────────────────────────────────────┐
│                               │    EXTERNAL SERVICES                           │
│                               ▼                                                 │
│                    ┌──────────────────────┐                                    │
│                    │   Supplier System    │  ← get_supplier_delivery_date()     │
│                    │  Delivery lead time: │    ≤10: same day                     │
│                    │  • 1-10 units: 0d    │    11-100: 1 day                    │
│                    │  • 11-100 units: 1d  │    101-1000: 4 days                 │
│                    │  • 101-1000 units: 4d │    >1000: 7 days                   │
│                    │  • >1000 units: 7d   │                                    │
│                    └──────────────────────┘                                    │
│                                                                                │
│                    ┌──────────────────────┐                                    │
│                    │   LLM (GPT-4)        │  ← Intent analysis, text gen      │
│                    │   OpenAI API         │    Customer request parsing         │
│                    └──────────────────────┘    Response synthesis              │
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

┌────────────────────────────┬─────────────────────────────────────────────────┐
│       Helper Function      │              Usage in Agents                    │
├────────────────────────────┼─────────────────────────────────────────────────┤
│ init_database()            │ Initialize DB with inventory & quotes          │
│ get_all_inventory(date)    │ Inventory Agent: Get all stock levels          │
│ get_stock_level(item, date)│ Inventory Agent: Check specific item stock      │
│ get_cash_balance(date)     │ Fulfillment Agent: Verify payment capacity   │
│ get_supplier_delivery_date()│ Quoting Agent: Estimate delivery lead time   │
│ search_quote_history(terms)│ Quoting Agent: Find similar historical quotes │
│ create_transaction(...)    │ Fulfillment Agent: Record sales/stock orders │
│ generate_financial_report()│ Fulfillment Agent: Report final state         │
└────────────────────────────┴─────────────────────────────────────────────────┘

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