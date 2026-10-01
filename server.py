import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from db_manager import db

app = Flask(__name__, static_folder="static", template_folder="templates")

# ==============================================================================
# PRESET BUSINESS SQL QUERIES (FOR 1-CLICK QUERY RUNNER)
# ==============================================================================
PRESET_QUERIES = [
    {
        "id": "exec_summary",
        "title": "1. Executive Sales & Revenue Overview",
        "category": "Sales & Revenue",
        "sql": """SELECT 
    COUNT(DISTINCT o.OrderID) AS total_orders,
    COALESCE(SUM(o.GrandTotal), 0) AS total_revenue_usd,
    ROUND(AVG(o.GrandTotal), 2) AS average_order_value,
    COALESCE(SUM(o.DiscountAmount), 0) AS total_discounts_granted,
    COUNT(DISTINCT o.CustomerID) AS active_purchasing_customers
FROM Orders o
WHERE o.OrderStatus != 'Cancelled';"""
    },
    {
        "id": "category_sales",
        "title": "2. Sales Breakdown by Product Category",
        "category": "Sales & Revenue",
        "sql": """SELECT 
    c.CategoryName,
    COUNT(DISTINCT p.ProductID) AS unique_products,
    SUM(od.Quantity) AS units_sold,
    ROUND(SUM(od.TotalPrice), 2) AS category_revenue
FROM Categories c
JOIN Products p ON c.CategoryID = p.CategoryID
JOIN ProductVariants pv ON p.ProductID = pv.ProductID
JOIN OrderDetails od ON pv.VariantID = od.VariantID
GROUP BY c.CategoryID, c.CategoryName
ORDER BY category_revenue DESC;"""
    },
    {
        "id": "top_products",
        "title": "3. Top Selling Products & Profit Margins",
        "category": "Products & Margin",
        "sql": """SELECT 
    p.ProductName,
    c.CategoryName,
    p.BasePrice AS unit_cost,
    p.SellingPrice AS retail_price,
    ROUND(((p.SellingPrice - p.BasePrice) / p.SellingPrice) * 100.0, 2) AS margin_pct,
    SUM(od.Quantity) AS units_sold,
    ROUND(SUM(od.TotalPrice), 2) AS total_sales
FROM Products p
JOIN Categories c ON p.CategoryID = c.CategoryID
JOIN ProductVariants pv ON p.ProductID = pv.ProductID
JOIN OrderDetails od ON pv.VariantID = od.VariantID
GROUP BY p.ProductID, p.ProductName, c.CategoryName, p.BasePrice, p.SellingPrice
ORDER BY total_sales DESC;"""
    },
    {
        "id": "artisan_efficiency",
        "title": "4. Artisan Productivity & Craft Output",
        "category": "Manufacturing",
        "sql": """SELECT 
    a.ArtisanName,
    a.Specialization,
    a.DailyRate,
    COUNT(DISTINCT pr.ProductionID) AS batches_managed,
    SUM(fp.QuantityProduced) AS units_crafted,
    ROUND(SUM(fp.ProductionCost), 2) AS total_production_value
FROM Artisans a
LEFT JOIN Production pr ON a.ArtisanID = pr.ArtisanID
LEFT JOIN FinishedProducts fp ON pr.ProductionID = fp.ProductionID
GROUP BY a.ArtisanID, a.ArtisanName, a.Specialization, a.DailyRate
ORDER BY units_crafted DESC;"""
    },
    {
        "id": "inventory_alerts",
        "title": "5. Low-Stock & Reorder Alerts",
        "category": "Inventory",
        "sql": """SELECT 
    p.ProductName,
    pv.SKU,
    pv.Color,
    pv.Size,
    i.QuantityInHand,
    i.ReservedQuantity,
    (i.QuantityInHand - i.ReservedQuantity) AS available_to_sell,
    i.ReorderLevel,
    i.Location
FROM Inventory i
JOIN ProductVariants pv ON i.VariantID = pv.VariantID
JOIN Products p ON pv.ProductID = p.ProductID
ORDER BY available_to_sell ASC;"""
    },
    {
        "id": "supplier_procurement",
        "title": "6. Raw Material Spend by Supplier",
        "category": "Supply Chain",
        "sql": """SELECT 
    s.SupplierName,
    s.City,
    s.State,
    COUNT(p.PurchaseID) AS purchase_orders,
    ROUND(SUM(p.TotalAmount), 2) AS total_procurement_spend
FROM Suppliers s
JOIN Purchases p ON s.SupplierID = p.SupplierID
GROUP BY s.SupplierID, s.SupplierName, s.City, s.State
ORDER BY total_procurement_spend DESC;"""
    },
    {
        "id": "customer_clv",
        "title": "7. Customer Lifetime Value (CLV)",
        "category": "CRM & Customers",
        "sql": """SELECT 
    c.CustomerName,
    c.Email,
    c.City,
    COUNT(o.OrderID) AS total_orders,
    ROUND(SUM(o.GrandTotal), 2) AS lifetime_spend,
    ROUND(AVG(o.GrandTotal), 2) AS avg_order_val
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
WHERE o.OrderStatus != 'Cancelled'
GROUP BY c.CustomerID, c.CustomerName, c.Email, c.City
ORDER BY lifetime_spend DESC;"""
    },
    {
        "id": "lead_conversion",
        "title": "8. Lead Conversion & Channel ROI",
        "category": "CRM & Marketing",
        "sql": """SELECT 
    Source AS channel,
    COUNT(LeadID) AS total_leads,
    SUM(CASE WHEN Status = 'Converted' THEN 1 ELSE 0 END) AS converted,
    SUM(CASE WHEN Status = 'Qualified' THEN 1 ELSE 0 END) AS qualified,
    ROUND((SUM(CASE WHEN Status = 'Converted' THEN 1.0 ELSE 0.0 END) / COUNT(LeadID)) * 100.0, 2) AS conversion_rate_pct
FROM Leads
GROUP BY Source
ORDER BY total_leads DESC;"""
    },
    {
        "id": "expense_breakdown",
        "title": "9. Operational Expense Analysis",
        "category": "Finance",
        "sql": """SELECT 
    ExpenseType,
    COUNT(ExpenseID) AS entries,
    ROUND(SUM(Amount), 2) AS total_amount
FROM Expenses
GROUP BY ExpenseType
ORDER BY total_amount DESC;"""
    },
    {
        "id": "shipping_efficiency",
        "title": "10. Logistics & Courier Performance",
        "category": "Fulfillment",
        "sql": """SELECT 
    CourierName,
    COUNT(ShipmentID) AS shipments_count,
    SUM(CASE WHEN DeliveryStatus = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN DeliveryStatus = 'In Transit' THEN 1 ELSE 0 END) AS in_transit
FROM Shipments
GROUP BY CourierName
ORDER BY shipments_count DESC;"""
    }
]

