-- ==============================================================================
-- HANDMADE LEATHER PRODUCTS - ADVANCED SQL ANALYTICAL QUERIES
-- Comprehensive Business Data Management Queries for Supabase PostgreSQL
-- ==============================================================================

-- ==============================================================================
-- 1. EXECUTIVE SUMMARY & REVENUE OVERVIEW
-- Total revenue, order count, average order value (AOV), and total discounts
-- ==============================================================================
SELECT 
    COUNT(DISTINCT o.OrderID) AS total_orders,
    COALESCE(SUM(o.GrandTotal), 0) AS total_revenue_usd,
    ROUND(AVG(o.GrandTotal), 2) AS average_order_value,
    COALESCE(SUM(o.DiscountAmount), 0) AS total_discounts_granted,
    COUNT(DISTINCT o.CustomerID) AS active_purchasing_customers
FROM Orders o
WHERE o.OrderStatus != 'Cancelled';


-- ==============================================================================
-- 2. SALES PERFORMANCE BY PRODUCT CATEGORY
-- Break down total revenue, units sold, and contribution percentage by category
-- ==============================================================================
SELECT 
    c.CategoryName,
    COUNT(DISTINCT p.ProductID) AS unique_products,
    SUM(od.Quantity) AS units_sold,
    ROUND(SUM(od.TotalPrice), 2) AS category_revenue,
    ROUND(SUM(od.TotalPrice) * 100.0 / (SELECT SUM(TotalPrice) FROM OrderDetails), 2) AS revenue_share_pct
FROM Categories c
JOIN Products p ON c.CategoryID = p.CategoryID
JOIN ProductVariants pv ON p.ProductID = pv.ProductID
JOIN OrderDetails od ON pv.VariantID = od.VariantID
GROUP BY c.CategoryID, c.CategoryName
ORDER BY category_revenue DESC;


-- ==============================================================================
-- 3. BEST-SELLING LEATHER PRODUCTS & PROFIT MARGIN PER PRODUCT
-- Measures product popularity, gross sales, manufacturing cost vs selling margin
-- ==============================================================================
SELECT 
    p.ProductID,
    p.ProductName,
    c.CategoryName,
    p.BasePrice AS unit_cost,
    p.SellingPrice AS retail_price,
    ROUND(((p.SellingPrice - p.BasePrice) / p.SellingPrice) * 100.0, 2) AS gross_margin_pct,
    SUM(od.Quantity) AS total_quantity_sold,
    ROUND(SUM(od.TotalPrice), 2) AS total_gross_sales,
    ROUND(SUM(od.Quantity * (p.SellingPrice - p.BasePrice)), 2) AS estimated_gross_profit
FROM Products p
JOIN Categories c ON p.CategoryID = c.CategoryID
JOIN ProductVariants pv ON p.ProductID = pv.ProductID
JOIN OrderDetails od ON pv.VariantID = od.VariantID
GROUP BY p.ProductID, p.ProductName, c.CategoryName, p.BasePrice, p.SellingPrice
ORDER BY total_gross_sales DESC;


-- ==============================================================================
-- 4. ARTISAN PRODUCTIVITY & MANUFACTURING EFFICIENCY
-- Evaluates batch output, quantity produced, and total production cost per artisan
-- ==============================================================================
SELECT 
    a.ArtisanID,
    a.ArtisanName,
    a.Specialization,
    a.DailyRate,
    COUNT(DISTINCT pr.ProductionID) AS total_batches_managed,
    SUM(fp.QuantityProduced) AS total_units_crafted,
    ROUND(SUM(fp.ProductionCost), 2) AS total_production_valuation,
    ROUND(AVG(fp.UnitCost), 2) AS avg_unit_cost
FROM Artisans a
LEFT JOIN Production pr ON a.ArtisanID = pr.ArtisanID
LEFT JOIN FinishedProducts fp ON pr.ProductionID = fp.ProductionID
GROUP BY a.ArtisanID, a.ArtisanName, a.Specialization, a.DailyRate
ORDER BY total_units_crafted DESC NULLS LAST;


-- ==============================================================================
-- 5. INVENTORY LOW-STOCK & REORDER ALERT REPORT
-- Identifies finished goods where available stock is below threshold
-- ==============================================================================
SELECT 
    p.ProductName,
    pv.SKU,
    pv.Color,
    pv.Size,
    i.QuantityInHand,
    i.ReservedQuantity,
    (i.QuantityInHand - i.ReservedQuantity) AS available_to_sell,
    i.ReorderLevel,
    i.Location,
    CASE 
        WHEN (i.QuantityInHand - i.ReservedQuantity) <= 0 THEN 'CRITICAL: OUT OF STOCK'
        WHEN (i.QuantityInHand - i.ReservedQuantity) < i.ReorderLevel THEN 'WARNING: REORDER REQUIRED'
        ELSE 'OPTIMAL STOCK'
    END AS stock_health_status
