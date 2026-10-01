-- ==============================================================================
-- HANDMADE LEATHER PRODUCTS - BUSINESS DATA MANAGEMENT
-- DATABASE SCHEMA DEFINITION (PostgreSQL / Supabase)
-- ==============================================================================

-- 1. DROP EXISTING TABLES (Reverse Dependency Order)
DROP TABLE IF EXISTS Returns CASCADE;
DROP TABLE IF EXISTS Shipments CASCADE;
DROP TABLE IF EXISTS Payments CASCADE;
DROP TABLE IF EXISTS OrderDetails CASCADE;
DROP TABLE IF EXISTS Orders CASCADE;
DROP TABLE IF EXISTS Discounts_Promotions CASCADE;
DROP TABLE IF EXISTS CRM_Interactions CASCADE;
DROP TABLE IF EXISTS Customers CASCADE;
DROP TABLE IF EXISTS Leads CASCADE;
DROP TABLE IF EXISTS Inventory CASCADE;
DROP TABLE IF EXISTS ProductVariants CASCADE;
DROP TABLE IF EXISTS FinishedProducts CASCADE;
DROP TABLE IF EXISTS ProductionMaterials CASCADE;
DROP TABLE IF EXISTS Production CASCADE;
DROP TABLE IF EXISTS Artisans CASCADE;
DROP TABLE IF EXISTS Products CASCADE;
DROP TABLE IF EXISTS Categories CASCADE;
DROP TABLE IF EXISTS PurchaseDetails CASCADE;
DROP TABLE IF EXISTS Purchases CASCADE;
DROP TABLE IF EXISTS RawMaterials CASCADE;
DROP TABLE IF EXISTS Suppliers CASCADE;
DROP TABLE IF EXISTS Expenses CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;
DROP TABLE IF EXISTS Addresses CASCADE;
DROP TABLE IF EXISTS Settings CASCADE;

-- ==============================================================================
-- MODULE 1: MASTER & SUPPORT TABLES
-- ==============================================================================

CREATE TABLE Settings (
    SettingID SERIAL PRIMARY KEY,
    SettingKey VARCHAR(100) UNIQUE NOT NULL,
    SettingValue TEXT NOT NULL,
    Description TEXT
);

CREATE TABLE Addresses (
    AddressID SERIAL PRIMARY KEY,
    AddressType VARCHAR(50) DEFAULT 'Shipping', -- 'Shipping', 'Billing', 'Warehouse', 'Supplier'
    AddressLine1 VARCHAR(255) NOT NULL,
    AddressLine2 VARCHAR(255),
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100) NOT NULL,
    Pincode VARCHAR(20) NOT NULL
);

CREATE TABLE Employees (
    EmployeeID SERIAL PRIMARY KEY,
    EmployeeName VARCHAR(150) NOT NULL,
    Designation VARCHAR(100) NOT NULL,
    Phone VARCHAR(50),
    Email VARCHAR(150) UNIQUE,
    Status VARCHAR(50) DEFAULT 'Active' -- 'Active', 'On Leave', 'Resigned'
);

CREATE TABLE Expenses (
    ExpenseID SERIAL PRIMARY KEY,
    ExpenseDate DATE NOT NULL DEFAULT CURRENT_DATE,
    ExpenseType VARCHAR(100) NOT NULL, -- 'Raw Materials', 'Artisan Wages', 'Shipping', 'Packaging', 'Marketing', 'Utilities'
    Description TEXT,
    Amount NUMERIC(12, 2) NOT NULL CHECK (Amount >= 0),
    PaidTo VARCHAR(150),
    PaymentMethod VARCHAR(50) DEFAULT 'Bank Transfer' -- 'Bank Transfer', 'UPI', 'Credit Card', 'Cash'
);

-- ==============================================================================
-- MODULE 2: SUPPLY & PROCUREMENT
-- ==============================================================================

CREATE TABLE Suppliers (
    SupplierID SERIAL PRIMARY KEY,
    SupplierName VARCHAR(150) NOT NULL,
    ContactPerson VARCHAR(100),
    Phone VARCHAR(50),
    Email VARCHAR(150),
    Address TEXT,
    City VARCHAR(100),
    State VARCHAR(100),
    GSTIN VARCHAR(50)
);