# ==============================================================================
# WEB & API ROUTES
# ==============================================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/kpis", methods=["GET"])
def get_kpis():
    return jsonify(db.get_kpis())

@app.route("/api/mis_summary", methods=["GET"])
def get_mis_summary():
    kpis = db.get_kpis()
    charts = db.get_charts_data()
    
    # Calculate advanced MIS ratios
    total_rev = kpis.get("totalRevenue", 0)
    total_exp = kpis.get("totalExpenses", 0)
    total_orders = kpis.get("totalOrders", 0)
    aov = round(total_rev / total_orders, 2) if total_orders > 0 else 0
    net_margin = round((kpis.get("netProfit", 0) / total_rev) * 100, 2) if total_rev > 0 else 0
    
    # Return rate
    ret_res = db.execute_raw_query("SELECT COUNT(*), COALESCE(SUM(RefundAmount), 0) FROM Returns;")
    total_returns = ret_res["rows"][0][0] if ret_res["success"] and ret_res["rows"] else 0
    total_refunds = ret_res["rows"][0][1] if ret_res["success"] and ret_res["rows"] else 0
    return_rate = round((total_returns / total_orders) * 100, 2) if total_orders > 0 else 0

    # Production summary
    prod_res = db.execute_raw_query("SELECT SUM(QuantityProduced), AVG(UnitCost), SUM(ProductionCost) FROM FinishedProducts;")
    units_crafted = prod_res["rows"][0][0] if prod_res["success"] and prod_res["rows"] else 0
    avg_unit_cost = round(prod_res["rows"][0][1] or 0, 2) if prod_res["success"] and prod_res["rows"] else 0
    total_prod_val = round(prod_res["rows"][0][2] or 0, 2) if prod_res["success"] and prod_res["rows"] else 0

    # Lead conversion
    lead_res = db.execute_raw_query("SELECT COUNT(*), SUM(CASE WHEN Status='Converted' THEN 1 ELSE 0 END) FROM Leads;")
    total_leads = lead_res["rows"][0][0] if lead_res["success"] and lead_res["rows"] else 0
    converted_leads = lead_res["rows"][0][1] if lead_res["success"] and lead_res["rows"] else 0
    lead_conv_rate = round((converted_leads / total_leads) * 100, 2) if total_leads > 0 else 0

    # Logistics delivery rate
    ship_res = db.execute_raw_query("SELECT COUNT(*), SUM(CASE WHEN DeliveryStatus='Delivered' THEN 1 ELSE 0 END) FROM Shipments;")
    total_ships = ship_res["rows"][0][0] if ship_res["success"] and ship_res["rows"] else 0
    delivered_ships = ship_res["rows"][0][1] if ship_res["success"] and ship_res["rows"] else 0
    otd_rate = round((delivered_ships / total_ships) * 100, 2) if total_ships > 0 else 0

    return jsonify({
        "strategic": {
            "totalRevenue": total_rev,
            "totalExpenses": total_exp,
            "netProfit": kpis.get("netProfit", 0),
            "netMarginPct": net_margin,
            "averageOrderValue": aov,
            "totalOrders": total_orders
        },
        "manufacturing": {
            "unitsCrafted": units_crafted,
            "avgUnitCost": avg_unit_cost,
            "totalProductionValuation": total_prod_val,
            "activeArtisans": kpis.get("activeArtisans", 0),
            "activeBatches": kpis.get("activeBatches", 0)
        },
        "inventorySupply": {
            "inventoryValuation": kpis.get("inventoryValuation", 0),
            "lowStockAlerts": kpis.get("lowStockAlerts", 0),
            "totalSuppliers": db.execute_raw_query("SELECT COUNT(*) FROM Suppliers;")["rows"][0][0],
            "totalRawMaterials": db.execute_raw_query("SELECT COUNT(*) FROM RawMaterials;")["rows"][0][0]
        },
        "salesCRM": {
            "totalCustomers": kpis.get("totalCustomers", 0),
            "totalLeads": total_leads,
            "convertedLeads": converted_leads,
            "leadConversionRate": lead_conv_rate,
            "returnRate": return_rate,
            "totalRefunds": total_refunds,
            "onTimeDeliveryRate": otd_rate
        },
        "dbEngine": kpis.get("dbEngine", "Supabase PostgreSQL")
    })