FROM Inventory i
JOIN ProductVariants pv ON i.VariantID = pv.VariantID
JOIN Products p ON pv.ProductID = p.ProductID
ORDER BY available_to_sell ASC;


-- ==============================================================================
-- 6. RAW MATERIAL PROCUREMENT SPEND BY SUPPLIER
-- Total procurement expenditure, order volume, and top leather suppliers
-- ==============================================================================
SELECT 
    s.SupplierID,
    s.SupplierName,
    s.City,
    s.State,
    COUNT(p.PurchaseID) AS purchase_orders_count,
    ROUND(SUM(p.TotalAmount), 2) AS total_procurement_spend,
    ROUND(AVG(p.TotalAmount), 2) AS avg_po_value
FROM Suppliers s
JOIN Purchases p ON s.SupplierID = p.SupplierID
GROUP BY s.SupplierID, s.SupplierName, s.City, s.State
ORDER BY total_procurement_spend DESC;


-- ==============================================================================
-- 7. RAW MATERIAL CONSUMPTION IN PRODUCTION BATCHES
-- Tracks leather hides, spools, and hardware consumed in manufacturing
-- ==============================================================================
SELECT 
    rm.MaterialID,
    rm.MaterialName,
    rm.MaterialType,
    rm.Unit,
    ROUND(SUM(pm.QuantityUsed), 2) AS total_quantity_consumed,
    COUNT(DISTINCT pm.ProductionID) AS batches_utilized_in
FROM RawMaterials rm
JOIN ProductionMaterials pm ON rm.MaterialID = pm.MaterialID
GROUP BY rm.MaterialID, rm.MaterialName, rm.MaterialType, rm.Unit
ORDER BY total_quantity_consumed DESC;


-- ==============================================================================
-- 8. CUSTOMER LIFETIME VALUE (CLV) & RFM ANALYSIS
-- Customer purchase frequency, total spend, average order value, and recency
-- ==============================================================================
SELECT 
    c.CustomerID,
    c.CustomerName,
    c.Email,
    c.City,
    c.State,
    COUNT(o.OrderID) AS total_orders_placed,
    ROUND(SUM(o.GrandTotal), 2) AS lifetime_spend,
    ROUND(AVG(o.GrandTotal), 2) AS avg_order_size,
    MAX(o.OrderDate) AS latest_order_date,
    CASE 
        WHEN SUM(o.GrandTotal) >= 1000 THEN 'VIP Tier 1 (Patron)'
        WHEN SUM(o.GrandTotal) >= 500  THEN 'Gold Tier 2 (Connoisseur)'
        ELSE 'Silver Tier 3 (Standard)'
    END AS customer_segment
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
WHERE o.OrderStatus != 'Cancelled'
GROUP BY c.CustomerID, c.CustomerName, c.Email, c.City, c.State
ORDER BY lifetime_spend DESC;


-- ==============================================================================
-- 9. MONTHLY FINANCIAL P&L: REVENUE VS EXPENSES & NET PROFIT MARGIN
-- Compares monthly customer receipts against all operating & material expenses
-- ==============================================================================
WITH MonthlyRevenue AS (
    SELECT 
        TO_CHAR(OrderDate, 'YYYY-MM') AS month_period,
        SUM(GrandTotal) AS gross_revenue
    FROM Orders
    WHERE OrderStatus != 'Cancelled'
    GROUP BY TO_CHAR(OrderDate, 'YYYY-MM')
),
MonthlyExpenses AS (
    SELECT 
        TO_CHAR(ExpenseDate, 'YYYY-MM') AS month_period,
        SUM(Amount) AS total_expenses
    FROM Expenses
    GROUP BY TO_CHAR(ExpenseDate, 'YYYY-MM')
)
SELECT 
    COALESCE(r.month_period, e.month_period) AS financial_period,
    COALESCE(r.gross_revenue, 0) AS revenue_usd,
    COALESCE(e.total_expenses, 0) AS expenses_usd,
    (COALESCE(r.gross_revenue, 0) - COALESCE(e.total_expenses, 0)) AS net_profit_usd,
    ROUND(
        ((COALESCE(r.gross_revenue, 0) - COALESCE(e.total_expenses, 0)) / NULLIF(COALESCE(r.gross_revenue, 0), 0)) * 100.0, 
        2
    ) AS net_profit_margin_pct
FROM MonthlyRevenue r
FULL OUTER JOIN MonthlyExpenses e ON r.month_period = e.month_period
ORDER BY financial_period ASC;