CREATE TABLE RawMaterials (
    MaterialID SERIAL PRIMARY KEY,
    MaterialName VARCHAR(150) NOT NULL,
    MaterialType VARCHAR(100) NOT NULL, -- 'Full Grain Leather', 'Top Grain Leather', 'Hardware/Brass', 'Waxed Thread', 'Lining Fabric', 'Adhesive'
    Unit VARCHAR(50) NOT NULL, -- 'Sq. Ft.', 'Meters', 'Pieces', 'Kg', 'Spools'
    Description TEXT
);

CREATE TABLE Purchases (
    PurchaseID SERIAL PRIMARY KEY,
    SupplierID INT NOT NULL REFERENCES Suppliers(SupplierID) ON DELETE RESTRICT,
    PurchaseDate DATE NOT NULL DEFAULT CURRENT_DATE,
    TotalAmount NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (TotalAmount >= 0),
    PaymentStatus VARCHAR(50) DEFAULT 'Paid' -- 'Paid', 'Pending', 'Partial'
);

CREATE TABLE PurchaseDetails (
    PurchaseDetailID SERIAL PRIMARY KEY,
    PurchaseID INT NOT NULL REFERENCES Purchases(PurchaseID) ON DELETE CASCADE,
    MaterialID INT NOT NULL REFERENCES RawMaterials(MaterialID) ON DELETE RESTRICT,
    Quantity NUMERIC(10, 2) NOT NULL CHECK (Quantity > 0),
    UnitPrice NUMERIC(10, 2) NOT NULL CHECK (UnitPrice >= 0),
    TotalPrice NUMERIC(12, 2) NOT NULL CHECK (TotalPrice >= 0)
);

-- ==============================================================================
-- MODULE 3: INVENTORY & PRODUCTS
-- ==============================================================================

CREATE TABLE Categories (
    CategoryID SERIAL PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL UNIQUE,
    Description TEXT,
    Status VARCHAR(50) DEFAULT 'Active' -- 'Active', 'Inactive'
);

CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    CategoryID INT NOT NULL REFERENCES Categories(CategoryID) ON DELETE RESTRICT,
    ProductName VARCHAR(200) NOT NULL,
    Description TEXT,
    BasePrice NUMERIC(10, 2) NOT NULL CHECK (BasePrice >= 0),
    SellingPrice NUMERIC(10, 2) NOT NULL CHECK (SellingPrice >= 0),
    IsActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE ProductVariants (
    VariantID SERIAL PRIMARY KEY,
    ProductID INT NOT NULL REFERENCES Products(ProductID) ON DELETE CASCADE,
    Color VARCHAR(50) NOT NULL, -- 'Saddle Tan', 'Espresso Brown', 'Obsidian Black', 'Cognac', 'Burgundy'
    Size VARCHAR(50) DEFAULT 'Standard', -- 'Small', 'Medium', 'Large', 'Standard'
    MaterialType VARCHAR(100) NOT NULL, -- 'Full Grain Veg-Tanned', 'Crazy Horse Buffalo Leather', 'Nappa Calfskin'
    SKU VARCHAR(100) NOT NULL UNIQUE,
    AdditionalPrice NUMERIC(10, 2) DEFAULT 0.00 CHECK (AdditionalPrice >= 0),
    IsActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE Inventory (
    InventoryID SERIAL PRIMARY KEY,
    VariantID INT NOT NULL REFERENCES ProductVariants(VariantID) ON DELETE CASCADE,
    QuantityInHand INT NOT NULL DEFAULT 0 CHECK (QuantityInHand >= 0),
    ReservedQuantity INT NOT NULL DEFAULT 0 CHECK (ReservedQuantity >= 0),
    ReorderLevel INT NOT NULL DEFAULT 10 CHECK (ReorderLevel >= 0),
    Location VARCHAR(100) DEFAULT 'Main Warehouse - Shelf A',
    LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- MODULE 4: MANUFACTURING & ARTISANS
-- ==============================================================================

CREATE TABLE Artisans (
    ArtisanID SERIAL PRIMARY KEY,
    ArtisanName VARCHAR(150) NOT NULL,
    Phone VARCHAR(50),
    Specialization VARCHAR(100) NOT NULL, -- 'Master Saddle Stitcher', 'Pattern Cutter', 'Edge Finishing & Burnishing', 'Tooling & Embossing'
    DailyRate NUMERIC(10, 2) NOT NULL CHECK (DailyRate > 0),
    Status VARCHAR(50) DEFAULT 'Active' -- 'Active', 'On Leave', 'Inactive'
);

CREATE TABLE Production (
    ProductionID SERIAL PRIMARY KEY,
    ArtisanID INT NOT NULL REFERENCES Artisans(ArtisanID) ON DELETE RESTRICT,
    ProductionDate DATE NOT NULL DEFAULT CURRENT_DATE,
    BatchNo VARCHAR(50) NOT NULL UNIQUE,
    Status VARCHAR(50) DEFAULT 'In Progress', -- 'Scheduled', 'In Progress', 'Completed', 'Quality Checked', 'Cancelled'
    Notes TEXT
);

CREATE TABLE ProductionMaterials (
    ProductionMaterialID SERIAL PRIMARY KEY,
    ProductionID INT NOT NULL REFERENCES Production(ProductionID) ON DELETE CASCADE,
    MaterialID INT NOT NULL REFERENCES RawMaterials(MaterialID) ON DELETE RESTRICT,
    QuantityUsed NUMERIC(10, 2) NOT NULL CHECK (QuantityUsed > 0),
    Remarks TEXT
);

CREATE TABLE FinishedProducts (
    FinishedProductID SERIAL PRIMARY KEY,
    ProductionID INT NOT NULL REFERENCES Production(ProductionID) ON DELETE CASCADE,
    ProductID INT NOT NULL REFERENCES Products(ProductID) ON DELETE RESTRICT,
    QuantityProduced INT NOT NULL CHECK (QuantityProduced > 0),
    UnitCost NUMERIC(10, 2) NOT NULL CHECK (UnitCost >= 0),
    ProductionCost NUMERIC(12, 2) NOT NULL CHECK (ProductionCost >= 0)
);

-- ==============================================================================
-- MODULE 5: CUSTOMER & CRM
-- ==============================================================================

CREATE TABLE Leads (
    LeadID SERIAL PRIMARY KEY,
    LeadName VARCHAR(150) NOT NULL,
    Phone VARCHAR(50),
    Email VARCHAR(150),
    Source VARCHAR(100) DEFAULT 'Instagram Ads', -- 'Instagram Ads', 'Google Search', 'Luxury Craft Fair', 'Referral', 'Website Signup'
    LeadDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Status VARCHAR(50) DEFAULT 'New' -- 'New', 'Contacted', 'Qualified', 'Converted', 'Lost'
);

CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    CustomerName VARCHAR(150) NOT NULL,
    Phone VARCHAR(50),
    Email VARCHAR(150) UNIQUE,
    Address TEXT,
    City VARCHAR(100),
    State VARCHAR(100),
    Pincode VARCHAR(20),
    JoinedDate DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE CRM_Interactions (
    InteractionID SERIAL PRIMARY KEY,
    CustomerID INT REFERENCES Customers(CustomerID) ON DELETE SET NULL,
    InteractionType VARCHAR(50) NOT NULL, -- 'Phone Call', 'Email Newsletter', 'Custom Monogram Inquiry', 'Support Ticket', 'WhatsApp Chat'
    Subject VARCHAR(200) NOT NULL,
    Description TEXT,
    InteractionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    NextFollowUpDate DATE,
    CreatedBy VARCHAR(100) DEFAULT 'Sales Rep'
);

-- ==============================================================================
-- MODULE 6: SALES, E-COMMERCE & FULFILLMENT
-- ==============================================================================

CREATE TABLE Discounts_Promotions (
    DiscountID SERIAL PRIMARY KEY,
    Code VARCHAR(50) NOT NULL UNIQUE,
    DiscountType VARCHAR(50) NOT NULL, -- 'Percentage', 'Fixed Amount'
    DiscountValue NUMERIC(10, 2) NOT NULL CHECK (DiscountValue > 0),
    MinOrderAmount NUMERIC(10, 2) DEFAULT 0.00,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE Orders (
    OrderID SERIAL PRIMARY KEY,
    CustomerID INT NOT NULL REFERENCES Customers(CustomerID) ON DELETE RESTRICT,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    OrderStatus VARCHAR(50) DEFAULT 'Pending', -- 'Pending', 'Processing', 'Handcrafted', 'Shipped', 'Delivered', 'Cancelled'
    TotalAmount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    DiscountAmount NUMERIC(10, 2) DEFAULT 0.00,
    ShippingAmount NUMERIC(10, 2) DEFAULT 0.00,
    GrandTotal NUMERIC(12, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE OrderDetails (
    OrderDetailID SERIAL PRIMARY KEY,
    OrderID INT NOT NULL REFERENCES Orders(OrderID) ON DELETE CASCADE,
    VariantID INT NOT NULL REFERENCES ProductVariants(VariantID) ON DELETE RESTRICT,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    UnitPrice NUMERIC(10, 2) NOT NULL CHECK (UnitPrice >= 0),
    Discount NUMERIC(10, 2) DEFAULT 0.00,
    TotalPrice NUMERIC(12, 2) NOT NULL CHECK (TotalPrice >= 0)
);

CREATE TABLE Payments (
    PaymentID SERIAL PRIMARY KEY,
    OrderID INT NOT NULL REFERENCES Orders(OrderID) ON DELETE CASCADE,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod VARCHAR(50) NOT NULL, -- 'Credit Card', 'UPI / QR', 'PayPal', 'Net Banking', 'COD'
    Amount NUMERIC(12, 2) NOT NULL CHECK (Amount >= 0),
    TransactionID VARCHAR(100) UNIQUE,
    PaymentStatus VARCHAR(50) DEFAULT 'Success' -- 'Success', 'Pending', 'Failed', 'Refunded'
);

CREATE TABLE Shipments (
    ShipmentID SERIAL PRIMARY KEY,
    OrderID INT NOT NULL REFERENCES Orders(OrderID) ON DELETE CASCADE,
    ShippingDate DATE,
    CourierName VARCHAR(100) DEFAULT 'BlueDart Express', -- 'BlueDart Express', 'DHL Luxury Freight', 'FedEx Express', 'Delhivery'
    TrackingNo VARCHAR(100) UNIQUE,
    ShippingAddress TEXT NOT NULL,
    DeliveryStatus VARCHAR(50) DEFAULT 'Dispatched', -- 'Dispatched', 'In Transit', 'Out for Delivery', 'Delivered', 'Returned'
    DeliveredDate DATE
);

CREATE TABLE Returns (
    ReturnID SERIAL PRIMARY KEY,
    OrderID INT NOT NULL REFERENCES Orders(OrderID) ON DELETE RESTRICT,
    OrderDetailID INT NOT NULL REFERENCES OrderDetails(OrderDetailID) ON DELETE RESTRICT,
    ReturnDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Reason TEXT NOT NULL, -- 'Defective Stitching', 'Wrong Color', 'Changed Mind', 'Leather Natural Scratches'
    ReturnStatus VARCHAR(50) DEFAULT 'Requested', -- 'Requested', 'Approved', 'Item Received', 'Refund Processed', 'Rejected'
    RefundAmount NUMERIC(10, 2) NOT NULL DEFAULT 0.00
);

-- ==============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ==============================================================================

CREATE INDEX idx_products_category ON Products(CategoryID);
CREATE INDEX idx_product_variants_product ON ProductVariants(ProductID);
CREATE INDEX idx_inventory_variant ON Inventory(VariantID);
CREATE INDEX idx_orders_customer ON Orders(CustomerID);
CREATE INDEX idx_orders_date ON Orders(OrderDate);
CREATE INDEX idx_order_details_order ON OrderDetails(OrderID);
CREATE INDEX idx_order_details_variant ON OrderDetails(VariantID);
CREATE INDEX idx_production_artisan ON Production(ArtisanID);
CREATE INDEX idx_production_materials_prod ON ProductionMaterials(ProductionID);
CREATE INDEX idx_purchases_supplier ON Purchases(SupplierID);
CREATE INDEX idx_crm_customer ON CRM_Interactions(CustomerID);
CREATE INDEX idx_expenses_date ON Expenses(ExpenseDate);