@app.route("/api/charts", methods=["GET"])
def get_charts():
    return jsonify(db.get_charts_data())

@app.route("/api/presets", methods=["GET"])
def get_presets():
    return jsonify(PRESET_QUERIES)

@app.route("/api/tables", methods=["GET"])
def get_tables():
    return jsonify(db.get_table_metadata())

@app.route("/api/table/<table_name>", methods=["GET"])
def get_table_data(table_name):
    # Sanitize table name against known tables
    valid_tables = [t["name"] for t in db.get_table_metadata()]
    if table_name not in valid_tables:
        return jsonify({"success": False, "error": f"Invalid table: {table_name}"}), 400

    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    search = request.args.get("search", "", type=str).strip()

    query = f"SELECT * FROM {table_name}"
    if search:
        # Fetch columns first
        meta = db.execute_raw_query(f"SELECT * FROM {table_name} LIMIT 1")
        if meta.get("columns"):
            where_clauses = [f"CAST({col} AS TEXT) LIKE '%{search}%'" for col in meta["columns"]]
            query += f" WHERE {' OR '.join(where_clauses)}"

    query += f" LIMIT {limit} OFFSET {offset};"
    result = db.execute_raw_query(query)
    return jsonify(result)

@app.route("/api/query", methods=["POST"])
def execute_query():
    data = request.get_json(force=True, silent=True) or {}
    sql = data.get("sql", "").strip()
    if not sql:
        return jsonify({"success": False, "error": "SQL query is required"}), 400

    result = db.execute_raw_query(sql)
    return jsonify(result)

@app.route("/api/lookups", methods=["GET"])
def get_lookups():
    return jsonify(db.get_lookup_options())

@app.route("/api/schema/<table_name>", methods=["GET"])
def get_schema(table_name):
    valid_tables = [t["name"] for t in db.get_table_metadata()]
    if table_name not in valid_tables:
        return jsonify({"success": False, "error": f"Invalid table: {table_name}"}), 400
    return jsonify(db.get_table_schema(table_name))

@app.route("/api/records/<table_name>", methods=["POST"])
def create_record(table_name):
    valid_tables = [t["name"] for t in db.get_table_metadata()]
    if table_name not in valid_tables:
        return jsonify({"success": False, "error": f"Invalid table: {table_name}"}), 400

    data = request.get_json(force=True, silent=True) or {}
    res = db.insert_row(table_name, data)
    return jsonify(res), (200 if res.get("success") else 400)

@app.route("/api/records/<table_name>/<pk_value>", methods=["PUT"])
def update_record(table_name, pk_value):
    valid_tables = [t["name"] for t in db.get_table_metadata()]
    if table_name not in valid_tables:
        return jsonify({"success": False, "error": f"Invalid table: {table_name}"}), 400

    data = request.get_json(force=True, silent=True) or {}
    res = db.update_row(table_name, pk_value, data)
    return jsonify(res), (200 if res.get("success") else 400)

@app.route("/api/records/<table_name>/<pk_value>", methods=["DELETE"])
def delete_record(table_name, pk_value):
    valid_tables = [t["name"] for t in db.get_table_metadata()]
    if table_name not in valid_tables:
        return jsonify({"success": False, "error": f"Invalid table: {table_name}"}), 400

    res = db.delete_row(table_name, pk_value)
    return jsonify(res), (200 if res.get("success") else 400)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*70)
    print(" [AETHELGARD LEATHERWORKS] BUSINESS DATA MANAGEMENT DASHBOARD")
    print(f" Server launching on: http://0.0.0.0:{port}")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)