-- ==============================================================================
-- 10. EXPENSE CATEGORY BREAKDOWN
-- Distribution of business expenditures across materials, payroll, freight, etc.
-- ==============================================================================
SELECT 
    ExpenseType,
    COUNT(ExpenseID) AS transaction_count,
    ROUND(SUM(Amount), 2) AS total_spent,
    ROUND(SUM(Amount) * 100.0 / (SELECT SUM(Amount) FROM Expenses), 2) AS pct_of_total_expenses
FROM Expenses
GROUP BY ExpenseType
ORDER BY total_spent DESC;


-- ==============================================================================
-- 11. LEAD CONVERSION FUNNEL & MARKETING SOURCE ROI
-- Tracks lead progression from acquisition channels to paying customers
-- ==============================================================================
SELECT 
    Source AS acquisition_channel,
    COUNT(LeadID) AS total_leads,
    COUNT(CASE WHEN Status = 'Converted' THEN 1 END) AS converted_leads,
    COUNT(CASE WHEN Status = 'Qualified' THEN 1 END) AS qualified_leads,
    COUNT(CASE WHEN Status = 'Contacted' THEN 1 END) AS contacted_leads,
    ROUND(
        (COUNT(CASE WHEN Status = 'Converted' THEN 1 END)::NUMERIC / NULLIF(COUNT(LeadID), 0)) * 100.0, 
        2
    ) AS conversion_rate_pct
FROM Leads
GROUP BY Source
ORDER BY total_leads DESC;


-- ==============================================================================
-- 12. SHIPMENT & FULFILLMENT EFFICIENCY BY COURIER PARTNER
-- Delivery lead times and status tracking across logistics carriers
-- ==============================================================================
SELECT 
    CourierName,
    COUNT(ShipmentID) AS total_parcels_handled,
    COUNT(CASE WHEN DeliveryStatus = 'Delivered' THEN 1 END) AS delivered_count,
    COUNT(CASE WHEN DeliveryStatus = 'In Transit' THEN 1 END) AS in_transit_count,
    ROUND(
        AVG(CASE WHEN DeliveredDate IS NOT NULL THEN (DeliveredDate - ShippingDate) END), 
        1
    ) AS avg_delivery_days
FROM Shipments
GROUP BY CourierName
ORDER BY total_parcels_handled DESC;


-- ==============================================================================
-- 13. RETURNS & QUALITY CONTROL DEFECT AUDIT
-- Return rates, reasons for return, and total refund liability
-- ==============================================================================
SELECT 
    p.ProductName,
    r.Reason,
    r.ReturnStatus,
    COUNT(r.ReturnID) AS return_count,
    ROUND(SUM(r.RefundAmount), 2) AS total_refunded_amount
FROM Returns r
JOIN Orders o ON r.OrderID = o.OrderID
JOIN OrderDetails od ON r.OrderDetailID = od.OrderDetailID
JOIN ProductVariants pv ON od.VariantID = pv.VariantID
JOIN Products p ON pv.ProductID = p.ProductID
GROUP BY p.ProductName, r.Reason, r.ReturnStatus
ORDER BY return_count DESC;


-- ==============================================================================
-- 14. PAYMENT METHOD PREFERENCE & TRANSACTION SUCCESS RATE
-- Breakdown of customer payment modes and settlement health
-- ==============================================================================
SELECT 
    PaymentMethod,
    COUNT(PaymentID) AS transaction_count,
    ROUND(SUM(Amount), 2) AS total_collected,
    COUNT(CASE WHEN PaymentStatus = 'Success' THEN 1 END) AS successful_count,
    COUNT(CASE WHEN PaymentStatus = 'Pending' THEN 1 END) AS pending_count,
    ROUND(
        (COUNT(CASE WHEN PaymentStatus = 'Success' THEN 1 END)::NUMERIC / NULLIF(COUNT(PaymentID), 0)) * 100.0,
        2
    ) AS success_rate_pct
FROM Payments
GROUP BY PaymentMethod
ORDER BY total_collected DESC;


-- ==============================================================================
-- 15. CRM ENGAGEMENT & HIGH-TOUCH CUSTOMER INTERACTIONS
-- Summary of customer touchpoints, monograms, and consultation inquiries
-- ==============================================================================
SELECT 
    ci.InteractionType,
    COUNT(ci.InteractionID) AS interaction_count,
    COUNT(DISTINCT ci.CustomerID) AS unique_customers_engaged,
    COUNT(CASE WHEN ci.NextFollowUpDate IS NOT NULL AND ci.NextFollowUpDate >= CURRENT_DATE THEN 1 END) AS pending_action_items
FROM CRM_Interactions ci
GROUP BY ci.InteractionType
ORDER BY interaction_count DESC;
