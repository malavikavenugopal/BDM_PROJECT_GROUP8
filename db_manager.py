import os
import sqlite3
import datetime
import time
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if os.getenv("VERCEL"):
    LOCAL_SQLITE_PATH = "/tmp/leather_products.db"
    orig_path = os.path.join(os.path.dirname(__file__), "leather_products.db")
    if os.path.exists(orig_path) and not os.path.exists(LOCAL_SQLITE_PATH):
        import shutil
        shutil.copyfile(orig_path, LOCAL_SQLITE_PATH)
else:
    LOCAL_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "leather_products.db")

TABLE_PRIMARY_KEYS = {
    "Suppliers": "SupplierID",
    "RawMaterials": "MaterialID",
    "Purchases": "PurchaseID",
    "PurchaseDetails": "PurchaseDetailID",
    "Artisans": "ArtisanID",
    "Production": "ProductionID",
    "ProductionMaterials": "ProductionMaterialID",
    "FinishedProducts": "FinishedProductID",
    "Categories": "CategoryID",
    "Products": "ProductID",
    "ProductVariants": "VariantID",
    "Inventory": "InventoryID",
    "Orders": "OrderID",
    "OrderDetails": "OrderDetailID",
    "Payments": "PaymentID",
    "Shipments": "ShipmentID",
    "Returns": "ReturnID",
    "Discounts_Promotions": "DiscountID",
    "Customers": "CustomerID",
    "Leads": "LeadID",
    "CRM_Interactions": "InteractionID",
    "Employees": "EmployeeID",
    "Expenses": "ExpenseID",
    "Addresses": "AddressID",
    "Settings": "SettingID"
}
TABLE_PRIMARY_KEYS_LOWER = {k.lower(): v for k, v in TABLE_PRIMARY_KEYS.items()}

class DatabaseManager:
    def __init__(self):
        self.is_postgres = False
        self.conn_str = DATABASE_URL
        self.pg_pool = None
        self._test_connection()

    def _test_connection(self):
        """Attempts to connect to Supabase PostgreSQL, falls back to SQLite if unreachable."""
        if self.conn_str:
            try:
                self.pg_pool = pool.ThreadedConnectionPool(1, 15, self.conn_str, connect_timeout=15)
                conn = self.pg_pool.getconn()
                cur = conn.cursor()
                cur.execute("SELECT 1;")
                cur.fetchone()
                cur.close()
                self.pg_pool.putconn(conn)
                self.is_postgres = True
                print("[INFO] Successfully connected to live Supabase PostgreSQL database!")
                return
            except Exception as e:
                print(f"[NOTICE] Supabase connection ({e}). Using local database instance for dashboard...")
        
        self.is_postgres = False
        self._init_sqlite_db()

    def _init_sqlite_db(self):
        """Initializes SQLite database with all tables and seed data if not present."""
        if os.path.exists(LOCAL_SQLITE_PATH):
            try:
                conn = sqlite3.connect(LOCAL_SQLITE_PATH)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM Products;")
                count = cur.fetchone()[0]
                conn.close()
                if count > 0:
                    return
            except Exception:
                pass

        print("[INFO] Initializing local database schema and seed dataset...")
        if os.path.exists(LOCAL_SQLITE_PATH):
            try:
                os.remove(LOCAL_SQLITE_PATH)
            except Exception:
                pass

        conn = sqlite3.connect(LOCAL_SQLITE_PATH)
        cur = conn.cursor()

        # DDL for SQLite
        ddl = """
        CREATE TABLE IF NOT EXISTS Settings (
            SettingID INTEGER PRIMARY KEY AUTOINCREMENT,
            SettingKey TEXT UNIQUE NOT NULL,
            SettingValue TEXT NOT NULL,
            Description TEXT
        );

        CREATE TABLE IF NOT EXISTS Addresses (
            AddressID INTEGER PRIMARY KEY AUTOINCREMENT,
            AddressType TEXT DEFAULT 'Shipping',
            AddressLine1 TEXT NOT NULL,
            AddressLine2 TEXT,
            City TEXT NOT NULL,
            State TEXT NOT NULL,
            Pincode TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Employees (
            EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
            EmployeeName TEXT NOT NULL,
            Designation TEXT NOT NULL,
            Phone TEXT,
            Email TEXT UNIQUE,
            Status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS Expenses (
            ExpenseID INTEGER PRIMARY KEY AUTOINCREMENT,
            ExpenseDate TEXT NOT NULL,
            ExpenseType TEXT NOT NULL,
            Description TEXT,
            Amount REAL NOT NULL,
            PaidTo TEXT,
            PaymentMethod TEXT DEFAULT 'Bank Transfer'
        );

        CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
            SupplierName TEXT NOT NULL,
            ContactPerson TEXT,
            Phone TEXT,
            Email TEXT,
            Address TEXT,
            City TEXT,
            State TEXT,
            GSTIN TEXT
        );

        CREATE TABLE IF NOT EXISTS RawMaterials (
            MaterialID INTEGER PRIMARY KEY AUTOINCREMENT,
            MaterialName TEXT NOT NULL,
            MaterialType TEXT NOT NULL,
            Unit TEXT NOT NULL,
            Description TEXT
        );

        CREATE TABLE IF NOT EXISTS Purchases (
            PurchaseID INTEGER PRIMARY KEY AUTOINCREMENT,
            SupplierID INTEGER REFERENCES Suppliers(SupplierID),
            PurchaseDate TEXT NOT NULL,
            TotalAmount REAL NOT NULL DEFAULT 0.00,
            PaymentStatus TEXT DEFAULT 'Paid'
        );

        CREATE TABLE IF NOT EXISTS PurchaseDetails (
            PurchaseDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
            PurchaseID INTEGER REFERENCES Purchases(PurchaseID),
            MaterialID INTEGER REFERENCES RawMaterials(MaterialID),
            Quantity REAL NOT NULL,
            UnitPrice REAL NOT NULL,
            TotalPrice REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Categories (
            CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryName TEXT NOT NULL UNIQUE,
            Description TEXT,
            Status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryID INTEGER REFERENCES Categories(CategoryID),
            ProductName TEXT NOT NULL,
            Description TEXT,
            BasePrice REAL NOT NULL,
            SellingPrice REAL NOT NULL,
            IsActive INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS ProductVariants (
            VariantID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductID INTEGER REFERENCES Products(ProductID),
            Color TEXT NOT NULL,
            Size TEXT DEFAULT 'Standard',
            MaterialType TEXT NOT NULL,
            SKU TEXT NOT NULL UNIQUE,
            AdditionalPrice REAL DEFAULT 0.00,
            IsActive INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS Inventory (
            InventoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            VariantID INTEGER REFERENCES ProductVariants(VariantID),
            QuantityInHand INTEGER NOT NULL DEFAULT 0,
            ReservedQuantity INTEGER NOT NULL DEFAULT 0,
            ReorderLevel INTEGER NOT NULL DEFAULT 10,
            Location TEXT DEFAULT 'Main Warehouse - Shelf A',
            LastUpdated TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Artisans (
            ArtisanID INTEGER PRIMARY KEY AUTOINCREMENT,
            ArtisanName TEXT NOT NULL,
            Phone TEXT,
            Specialization TEXT NOT NULL,
            DailyRate REAL NOT NULL,
            Status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS Production (
            ProductionID INTEGER PRIMARY KEY AUTOINCREMENT,
            ArtisanID INTEGER REFERENCES Artisans(ArtisanID),
            ProductionDate TEXT NOT NULL,
            BatchNo TEXT NOT NULL UNIQUE,
            Status TEXT DEFAULT 'In Progress',
            Notes TEXT
        );

        CREATE TABLE IF NOT EXISTS ProductionMaterials (
            ProductionMaterialID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductionID INTEGER REFERENCES Production(ProductionID),
            MaterialID INTEGER REFERENCES RawMaterials(MaterialID),
            QuantityUsed REAL NOT NULL,
            Remarks TEXT
        );

        CREATE TABLE IF NOT EXISTS FinishedProducts (
            FinishedProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductionID INTEGER REFERENCES Production(ProductionID),
            ProductID INTEGER REFERENCES Products(ProductID),
            QuantityProduced INTEGER NOT NULL,
            UnitCost REAL NOT NULL,
            ProductionCost REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Customers (
            CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerName TEXT NOT NULL,
            Phone TEXT,
            Email TEXT UNIQUE,
            Address TEXT,
            City TEXT,
            State TEXT,
            Pincode TEXT,
            JoinedDate TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Leads (
            LeadID INTEGER PRIMARY KEY AUTOINCREMENT,
            LeadName TEXT NOT NULL,
            Phone TEXT,
            Email TEXT,
            Source TEXT DEFAULT 'Instagram Ads',
            LeadDate TEXT NOT NULL,
            Status TEXT DEFAULT 'New'
        );

        CREATE TABLE IF NOT EXISTS CRM_Interactions (
            InteractionID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerID INTEGER REFERENCES Customers(CustomerID),
            InteractionType TEXT NOT NULL,
            Subject TEXT NOT NULL,
            Description TEXT,
            InteractionDate TEXT DEFAULT CURRENT_TIMESTAMP,
            NextFollowUpDate TEXT,
            CreatedBy TEXT DEFAULT 'Sales Rep'
        );

        CREATE TABLE IF NOT EXISTS Discounts_Promotions (
            DiscountID INTEGER PRIMARY KEY AUTOINCREMENT,
            Code TEXT NOT NULL UNIQUE,
            DiscountType TEXT NOT NULL,
            DiscountValue REAL NOT NULL,
            MinOrderAmount REAL DEFAULT 0.00,
            StartDate TEXT NOT NULL,
            EndDate TEXT NOT NULL,
            IsActive INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerID INTEGER REFERENCES Customers(CustomerID),
            OrderDate TEXT DEFAULT CURRENT_TIMESTAMP,
            OrderStatus TEXT DEFAULT 'Pending',
            TotalAmount REAL NOT NULL DEFAULT 0.00,
            DiscountAmount REAL DEFAULT 0.00,
            ShippingAmount REAL DEFAULT 0.00,
            GrandTotal REAL NOT NULL DEFAULT 0.00
        );

        CREATE TABLE IF NOT EXISTS OrderDetails (
            OrderDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER REFERENCES Orders(OrderID),
            VariantID INTEGER REFERENCES ProductVariants(VariantID),
            Quantity INTEGER NOT NULL,
            UnitPrice REAL NOT NULL,
            Discount REAL DEFAULT 0.00,
            TotalPrice REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Payments (
            PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER REFERENCES Orders(OrderID),
            PaymentDate TEXT DEFAULT CURRENT_TIMESTAMP,
            PaymentMethod TEXT NOT NULL,
            Amount REAL NOT NULL,
            TransactionID TEXT UNIQUE,
            PaymentStatus TEXT DEFAULT 'Success'
        );

        CREATE TABLE IF NOT EXISTS Shipments (
            ShipmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER REFERENCES Orders(OrderID),
            ShippingDate TEXT,
            CourierName TEXT DEFAULT 'BlueDart Express',
            TrackingNo TEXT UNIQUE,
            ShippingAddress TEXT NOT NULL,
            DeliveryStatus TEXT DEFAULT 'Dispatched',
            DeliveredDate TEXT
        );

        CREATE TABLE IF NOT EXISTS Returns (
            ReturnID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER REFERENCES Orders(OrderID),
            OrderDetailID INTEGER REFERENCES OrderDetails(OrderDetailID),
            ReturnDate TEXT NOT NULL,
            Reason TEXT NOT NULL,
            ReturnStatus TEXT DEFAULT 'Requested',
            RefundAmount REAL NOT NULL DEFAULT 0.00
        );
        """
        for statement in ddl.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cur.execute(statement)
                except Exception as e:
                    print(f"[DDL ERROR] in {statement[:30]}...: {e}")

        # Seed data
        settings_data = [
            ("STORE_NAME", "Aethelgard Handcrafted Leatherworks", "Official business name"),
            ("CURRENCY", "USD", "Operating business currency"),
            ("TAX_RATE_PERCENT", "12.0", "Applicable VAT/GST sales tax rate"),
            ("FREE_SHIPPING_THRESHOLD", "150.00", "Minimum order amount for complimentary express freight"),
            ("REORDER_ALERT_EMAIL", "inventory@aethelgard-leather.com", "Alert destination for low stock items"),
            ("DEFAULT_LEAD_TIME_DAYS", "7", "Standard lead time for bespoke handcrafted items"),
            ("WARRANTY_MONTHS", "24", "Manufacturer warranty on leather stitching and brass hardware"),
            ("LEATHER_SOURCE_STANDARD", "100% Full-Grain Vegetable-Tanned Eco Certified", "Leather procurement guideline")
        ]
        cur.executemany("INSERT INTO Settings (SettingKey, SettingValue, Description) VALUES (?, ?, ?);", settings_data)

        addresses_data = [
            ("Warehouse", "104 Artisan Boulevard", "Bay 4 Industrial Estate", "Florence", "Tuscany", "50123"),
            ("Workshop", "45 Tannery Row", "Suite 2B", "Kanpur", "Uttar Pradesh", "208001"),
            ("HQ", "742 Evergreen Terrace", "Floor 3", "Austin", "Texas", "78701"),
            ("Supplier Hub", "12 Santa Croce Way", "Depot 8", "Pisa", "Tuscany", "56121"),
            ("Shipping", "88 High Street", "Dock 1", "London", "Greater London", "EC1A 1BB")
        ]
        cur.executemany("INSERT INTO Addresses (AddressType, AddressLine1, AddressLine2, City, State, Pincode) VALUES (?, ?, ?, ?, ?, ?);", addresses_data)

        employees_data = [
            ("Victoria Vance", "Chief Operations Officer", "+1-512-555-0199", "v.vance@aethelgard.com", "Active"),
            ("Marcus Sterling", "Master Leather Guild Supervisor", "+1-512-555-0182", "m.sterling@aethelgard.com", "Active"),
            ("Aanya Sen", "Quality Assurance & Finishing Lead", "+91-98765-43210", "a.sen@aethelgard.com", "Active"),
            ("Julian Croft", "Head of E-Commerce & CRM", "+1-512-555-0144", "j.croft@aethelgard.com", "Active"),
            ("Derek O'Connor", "Procurement & Logistics Manager", "+1-512-555-0176", "d.oconnor@aethelgard.com", "Active"),
            ("Sofia Morales", "Digital Marketing & Brand Strategist", "+1-512-555-0163", "s.morales@aethelgard.com", "Active")
        ]
        cur.executemany("INSERT INTO Employees (EmployeeName, Designation, Phone, Email, Status) VALUES (?, ?, ?, ?, ?);", employees_data)

        suppliers_data = [
            ("Tuscan Heritage Tannery S.p.A.", "Giovanni Moretti", "+39-055-123456", "sales@tuscantannery.it", "Via del Cuoio 44", "Santa Croce sull'Arno", "Pisa", "IT98765432100"),
            ("Ganges Prime Leather Works", "Vikram Rathore", "+91-512-2345678", "exports@gangesleather.in", "Jajmau Industrial Area", "Kanpur", "Uttar Pradesh", "09AAACG1234F1Z8"),
            ("Solid Brass & Hardware Foundry", "Arthur Pendelton", "+44-20-7946-0912", "orders@solidbrasscraft.co.uk", "Forge Road 12", "Birmingham", "West Midlands", "GB123456789"),
            ("Coats & Clark Waxed Threads", "Clara Schmidt", "+49-30-891234", "service@coatsclark.de", "Fadenstrasse 9", "Stuttgart", "Baden-Württemberg", "DE812345678"),
            ("Fiebing's Leather Dye & Edge Balm", "Thomas Miller", "+1-414-555-0130", "supplies@fiebingsusa.com", "516 S 2nd St", "Milwaukee", "Wisconsin", "US391283912"),
            ("Pelle Naturale Organic Leathers", "Matteo Ricci", "+39-055-789012", "matteo@pellenaturale.it", "Piazza Santa Croce 8", "Florence", "Tuscany", "IT11223344556")
        ]
        cur.executemany("INSERT INTO Suppliers (SupplierName, ContactPerson, Phone, Email, Address, City, State, GSTIN) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", suppliers_data)

        raw_materials_data = [
            ("Italian Veg-Tanned Full-Grain Cowhide (Saddle Tan)", "Full Grain Leather", "Sq. Ft.", "Grade A Tuscan cowhide, 5-6 oz thickness, vegetable-tanned"),
            ("Crazy Horse Distressed Buffalo Hide (Dark Espresso)", "Top Grain Leather", "Sq. Ft.", "Heavy wax finish with natural pull-up effect, 6-7 oz"),
            ("Nappa Calfskin Lining (Midnight Black)", "Calfskin Leather", "Sq. Ft.", "Ultra-soft 2 oz calf leather for luxury interior lining"),
            ("Solid Cast Brass Roller Buckles 35mm", "Hardware/Brass", "Pieces", "Hand-polished heavy duty solid antique brass buckles"),
            ("YKK Heavy Metal Antique Brass Zippers (#5 - 18 inch)", "Hardware/Zippers", "Pieces", "Heavy gauge antique brass teeth with leather pullers"),
            ("Fil Au Chinois Waxed French Linen Thread (0.57mm)", "Waxed Thread", "Spools", "Premium hand-waxed linen thread for saddle stitching (500m spool)"),
            ("Tokonole Japanese Leather Edge Gum (500g)", "Adhesive & Edge Compound", "Kg", "Water-based leather burnishing gum for mirror edge finish"),
            ("Pure Neatsfoot Oil Conditioning Balm (1 Litre)", "Conditioner/Oil", "Litre", "Deep penetrating natural leather preserver & softening compound"),
            ("Solid Brass Chicago Screws & Rivets (Pack of 100)", "Hardware/Rivets", "Packs", "Corrosion resistant machined solid brass rivets"),
            ("Reinforced Suede Microfiber Backing Material", "Lining Fabric", "Meters", "Non-fraying plush velvet suede backing for laptop compartments")
        ]
        cur.executemany("INSERT INTO RawMaterials (MaterialName, MaterialType, Unit, Description) VALUES (?, ?, ?, ?);", raw_materials_data)

        purchases_seed = [
            (1, "2026-08-01", 3850.00, "Paid"),
            (2, "2026-08-05", 2400.00, "Paid"),
            (3, "2026-08-10", 1150.00, "Paid"),
            (4, "2026-08-15", 720.00, "Paid"),
            (5, "2026-08-20", 450.00, "Paid"),
            (1, "2026-09-02", 4200.00, "Paid"),
            (2, "2026-09-08", 2900.00, "Paid"),
            (3, "2026-09-14", 1350.00, "Paid"),
            (6, "2026-09-20", 3100.00, "Paid"),
            (4, "2026-09-25", 650.00, "Paid")
        ]
        cur.executemany("INSERT INTO Purchases (SupplierID, PurchaseDate, TotalAmount, PaymentStatus) VALUES (?, ?, ?, ?);", purchases_seed)

        purchase_details_seed = [
            (1, 1, 200.00, 15.00, 3000.00),
            (1, 3, 50.00, 17.00, 850.00),
            (2, 2, 200.00, 12.00, 2400.00),
            (3, 4, 150.00, 5.00, 750.00),
            (3, 9, 40.00, 10.00, 400.00),
            (4, 6, 20.00, 36.00, 720.00),
            (5, 7, 10.00, 25.00, 250.00),
            (5, 8, 10.00, 20.00, 200.00),
            (6, 1, 220.00, 15.00, 3300.00),
            (6, 3, 60.00, 15.00, 900.00),
            (7, 2, 250.00, 11.60, 2900.00),
            (8, 4, 180.00, 5.00, 900.00),
            (8, 5, 90.00, 5.00, 450.00),
            (9, 1, 150.00, 16.00, 2400.00),
            (9, 10, 35.00, 20.00, 700.00),
            (10, 6, 18.00, 36.11, 650.00)
        ]
        cur.executemany("INSERT INTO PurchaseDetails (PurchaseID, MaterialID, Quantity, UnitPrice, TotalPrice) VALUES (?, ?, ?, ?, ?);", purchase_details_seed)

        artisans_data = [
            ("Marco Bellini", "+39-340-1122334", "Master Saddle Stitcher & Bag Maker", 160.00, "Active"),
            ("Rajesh Kumar Sharma", "+91-94150-88776", "Pattern Cutting & Edge Burnishing", 110.00, "Active"),
            ("Elena Rostova", "+44-7700-900123", "Wallet & Small Leather Goods Artisan", 140.00, "Active"),
            ("Samuel K. Wright", "+1-512-555-0189", "Heavy Belt & Tooling Specialist", 150.00, "Active"),
            ("Anita Verma", "+91-98390-11223", "Lining, Hardware & Assembly Expert", 105.00, "Active"),
            ("Matteo Rossi", "+39-348-9988776", "Leather Dyeing & Vintage Patina Finisher", 155.00, "Active"),
            ("Liam Henderson", "+1-512-555-0177", "Embroidery & Laser Engraving Artisan", 130.00, "Active")
        ]
        cur.executemany("INSERT INTO Artisans (ArtisanName, Phone, Specialization, DailyRate, Status) VALUES (?, ?, ?, ?, ?);", artisans_data)

        categories_data = [
            ("Handcrafted Wallets", "Minimalist bifold, trifold, cardholders and passport sleeves crafted with full-grain leather.", "Active"),
            ("Luxury Bags & Briefcases", "Vegetable-tanned leather messenger bags, heritage briefcases and weekend duffels.", "Active"),
            ("Full-Grain Leather Belts", "Solid brass buckled heavy duty full-grain harness and dress belts.", "Active"),
            ("Leather Travel Gear", "Duffel bags, dopp kits, luggage tags and passport organizers.", "Active"),
            ("Desk & Tech Folios", "MacBook leather sleeves, iPad cases, mousepads and luxury desk mats.", "Active"),
            ("Leather Jackets & Vests", "Custom tailored genuine leather bomber, biker, and café racer jackets.", "Active")
        ]
        cur.executemany("INSERT INTO Categories (CategoryName, Description, Status) VALUES (?, ?, ?);", categories_data)

        products_data = [
            (1, "The Heritage Bifold Wallet", "Classic 6-pocket vegetable-tanned leather bifold with hidden cash flap and hand-stitched edges.", 45.00, 115.00, 1),
            (1, "The Slim Cardholder Sleeve", "Ultra-thin 4-slot minimalist leather cardholder with central cash stash.", 20.00, 55.00, 1),
            (1, "The Passport Travel Wallet", "Full-grain passport holder with boarding pass pocket, card slots and pen loop.", 38.00, 95.00, 1),
            (2, "The Executive Briefcase 15\"", "Full-grain vegetable-tanned leather briefcase with solid brass hardware, laptop divider and key lanyard.", 180.00, 480.00, 1),
            (2, "The Artisan Messenger Satchel", "Classic over-the-shoulder messenger bag with quick-release brass buckles and reinforced base.", 140.00, 360.00, 1),
            (2, "The Florence Leather Tote Bag", "Spacious open-top women's tote handcrafted from pull-up cowhide with inner zipped pocket.", 110.00, 290.00, 1),
            (3, "The Old-World Harness Belt 1.5\"", "Heavy 10 oz English bridle leather belt with solid cast brass roller buckle and beveled edges.", 32.00, 85.00, 1),
            (3, "The Formal Feathered Dress Belt", "Slim 1.25\" vegetable-tanned calfskin belt with feathered edge profile and brushed nickel hardware.", 35.00, 95.00, 1),
            (4, "The Nomad Weekender Duffel 45L", "Flight-ready 45L luxury leather duffel with shoe compartment, luggage tag and heavy brass zippers.", 220.00, 580.00, 1),
            (4, "The Master Dopp Kit / Toiletry Bag", "Water-resistant lined leather shaving kit bag with wide mouth frame opening.", 30.00, 80.00, 1),
            (5, "The Executive Desk Pad Mat (Large)", "Smooth vegetable-tanned desk blotter with hand-burnished edges and non-slip backing.", 45.00, 120.00, 1),
            (5, "The MacBook Pro Leather Folio Sleeve", "Snug fit padded leather folio with magnetic flap closure and plush microfiber lining.", 40.00, 110.00, 1),
            (6, "The Café Racer Moto Jacket", "Top-grain cowhide motorcycle jacket with antique brass zippers, quilted shoulders and breathable satin lining.", 260.00, 690.00, 1),
            (6, "The Vintage Flight Bomber Jacket", "Classic sheepskin shearling collar leather bomber with ribbed storm cuffs and flap cargo pockets.", 310.00, 780.00, 1)
        ]
        cur.executemany("INSERT INTO Products (CategoryID, ProductName, Description, BasePrice, SellingPrice, IsActive) VALUES (?, ?, ?, ?, ?, ?);", products_data)

        variants_data = [
            (1, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "WAL-HER-TAN", 0.00, 1),
            (1, "Espresso Brown", "Standard", "Crazy Horse Buffalo", "WAL-HER-BRN", 0.00, 1),
            (1, "Obsidian Black", "Standard", "Nappa Calfskin", "WAL-HER-BLK", 5.00, 1),
            (2, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "CRD-SLM-TAN", 0.00, 1),
            (2, "Burgundy Wine", "Standard", "Full Grain Veg-Tanned", "CRD-SLM-BUR", 0.00, 1),
            (2, "Espresso Brown", "Standard", "Crazy Horse Buffalo", "CRD-SLM-BRN", 0.00, 1),
            (3, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "PAS-TRV-TAN", 0.00, 1),
            (3, "Obsidian Black", "Standard", "Nappa Calfskin", "PAS-TRV-BLK", 0.00, 1),
            (4, "Cognac Brown", "15-Inch", "Full Grain Veg-Tanned", "BAG-BRF-COG-15", 0.00, 1),
            (4, "Obsidian Black", "15-Inch", "Full Grain Veg-Tanned", "BAG-BRF-BLK-15", 20.00, 1),
            (5, "Espresso Brown", "Medium", "Crazy Horse Buffalo", "BAG-MSG-BRN-M", 0.00, 1),
            (5, "Saddle Tan", "Medium", "Full Grain Veg-Tanned", "BAG-MSG-TAN-M", 0.00, 1),
            (6, "Warm Chestnut", "Large", "Full Grain Veg-Tanned", "TOT-FLO-CHE-L", 0.00, 1),
            (6, "Obsidian Black", "Large", "Full Grain Veg-Tanned", "TOT-FLO-BLK-L", 0.00, 1),
            (7, "Saddle Tan", "34-Inch", "Full Grain Veg-Tanned", "BLT-HAR-TAN-34", 0.00, 1),
            (7, "Saddle Tan", "36-Inch", "Full Grain Veg-Tanned", "BLT-HAR-TAN-36", 0.00, 1),
            (7, "Espresso Brown", "34-Inch", "Full Grain Veg-Tanned", "BLT-HAR-BRN-34", 0.00, 1),
            (7, "Espresso Brown", "36-Inch", "Full Grain Veg-Tanned", "BLT-HAR-BRN-36", 0.00, 1),
            (8, "Obsidian Black", "34-Inch", "Nappa Calfskin", "BLT-DRS-BLK-34", 0.00, 1),
            (8, "Obsidian Black", "36-Inch", "Nappa Calfskin", "BLT-DRS-BLK-36", 0.00, 1),
            (9, "Saddle Tan", "45L Standard", "Full Grain Veg-Tanned", "DUF-NOM-TAN-45", 0.00, 1),
            (9, "Espresso Brown", "45L Standard", "Crazy Horse Buffalo", "DUF-NOM-BRN-45", 0.00, 1),
            (10, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "DOP-MST-TAN", 0.00, 1),
            (10, "Espresso Brown", "Standard", "Crazy Horse Buffalo", "DOP-MST-BRN", 0.00, 1),
            (11, "Saddle Tan", "90x40cm", "Full Grain Veg-Tanned", "DSK-MAT-TAN", 0.00, 1),
            (11, "Espresso Brown", "90x40cm", "Full Grain Veg-Tanned", "DSK-MAT-BRN", 0.00, 1),
            (12, "Cognac Brown", "14-Inch", "Full Grain Veg-Tanned", "FOL-MAC-COG-14", 0.00, 1),
            (12, "Cognac Brown", "16-Inch", "Full Grain Veg-Tanned", "FOL-MAC-COG-16", 15.00, 1),
            (13, "Obsidian Black", "Large", "Top Grain Cowhide", "JKT-RAC-BLK-L", 0.00, 1),
            (13, "Vintage Brown", "Large", "Top Grain Cowhide", "JKT-RAC-BRN-L", 0.00, 1),
            (14, "Dark Brown", "Large", "Top Grain Cowhide", "JKT-BOM-BRN-L", 0.00, 1)
        ]
        cur.executemany("INSERT INTO ProductVariants (ProductID, Color, Size, MaterialType, SKU, AdditionalPrice, IsActive) VALUES (?, ?, ?, ?, ?, ?, ?);", variants_data)

        inventory_seed = [
            (1, 45, 4, 15, "Warehouse Bay A - Shelf 1"),
            (2, 38, 2, 15, "Warehouse Bay A - Shelf 1"),
            (3, 28, 1, 10, "Warehouse Bay A - Shelf 1"),
            (4, 60, 5, 20, "Warehouse Bay A - Shelf 2"),
            (5, 22, 3, 10, "Warehouse Bay A - Shelf 2"),
            (6, 40, 2, 15, "Warehouse Bay A - Shelf 2"),
            (7, 18, 1, 10, "Warehouse Bay A - Shelf 3"),
            (8, 14, 0, 8,  "Warehouse Bay A - Shelf 3"),
            (9, 12, 2, 5,  "Warehouse Bay B - Heavy Rack 1"),
            (10, 8, 1, 5,  "Warehouse Bay B - Heavy Rack 1"),
            (11, 16, 2, 6, "Warehouse Bay B - Heavy Rack 2"),
            (12, 14, 1, 6, "Warehouse Bay B - Heavy Rack 2"),
            (13, 20, 2, 8, "Warehouse Bay B - Shelf 4"),
            (14, 15, 1, 8, "Warehouse Bay B - Shelf 4"),
            (15, 35, 4, 12, "Warehouse Bay C - Belt Rack 1"),
            (16, 40, 3, 12, "Warehouse Bay C - Belt Rack 1"),
            (17, 30, 2, 12, "Warehouse Bay C - Belt Rack 2"),
            (18, 28, 1, 12, "Warehouse Bay C - Belt Rack 2"),
            (19, 22, 2, 10, "Warehouse Bay C - Belt Rack 3"),
            (20, 25, 1, 10, "Warehouse Bay C - Belt Rack 3"),
            (21, 9,  1, 4,  "Warehouse Bay B - Duffel Vault"),
            (22, 7,  0, 4,  "Warehouse Bay B - Duffel Vault"),
            (23, 24, 2, 10, "Warehouse Bay A - Shelf 5"),
            (24, 19, 1, 10, "Warehouse Bay A - Shelf 5"),
            (25, 26, 3, 8,  "Warehouse Bay D - Desk Acc"),
            (26, 21, 2, 8,  "Warehouse Bay D - Desk Acc"),
            (27, 17, 1, 6,  "Warehouse Bay D - Tech Sleeves"),
            (28, 12, 0, 6,  "Warehouse Bay D - Tech Sleeves"),
            (29, 6,  1, 3,  "Apparel Room - Rack 1"),
            (30, 5,  0, 3,  "Apparel Room - Rack 1"),
            (31, 4,  0, 3,  "Apparel Room - Rack 2")
        ]
        cur.executemany("INSERT INTO Inventory (VariantID, QuantityInHand, ReservedQuantity, ReorderLevel, Location) VALUES (?, ?, ?, ?, ?);", inventory_seed)

        production_seed = [
            (1, "2026-08-05", "BATCH-2026-08-A01", "Completed", "Crafted 30 units of Heritage Bifolds (Saddle Tan). Zero defect rate."),
            (2, "2026-08-12", "BATCH-2026-08-A02", "Completed", "Crafted 15 Executive Briefcases in Tuscan Veg-Tan leather."),
            (3, "2026-08-18", "BATCH-2026-08-A03", "Completed", "Crafted 40 Slim Cardholders in Burgundy and Espresso."),
            (4, "2026-08-25", "BATCH-2026-08-A04", "Completed", "Crafted 50 Old-World Harness Belts with solid brass buckles."),
            (1, "2026-09-02", "BATCH-2026-09-B01", "Completed", "Crafted 10 Nomad Weekender Duffels in 45L configuration."),
            (5, "2026-09-10", "BATCH-2026-09-B02", "Completed", "Crafted 25 Florence Leather Totes with reinforced brass rivets."),
            (6, "2026-09-16", "BATCH-2026-09-B03", "Completed", "Custom patina dye finish batch for 8 Café Racer Moto Jackets."),
            (7, "2026-09-22", "BATCH-2026-09-B04", "Completed", "Laser cut and hand stitched 30 MacBook leather sleeves."),
            (2, "2026-09-27", "BATCH-2026-09-B05", "In Progress", "Currently assembling 20 Artisan Messenger Satchels."),
            (4, "2026-09-29", "BATCH-2026-09-B06", "Scheduled", "Upcoming batch for 60 Formal Dress Belts.")
        ]
        cur.executemany("INSERT INTO Production (ArtisanID, ProductionDate, BatchNo, Status, Notes) VALUES (?, ?, ?, ?, ?);", production_seed)

        production_materials_seed = [
            (1, 1, 45.00, "Used 45 sq ft of Grade A Tuscan Veg-Tan"),
            (1, 6, 2.00,  "Used 2 spools of French waxed linen thread"),
            (2, 1, 75.00, "Used 75 sq ft for 15 briefcases"),
            (2, 4, 30.00, "30 solid brass buckles and D-rings"),
            (2, 5, 15.00, "15 YKK antique brass zippers"),
            (3, 1, 20.00, "20 sq ft for cardholders"),
            (3, 6, 1.00,  "1 spool waxed thread"),
            (4, 1, 40.00, "Heavy strap leather 40 sq ft"),
            (4, 4, 50.00, "50 brass roller buckles"),
            (5, 1, 80.00, "80 sq ft for weekender duffels"),
            (5, 5, 20.00, "20 heavy dual-pull zippers"),
            (6, 1, 60.00, "60 sq ft chestnut leather"),
            (6, 9, 10.00, "10 packs brass rivets"),
            (7, 2, 50.00, "50 sq ft buffalo leather"),
            (8, 3, 25.00, "25 sq ft calfskin and microfiber backing")
        ]
        cur.executemany("INSERT INTO ProductionMaterials (ProductionID, MaterialID, QuantityUsed, Remarks) VALUES (?, ?, ?, ?);", production_materials_seed)

        finished_products_seed = [
            (1, 1, 30, 45.00, 1350.00),
            (2, 4, 15, 180.00, 2700.00),
            (3, 2, 40, 20.00, 800.00),
            (4, 7, 50, 32.00, 1600.00),
            (5, 9, 10, 220.00, 2200.00),
            (6, 6, 25, 110.00, 2750.00),
            (7, 13, 8, 260.00, 2080.00),
            (8, 12, 30, 40.00, 1200.00)
        ]
        cur.executemany("INSERT INTO FinishedProducts (ProductionID, ProductID, QuantityProduced, UnitCost, ProductionCost) VALUES (?, ?, ?, ?, ?);", finished_products_seed)

        customers_data = [
            ("Alexander Hayes", "+1-415-555-0142", "a.hayes@sfcapital.com", "452 Montgomery St", "San Francisco", "California", "94104", "2026-06-12"),
            ("Claire Beauchamp", "+1-212-555-0198", "claire.b@luxuryedit.com", "740 Park Avenue", "New York", "New York", "10021", "2026-06-25"),
            ("Rohan Singhania", "+91-98200-55443", "rohan@singhaniagroup.in", "18 Altamount Road", "Mumbai", "Maharashtra", "400026", "2026-07-02"),
            ("Sir Evelyn Montgomery", "+44-20-7946-0811", "evelyn@montgomeryestate.co.uk", "14 Belgrave Square", "London", "Greater London", "SW1X 8PS", "2026-07-15"),
            ("Sebastian Richter", "+49-89-1234889", "s.richter@munich-advisors.de", "Maximilianstrasse 22", "Munich", "Bavaria", "80539", "2026-07-28"),
            ("Ananya Deshmukh", "+91-98450-99887", "ananya.d@techbangalore.io", "88 Lavelle Road", "Bangalore", "Karnataka", "560001", "2026-08-04"),
            ("Harrison Thorne", "+1-312-555-0174", "h.thorne@chicagolaw.com", "300 N LaSalle St", "Chicago", "Illinois", "60654", "2026-08-11"),
            ("Genevieve Dubois", "+33-1-4268-5500", "genevieve@dubois-art.fr", "12 Place Vendôme", "Paris", "Île-de-France", "75001", "2026-08-19"),
            ("David Sterling", "+1-512-555-0133", "david@sterlingventures.com", "1200 S Congress Ave", "Austin", "Texas", "78704", "2026-08-28"),
            ("Pooja Nair", "+91-99400-33221", "pooja.nair@chennaidesign.in", "45 Boat Club Road", "Chennai", "Tamil Nadu", "600028", "2026-09-05"),
            ("Oliver Bennett", "+1-206-555-0165", "oliver.b@seattlecraft.org", "1500 Pike Place", "Seattle", "Washington", "98101", "2026-09-12"),
            ("Matteo Barone", "+39-02-8877665", "m.barone@milanomoda.it", "Via Montenapoleone 8", "Milan", "Lombardy", "20121", "2026-09-18")
        ]
        cur.executemany("INSERT INTO Customers (CustomerName, Phone, Email, Address, City, State, Pincode, JoinedDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", customers_data)

        leads_data = [
            ("Jonathan Archer", "+1-214-555-0111", "j.archer@enterprise.com", "Instagram Ads", "2026-09-10", "Qualified"),
            ("Kavita Mehta", "+91-98110-44332", "kavita.m@delhicouture.in", "Luxury Craft Fair", "2026-09-12", "Converted"),
            ("Henrietta Clark", "+44-7700-900555", "h.clark@oxfordalumni.org", "Google Search", "2026-09-15", "Contacted"),
            ("Vikramaditya Rao", "+91-97000-88112", "v.rao@hyderabadtech.com", "Website Signup", "2026-09-18", "New"),
            ("Charlotte Laurent", "+33-6-1234-5678", "c.laurent@bordeauxwine.fr", "Instagram Ads", "2026-09-22", "Qualified"),
            ("Brandon Walsh", "+1-310-555-0129", "b.walsh@beverlyhills.net", "Referral", "2026-09-25", "Contacted")
        ]
        cur.executemany("INSERT INTO Leads (LeadName, Phone, Email, Source, LeadDate, Status) VALUES (?, ?, ?, ?, ?, ?);", leads_data)

        crm_interactions_data = [
            (1, "Phone Call", "Custom Monogram Inquiry", "Customer requested golden debossed initials 'A.H.' on the briefcase lid.", "2026-08-15 14:30:00", "2026-08-18", "Julian Croft"),
            (2, "WhatsApp Chat", "Leather Swatch Request", "Sent physical swatch kit for Tan vs Chestnut tote options.", "2026-08-20 11:15:00", "2026-08-24", "Julian Croft"),
            (3, "Email Newsletter", "VIP Autumn Collection Preview", "Engaged with promotional preview, clicked on weekender duffel.", "2026-09-01 09:00:00", None, "System Marketing"),
            (4, "Phone Call", "Bespoke Luggage Set Consultation", "Discussed matching 3-piece luggage set in Cognac leather.", "2026-09-10 16:45:00", "2026-09-20", "Victoria Vance"),
            (7, "Support Ticket", "Belt Sizing Guidance", "Assisted client in sizing up from 34\" to 36\" for waist size 33.", "2026-09-14 10:20:00", None, "Derek O'Connor"),
            (9, "WhatsApp Chat", "Corporate Gifting Inquiry", "Requested quote for 25 custom debossed bifold wallets for tech summit.", "2026-09-22 13:00:00", "2026-10-05", "Sofia Morales")
        ]
        cur.executemany("INSERT INTO CRM_Interactions (CustomerID, InteractionType, Subject, Description, InteractionDate, NextFollowUpDate, CreatedBy) VALUES (?, ?, ?, ?, ?, ?, ?);", crm_interactions_data)

        discounts_data = [
            ("LEATHERLUX10", "Percentage", 10.00, 100.00, "2026-08-01", "2026-12-31", 1),
            ("CRAFT20", "Percentage", 20.00, 250.00, "2026-09-01", "2026-10-31", 1),
            ("HERITAGE50", "Fixed Amount", 50.00, 400.00, "2026-08-15", "2026-11-30", 1),
            ("WELCOME15", "Percentage", 15.00, 50.00, "2026-01-01", "2026-12-31", 1)
        ]
        cur.executemany("INSERT INTO Discounts_Promotions (Code, DiscountType, DiscountValue, MinOrderAmount, StartDate, EndDate, IsActive) VALUES (?, ?, ?, ?, ?, ?, ?);", discounts_data)

        orders_seed = [
            (1, "2026-08-16 10:30:00", "Delivered", 480.00, 48.00, 0.00, 432.00),
            (2, "2026-08-22 15:45:00", "Delivered", 290.00, 0.00, 0.00, 290.00),
            (3, "2026-08-28 12:10:00", "Delivered", 695.00, 50.00, 0.00, 645.00),
            (4, "2026-09-03 09:15:00", "Delivered", 580.00, 58.00, 0.00, 522.00),
            (5, "2026-09-08 14:20:00", "Delivered", 170.00, 17.00, 15.00, 168.00),
            (6, "2026-09-12 11:05:00", "Shipped",   360.00, 0.00, 0.00, 360.00),
            (7, "2026-09-15 16:30:00", "Delivered", 85.00, 0.00, 15.00, 100.00),
            (8, "2026-09-19 13:40:00", "Shipped",   780.00, 78.00, 0.00, 702.00),
            (9, "2026-09-22 18:00:00", "Processing", 1150.00, 100.00, 0.00, 1050.00),
            (10, "2026-09-24 10:15:00", "Processing", 230.00, 23.00, 0.00, 207.00),
            (11, "2026-09-26 14:50:00", "Pending",   690.00, 69.00, 0.00, 621.00),
            (12, "2026-09-28 17:20:00", "Delivered", 470.00, 47.00, 0.00, 423.00)
        ]
        cur.executemany("INSERT INTO Orders (CustomerID, OrderDate, OrderStatus, TotalAmount, DiscountAmount, ShippingAmount, GrandTotal) VALUES (?, ?, ?, ?, ?, ?, ?);", orders_seed)

        order_details_seed = [
            (1, 9, 1, 480.00, 48.00, 432.00),
            (2, 13, 1, 290.00, 0.00, 290.00),
            (3, 21, 1, 580.00, 50.00, 530.00),
            (3, 1, 1, 115.00, 0.00, 115.00),
            (4, 21, 1, 580.00, 58.00, 522.00),
            (5, 7, 1, 95.00, 10.00, 85.00),
            (5, 15, 1, 85.00, 7.00, 78.00),
            (6, 11, 1, 360.00, 0.00, 360.00),
            (7, 15, 1, 85.00, 0.00, 85.00),
            (8, 31, 1, 780.00, 78.00, 702.00),
            (9, 10, 2, 500.00, 50.00, 950.00),
            (9, 27, 1, 150.00, 50.00, 100.00),
            (10, 1, 2, 115.00, 23.00, 207.00),
            (11, 29, 1, 690.00, 69.00, 621.00),
            (12, 9, 1, 480.00, 47.00, 433.00)
        ]
        cur.executemany("INSERT INTO OrderDetails (OrderID, VariantID, Quantity, UnitPrice, Discount, TotalPrice) VALUES (?, ?, ?, ?, ?, ?);", order_details_seed)

        payments_seed = [
            (1, "2026-08-16 10:32:00", "Credit Card", 432.00, "TXN-AMEX-998811", "Success"),
            (2, "2026-08-22 15:47:00", "Credit Card", 290.00, "TXN-VISA-443322", "Success"),
            (3, "2026-08-28 12:12:00", "UPI / QR", 645.00, "TXN-UPI-771122@hdfc", "Success"),
            (4, "2026-09-03 09:17:00", "PayPal", 522.00, "TXN-PP-00998877", "Success"),
            (5, "2026-09-08 14:22:00", "Credit Card", 168.00, "TXN-MC-665544", "Success"),
            (6, "2026-09-12 11:08:00", "Net Banking", 360.00, "TXN-NB-332211", "Success"),
            (7, "2026-09-15 16:32:00", "Credit Card", 100.00, "TXN-VISA-112299", "Success"),
            (8, "2026-09-19 13:42:00", "Credit Card", 702.00, "TXN-AMEX-554477", "Success"),
            (9, "2026-09-22 18:05:00", "Credit Card", 1050.00, "TXN-VISA-887766", "Success"),
            (10, "2026-09-24 10:18:00", "UPI / QR", 207.00, "TXN-UPI-994400@icici", "Success"),
            (11, "2026-09-26 14:52:00", "Credit Card", 621.00, "TXN-MC-334411", "Pending"),
            (12, "2026-09-28 17:22:00", "Credit Card", 423.00, "TXN-VISA-778899", "Success")
        ]
        cur.executemany("INSERT INTO Payments (OrderID, PaymentDate, PaymentMethod, Amount, TransactionID, PaymentStatus) VALUES (?, ?, ?, ?, ?, ?);", payments_seed)

        shipments_seed = [
            (1, "2026-08-17", "DHL Luxury Freight", "DHL-EXP-900188", "452 Montgomery St, San Francisco, CA 94104", "Delivered", "2026-08-20"),
            (2, "2026-08-23", "FedEx Express", "FDX-77441122", "740 Park Avenue, New York, NY 10021", "Delivered", "2026-08-25"),
            (3, "2026-08-29", "BlueDart Express", "BD-EXP-332211", "18 Altamount Road, Mumbai, MH 400026", "Delivered", "2026-08-31"),
            (4, "2026-09-04", "DHL Luxury Freight", "DHL-EXP-900244", "14 Belgrave Square, London SW1X 8PS", "Delivered", "2026-09-07"),
            (5, "2026-09-09", "DHL Luxury Freight", "DHL-EXP-900311", "Maximilianstrasse 22, Munich 80539", "Delivered", "2026-09-12"),
            (6, "2026-09-13", "BlueDart Express", "BD-EXP-445566", "88 Lavelle Road, Bangalore 560001", "In Transit", None),
            (7, "2026-09-16", "FedEx Express", "FDX-88990011", "300 N LaSalle St, Chicago, IL 60654", "Delivered", "2026-09-18"),
            (8, "2026-09-20", "DHL Luxury Freight", "DHL-EXP-900455", "12 Place Vendôme, Paris 75001", "In Transit", None),
            (12, "2026-09-29", "DHL Luxury Freight", "DHL-EXP-900599", "Via Montenapoleone 8, Milan 20121", "Delivered", "2026-09-30")
        ]
        cur.executemany("INSERT INTO Shipments (OrderID, ShippingDate, CourierName, TrackingNo, ShippingAddress, DeliveryStatus, DeliveredDate) VALUES (?, ?, ?, ?, ?, ?, ?);", shipments_seed)

        returns_seed = [
            (7, 9, "2026-09-20", "Belt was 2 inches larger than anticipated for client trousers.", "Refund Processed", 85.00),
            (5, 7, "2026-09-15", "Customer requested exchange for Saddle Tan passport sleeve instead of Black.", "Approved", 0.00)
        ]
        cur.executemany("INSERT INTO Returns (OrderID, OrderDetailID, ReturnDate, Reason, ReturnStatus, RefundAmount) VALUES (?, ?, ?, ?, ?, ?);", returns_seed)

        expenses_seed = [
            ("2026-08-01", "Raw Materials", "Tuscan Tannery bulk cowhide hide shipment invoice #IT-881", 3850.00, "Tuscan Heritage Tannery", "Bank Transfer"),
            ("2026-08-05", "Raw Materials", "Ganges Prime crazy horse leather procurement", 2400.00, "Ganges Prime Leather Works", "Bank Transfer"),
            ("2026-08-10", "Hardware & Components", "Solid brass buckles and rivet lot batch #992", 1150.00, "Solid Brass & Hardware Foundry", "Credit Card"),
            ("2026-08-15", "Artisan Wages", "Artisan wages for Marco Bellini & Rajesh Sharma (Bi-weekly)", 2450.00, "Artisan Guild Payroll", "Bank Transfer"),
            ("2026-08-20", "Shipping & Freight", "DHL Express international courier charges August batch", 620.00, "DHL Worldwide Express", "Credit Card"),
            ("2026-08-25", "Marketing & Branding", "Instagram Sponsored Ads & High-Res Lookbook Campaign", 850.00, "Meta Ads Inc.", "Credit Card"),
            ("2026-08-30", "Workshop Utilities", "Workshop electricity, HVAC and burnishing tool maintenance", 420.00, "City Energy Grid", "Direct Debit"),
            ("2026-09-02", "Raw Materials", "Grade A Veg-Tanned leather restock #IT-914", 4200.00, "Tuscan Heritage Tannery", "Bank Transfer"),
            ("2026-09-15", "Artisan Wages", "Artisan guild wages mid-September cycle", 2800.00, "Artisan Guild Payroll", "Bank Transfer"),
            ("2026-09-20", "Packaging & Boxes", "Debossed gold foil luxury rigid gift boxes (500 units)", 750.00, "Custom Luxe Packaging Ltd", "Bank Transfer"),
            ("2026-09-25", "Shipping & Freight", "Air freight and customs duty clearance for European exports", 590.00, "DHL Luxury Freight", "Credit Card")
        ]
        cur.executemany("INSERT INTO Expenses (ExpenseDate, ExpenseType, Description, Amount, PaidTo, PaymentMethod) VALUES (?, ?, ?, ?, ?, ?);", expenses_seed)

        conn.commit()
        conn.close()
        print("[SUCCESS] Database initialized with all 24 tables and mock data.")

    def get_connection(self):
        if self.is_postgres and self.pg_pool:
            conn = self.pg_pool.getconn()
            try:
                conn.autocommit = True
            except Exception:
                pass
            return conn
        elif self.is_postgres:
            conn = psycopg2.connect(self.conn_str)
            try:
                conn.autocommit = True
            except Exception:
                pass
            return conn
        else:
            conn = sqlite3.connect(LOCAL_SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            return conn

    def release_connection(self, conn):
        if self.is_postgres and self.pg_pool:
            try:
                if not conn.closed:
                    if hasattr(conn, 'status') and conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
                        conn.commit()
                self.pg_pool.putconn(conn)
            except Exception:
                try:
                    self.pg_pool.putconn(conn, close=True)
                except Exception:
                    pass
        else:
            try:
                conn.close()
            except Exception:
                pass

    def execute_raw_query(self, sql_query):
        """Executes any raw SQL query and returns column names, rows, runtime and rowcount."""
        start_time = time.time()
        
        # Simple cross-compatibility transformations if running on SQLite
        query_to_run = sql_query
        if not self.is_postgres:
            query_to_run = (query_to_run
                .replace("::NUMERIC", "")
                .replace("NULLS LAST", "")
                .replace("TO_CHAR(OrderDate, 'YYYY-MM')", "strftime('%Y-%m', OrderDate)")
                .replace("TO_CHAR(ExpenseDate, 'YYYY-MM')", "strftime('%Y-%m', ExpenseDate)")
                .replace("CURRENT_DATE", "date('now')")
            )

        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query_to_run)
            
            runtime_ms = round((time.time() - start_time) * 1000, 2)
            
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                if self.is_postgres:
                    formatted_rows = [list(r) for r in rows]
                else:
                    formatted_rows = [[item for item in r] for r in rows]
                
                # Format dates and decimals for JSON serialization
                serializable_rows = []
                for row in formatted_rows:
                    cleaned_row = []
                    for val in row:
                        if isinstance(val, (datetime.date, datetime.datetime)):
                            cleaned_row.append(str(val))
                        elif hasattr(val, '__float__') and not isinstance(val, (int, bool)):
                            cleaned_row.append(round(float(val), 2))
                        else:
                            cleaned_row.append(val)
                    serializable_rows.append(cleaned_row)

                return {
                    "success": True,
                    "columns": columns,
                    "rows": serializable_rows,
                    "rowCount": len(serializable_rows),
                    "executionTimeMs": runtime_ms,
                    "engine": "Supabase PostgreSQL"
                }
            else:
                conn.commit()
                return {
                    "success": True,
                    "columns": ["Result"],
                    "rows": [["Query executed successfully. Impacted rows: " + str(cur.rowcount)]],
                    "rowCount": cur.rowcount,
                    "executionTimeMs": runtime_ms,
                    "engine": "Supabase PostgreSQL"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "executionTimeMs": round((time.time() - start_time) * 1000, 2),
                "engine": "Supabase PostgreSQL"
            }
        finally:
            cur.close()
            self.release_connection(conn)

    def invalidate_caches(self):
        """Clears all in-memory query caches upon database mutations."""
        self._kpis_cache = None
        self._charts_cache = None
        self._lookup_cache = None
        self._table_meta_cache = None

    def get_kpis(self, force_refresh=False):
        """Calculates executive KPI metrics in a single network roundtrip with caching."""
        now = time.time()
        if not force_refresh and hasattr(self, '_kpis_cache') and self._kpis_cache and (now - getattr(self, '_kpis_cache_time', 0)) < 15:
            return self._kpis_cache

        q_single = """
            SELECT 
                (SELECT COALESCE(SUM(GrandTotal), 0) FROM Orders WHERE OrderStatus != 'Cancelled') AS rev,
                (SELECT COUNT(*) FROM Orders) AS orders,
                (SELECT COUNT(*) FROM Artisans WHERE Status = 'Active') AS artisans,
                (SELECT COUNT(*) FROM Production WHERE Status IN ('In Progress', 'Scheduled')) AS batches,
                (SELECT COALESCE(SUM(Amount), 0) FROM Expenses) AS expenses,
                (SELECT COALESCE(SUM(i.QuantityInHand * p.SellingPrice), 0) FROM Inventory i JOIN ProductVariants pv ON i.VariantID = pv.VariantID JOIN Products p ON pv.ProductID = p.ProductID) AS inv_val,
                (SELECT COUNT(*) FROM Inventory WHERE (QuantityInHand - ReservedQuantity) < ReorderLevel) AS low_stock,
                (SELECT COUNT(*) FROM Customers) AS customers,
                (SELECT COUNT(*) FROM Leads) AS leads;
        """
        res = self.execute_raw_query(q_single)
        if res.get("success") and res.get("rows"):
            r = res["rows"][0]
            total_rev = float(r[0] or 0.0)
            total_orders = int(r[1] or 0)
            active_artisans = int(r[2] or 0)
            active_batches = int(r[3] or 0)
            total_exp = float(r[4] or 0.0)
            inv_val = float(r[5] or 0.0)
            low_stock = int(r[6] or 0)
            total_cust = int(r[7] or 0)
            total_leads = int(r[8] or 0)
            net_profit = total_rev - total_exp

            result = {
                "totalRevenue": round(total_rev, 2),
                "totalExpenses": round(total_exp, 2),
                "netProfit": round(net_profit, 2),
                "totalOrders": total_orders,
                "activeArtisans": active_artisans,
                "activeBatches": active_batches,
                "inventoryValuation": round(inv_val, 2),
                "lowStockAlerts": low_stock,
                "totalCustomers": total_cust,
                "totalLeads": total_leads,
                "dbEngine": "Supabase PostgreSQL"
            }
            self._kpis_cache = result
            self._kpis_cache_time = now
            return result

        # Fallback if single query fails
        return {
            "totalRevenue": 0.0,
            "totalExpenses": 0.0,
            "netProfit": 0.0,
            "totalOrders": 0,
            "activeArtisans": 0,
            "activeBatches": 0,
            "inventoryValuation": 0.0,
            "lowStockAlerts": 0,
            "totalCustomers": 0,
            "totalLeads": 0,
            "dbEngine": "Supabase PostgreSQL"
        }

    def get_charts_data(self, force_refresh=False):
        """Fetches aggregated data for charts with caching."""
        now = time.time()
        if not force_refresh and hasattr(self, '_charts_cache') and self._charts_cache and (now - getattr(self, '_charts_cache_time', 0)) < 30:
            return self._charts_cache

        # 1. Category Revenue
        cat_query = """
            SELECT c.CategoryName, ROUND(SUM(od.TotalPrice), 2) as revenue
            FROM Categories c
            JOIN Products p ON c.CategoryID = p.CategoryID
            JOIN ProductVariants pv ON p.ProductID = pv.ProductID
            JOIN OrderDetails od ON pv.VariantID = od.VariantID
            GROUP BY c.CategoryName
            ORDER BY revenue DESC;
        """
        cat_data = self.execute_raw_query(cat_query)

        # 2. Artisan Output
        art_query = """
            SELECT a.ArtisanName, COALESCE(SUM(fp.QuantityProduced), 0) as units
            FROM Artisans a
            LEFT JOIN Production pr ON a.ArtisanID = pr.ArtisanID
            LEFT JOIN FinishedProducts fp ON pr.ProductionID = fp.ProductionID
            GROUP BY a.ArtisanName
            ORDER BY units DESC;
        """
        art_data = self.execute_raw_query(art_query)

        # 3. Order Status Breakdown
        status_query = "SELECT OrderStatus, COUNT(*) FROM Orders GROUP BY OrderStatus;"
        status_data = self.execute_raw_query(status_query)

        # 4. Expense Breakdown
        exp_query = "SELECT ExpenseType, ROUND(SUM(Amount), 2) FROM Expenses GROUP BY ExpenseType ORDER BY SUM(Amount) DESC;"
        exp_data = self.execute_raw_query(exp_query)

        # 5. Leads by Source
        leads_query = "SELECT Source, COUNT(*) FROM Leads GROUP BY Source;"
        leads_data = self.execute_raw_query(leads_query)

        # 6. Inventory Stock by Variant
        inv_query = """
            SELECT (p.ProductName || ' (' || pv.Color || ')') as item_name, i.QuantityInHand, i.ReorderLevel
            FROM Inventory i
            JOIN ProductVariants pv ON i.VariantID = pv.VariantID
            JOIN Products p ON pv.ProductID = p.ProductID
            LIMIT 10;
        """
        inv_data = self.execute_raw_query(inv_query)

        result = {
            "categories": cat_data.get("rows", []),
            "artisans": art_data.get("rows", []),
            "orderStatuses": status_data.get("rows", []),
            "expenses": exp_data.get("rows", []),
            "leadSources": leads_data.get("rows", []),
            "inventory": inv_data.get("rows", [])
        }
        self._charts_cache = result
        self._charts_cache_time = now
        return result

    def get_table_metadata(self, force_refresh=False):
        """Returns list of tables and their row counts with caching."""
        now = time.time()
        if not force_refresh and hasattr(self, '_table_meta_cache') and self._table_meta_cache and (now - getattr(self, '_table_meta_cache_time', 0)) < 30:
            return self._table_meta_cache

        tables = [
            ("Suppliers", "Supply & Procurement"),
            ("RawMaterials", "Supply & Procurement"),
            ("Purchases", "Supply & Procurement"),
            ("PurchaseDetails", "Supply & Procurement"),
            ("Artisans", "Manufacturing"),
            ("Production", "Manufacturing"),
            ("ProductionMaterials", "Manufacturing"),
            ("FinishedProducts", "Manufacturing"),
            ("Categories", "Inventory & Products"),
            ("Products", "Inventory & Products"),
            ("ProductVariants", "Inventory & Products"),
            ("Inventory", "Inventory & Products"),
            ("Orders", "Sales & E-Commerce"),
            ("OrderDetails", "Sales & E-Commerce"),
            ("Payments", "Sales & E-Commerce"),
            ("Shipments", "Sales & E-Commerce"),
            ("Returns", "Sales & E-Commerce"),
            ("Discounts_Promotions", "Sales & E-Commerce"),
            ("Customers", "Customer & CRM"),
            ("Leads", "Customer & CRM"),
            ("CRM_Interactions", "Customer & CRM"),
            ("Employees", "Master & Support"),
            ("Expenses", "Master & Support"),
            ("Addresses", "Master & Support"),
            ("Settings", "Master & Support")
        ]
        
        result = []
        if self.is_postgres:
            try:
                count_query = " UNION ALL ".join([f"SELECT '{tbl}' AS tbl, COUNT(*) AS cnt FROM {tbl}" for tbl, _ in tables])
                cnt_res = self.execute_raw_query(count_query)
                if cnt_res.get("success"):
                    counts_map = {r[0]: r[1] for r in cnt_res.get("rows", [])}
                    result = [{
                        "name": tbl,
                        "module": mod,
                        "rowCount": counts_map.get(tbl, 0)
                    } for tbl, mod in tables]
                    self._table_meta_cache = result
                    self._table_meta_cache_time = now
                    return result
            except Exception:
                pass

        for tbl, mod in tables:
            cnt_res = self.execute_raw_query(f"SELECT COUNT(*) FROM {tbl};")
            count = cnt_res["rows"][0][0] if cnt_res["success"] and cnt_res["rows"] else 0
            result.append({
                "name": tbl,
                "module": mod,
                "rowCount": count
            })
        self._table_meta_cache = result
        self._table_meta_cache_time = now
        return result

    def get_lookup_options(self, force_refresh=False):
        """Fetches human-readable labels for all foreign key relations."""
        if not force_refresh and hasattr(self, '_lookup_cache') and self._lookup_cache and (time.time() - getattr(self, '_lookup_cache_time', 0)) < 60:
            return self._lookup_cache

        lookups = {}
        
        # 1. Categories
        cat_res = self.execute_raw_query("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryName;")
        lookups["CategoryID"] = [{"id": r[0], "label": r[1]} for r in cat_res.get("rows", [])]

        # 2. Suppliers
        sup_res = self.execute_raw_query("SELECT SupplierID, SupplierName, City FROM Suppliers ORDER BY SupplierName;")
        lookups["SupplierID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]})"} for r in sup_res.get("rows", [])]

        # 3. Artisans
        art_res = self.execute_raw_query("SELECT ArtisanID, ArtisanName, Specialization FROM Artisans ORDER BY ArtisanName;")
        lookups["ArtisanID"] = [{"id": r[0], "label": f"{r[1]} - {r[2]}"} for r in art_res.get("rows", [])]

        # 4. Products
        prd_res = self.execute_raw_query("SELECT ProductID, ProductName, SellingPrice FROM Products ORDER BY ProductName;")
        lookups["ProductID"] = [{"id": r[0], "label": f"{r[1]} (${r[2]})"} for r in prd_res.get("rows", [])]

        # 5. ProductVariants
        var_res = self.execute_raw_query("SELECT pv.VariantID, p.ProductName, pv.Color, pv.SKU FROM ProductVariants pv JOIN Products p ON pv.ProductID = p.ProductID ORDER BY p.ProductName;")
        lookups["VariantID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]} / {r[3]})"} for r in var_res.get("rows", [])]

        # 6. RawMaterials
        mat_res = self.execute_raw_query("SELECT MaterialID, MaterialName, Unit FROM RawMaterials ORDER BY MaterialName;")
        lookups["MaterialID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]})"} for r in mat_res.get("rows", [])]

        # 7. Customers
        cst_res = self.execute_raw_query("SELECT CustomerID, CustomerName, City FROM Customers ORDER BY CustomerName;")
        lookups["CustomerID"] = [{"id": r[0], "label": f"{r[1]} - {r[2]}"} for r in cst_res.get("rows", [])]

        # 8. Orders
        ord_res = self.execute_raw_query("SELECT o.OrderID, c.CustomerName, o.GrandTotal, o.OrderStatus FROM Orders o JOIN Customers c ON o.CustomerID = c.CustomerID ORDER BY o.OrderID DESC;")
        lookups["OrderID"] = [{"id": r[0], "label": f"Order #{r[0]} - {r[1]} (${r[2]} - {r[3]})"} for r in ord_res.get("rows", [])]

        # 9. Production Batches
        prb_res = self.execute_raw_query("SELECT ProductionID, BatchNo, Status FROM Production ORDER BY ProductionID DESC;")
        lookups["ProductionID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]})"} for r in prb_res.get("rows", [])]

        # 10. Purchases
        pur_res = self.execute_raw_query("SELECT p.PurchaseID, s.SupplierName, p.TotalAmount FROM Purchases p JOIN Suppliers s ON p.SupplierID = s.SupplierID ORDER BY p.PurchaseID DESC;")
        lookups["PurchaseID"] = [{"id": r[0], "label": f"PO #{r[0]} - {r[1]} (${r[2]})"} for r in pur_res.get("rows", [])]

        # 11. OrderDetails
        odt_res = self.execute_raw_query("SELECT od.OrderDetailID, o.OrderID, p.ProductName, pv.Color FROM OrderDetails od JOIN Orders o ON od.OrderID = o.OrderID JOIN ProductVariants pv ON od.VariantID = pv.VariantID JOIN Products p ON pv.ProductID = p.ProductID ORDER BY od.OrderDetailID DESC;")
        lookups["OrderDetailID"] = [{"id": r[0], "label": f"Line #{r[0]} (Order #{r[1]} - {r[2]} {r[3]})"} for r in odt_res.get("rows", [])]

        # 12. Addresses
        adr_res = self.execute_raw_query("SELECT AddressID, AddressLine1, City, AddressType FROM Addresses ORDER BY AddressID;")
        lookups["AddressID"] = [{"id": r[0], "label": f"{r[1]}, {r[2]} ({r[3]})"} for r in adr_res.get("rows", [])]

        # 13. Employees
        emp_res = self.execute_raw_query("SELECT EmployeeID, EmployeeName, Designation FROM Employees ORDER BY EmployeeName;")
        lookups["EmployeeID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]})"} for r in emp_res.get("rows", [])]

        # 14. Leads
        led_res = self.execute_raw_query("SELECT LeadID, LeadName, Source, Status FROM Leads ORDER BY LeadName;")
        lookups["LeadID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]} - {r[3]})"} for r in led_res.get("rows", [])]

        # 15. Discounts & Promotions
        dsc_res = self.execute_raw_query("SELECT DiscountID, Code, DiscountType, DiscountValue FROM Discounts_Promotions ORDER BY Code;")
        lookups["DiscountID"] = [{"id": r[0], "label": f"{r[1]} ({r[2]} - {r[3]})"} for r in dsc_res.get("rows", [])]
        lookups["PromotionID"] = lookups["DiscountID"]

        # Static ENUM dropdown options
        lookups["ENUMS"] = {
            "OrderStatus": ["Pending", "Processing", "Handcrafted", "Shipped", "Delivered", "Cancelled"],
            "PaymentStatus": ["Success", "Pending", "Failed", "Refunded"],
            "PaymentMethod": ["Credit Card", "UPI / QR", "PayPal", "Net Banking", "COD", "Bank Transfer", "Direct Debit"],
            "DeliveryStatus": ["Dispatched", "In Transit", "Out for Delivery", "Delivered", "Returned"],
            "ReturnStatus": ["Requested", "Approved", "Item Received", "Refund Processed", "Rejected"],
            "Status": ["Active", "On Leave", "Inactive", "Resigned"],
            "LeadStatus": ["New", "Contacted", "Qualified", "Converted", "Lost"],
            "Source": ["Instagram Ads", "Google Search", "Luxury Craft Fair", "Referral", "Website Signup"],
            "ExpenseType": ["Raw Materials", "Artisan Wages", "Hardware & Components", "Shipping & Freight", "Marketing & Branding", "Packaging & Boxes", "Workshop Utilities"],
            "MaterialType": ["Full Grain Leather", "Top Grain Leather", "Calfskin Leather", "Hardware/Brass", "Hardware/Zippers", "Hardware/Rivets", "Waxed Thread", "Adhesive & Edge Compound", "Conditioner/Oil", "Lining Fabric"],
            "Unit": ["Sq. Ft.", "Meters", "Pieces", "Kg", "Spools", "Litre", "Packs"],
            "Color": ["Saddle Tan", "Espresso Brown", "Obsidian Black", "Burgundy Wine", "Cognac Brown", "Warm Chestnut", "Vintage Brown", "Dark Brown"],
            "Size": ["Standard", "Small", "Medium", "Large", "34-Inch", "36-Inch", "38-Inch", "14-Inch", "15-Inch", "16-Inch", "45L Standard", "90x40cm"],
            "DiscountType": ["Percentage", "Fixed Amount"],
            "CourierName": ["BlueDart Express", "DHL Luxury Freight", "FedEx Express", "Delhivery"],
            "InteractionType": ["Phone Call", "WhatsApp Chat", "Email Newsletter", "Custom Monogram Inquiry", "Support Ticket", "Bespoke Consultation"],
            "AddressType": ["Shipping", "Billing", "Warehouse", "Supplier", "Workshop", "HQ"]
        }

        self._lookup_cache = lookups
        self._lookup_cache_time = time.time()
        return lookups

    def get_table_schema(self, table_name):
        """Returns column definitions, primary key, and foreign key options for dynamic UI form dropdowns."""
        if not hasattr(self, '_schema_cache'):
            self._schema_cache = {}
        if table_name.lower() in self._schema_cache:
            return self._schema_cache[table_name.lower()]

        pk_col = TABLE_PRIMARY_KEYS_LOWER.get(table_name.lower(), "id")
        
        # Get sample row description
        meta = self.execute_raw_query(f"SELECT * FROM {table_name} LIMIT 1;")
        columns = meta.get("columns", [])
        
        all_lookups = self.get_lookup_options()
        enums = all_lookups.get("ENUMS", {})

        lookup_map_lower = {k.lower(): v for k, v in all_lookups.items() if k != "ENUMS"}
        enums_map_lower = {k.lower(): v for k, v in enums.items()}

        col_list = []
        for col in columns:
            lower_c = col.lower()
            is_pk = (lower_c == pk_col.lower())
            col_type = "text"
            lookup_options = None
            is_fk = False

            if is_pk:
                col_type = "pk"
            elif lower_c in lookup_map_lower:
                col_type = "select"
                is_fk = True
                lookup_options = lookup_map_lower[lower_c]
            elif lower_c in enums_map_lower:
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums_map_lower[lower_c]]
            elif "status" in lower_c:
                matched_enum = None
                for ek, ev in enums.items():
                    if ek.lower() in lower_c:
                        matched_enum = ev
                        break
                if matched_enum:
                    col_type = "select"
                    lookup_options = [{"id": opt, "label": opt} for opt in matched_enum]
                else:
                    col_type = "select"
                    lookup_options = [{"id": opt, "label": opt} for opt in enums.get("Status", ["Active", "Inactive"])]
            elif "method" in lower_c:
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums.get("PaymentMethod", [])]
            elif "courier" in lower_c:
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums.get("CourierName", [])]
            elif "source" in lower_c:
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums.get("Source", [])]
            elif "type" in lower_c:
                matched_type = None
                for ek, ev in enums.items():
                    if ek.lower() in lower_c or lower_c in ek.lower():
                        matched_type = ev
                        break
                if matched_type:
                    col_type = "select"
                    lookup_options = [{"id": opt, "label": opt} for opt in matched_type]
            elif lower_c in ("unit", "unitofmeasure", "uom"):
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums.get("Unit", [])]
            elif "color" in lower_c:
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums.get("Color", [])]
            elif "size" in lower_c:
                col_type = "select"
                lookup_options = [{"id": opt, "label": opt} for opt in enums.get("Size", [])]
            elif "date" in lower_c:
                col_type = "date"
            elif "price" in lower_c or "amount" in lower_c or "cost" in lower_c or "rate" in lower_c or "margin" in lower_c or "total" in lower_c or "discount" in lower_c:
                col_type = "number"
            elif "quantity" in lower_c or "qty" in lower_c or "level" in lower_c or "units" in lower_c or "count" in lower_c:
                col_type = "number"
            elif "is" in lower_c or "active" in lower_c:
                col_type = "select"
                lookup_options = [{"id": 1, "label": "Active (True)"}, {"id": 0, "label": "Inactive (False)"}]
            
            col_list.append({
                "name": col,
                "type": col_type,
                "is_primary_key": is_pk,
                "is_foreign_key": is_fk,
                "options": lookup_options
            })

        res = {
            "tableName": table_name,
            "primaryKey": pk_col,
            "columns": col_list
        }
        self._schema_cache[table_name.lower()] = res
        return res

    def insert_row(self, table_name, data):
        """Creates a new record in the table."""
        pk_col = TABLE_PRIMARY_KEYS_LOWER.get(table_name.lower(), "id")
        # Remove PK if empty or auto-increment
        filtered_data = {k: v for k, v in data.items() if k.lower() != pk_col.lower() and v is not None and v != ""}
        
        cols = list(filtered_data.keys())
        vals = list(filtered_data.values())
        
        if not cols:
            raise ValueError("No valid column values provided for insert")

        placeholders = ", ".join(["%s" if self.is_postgres else "?" for _ in vals])
        col_names = ", ".join(cols)
        
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders});"
        
        conn = self.get_connection()
        try:
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute(sql, tuple(vals))
            conn.commit()
            conn.autocommit = True
            cur.close()
            self.release_connection(conn)
            self.invalidate_caches()
            return {"success": True, "message": f"New record added to {table_name} successfully!"}
        except Exception as e:
            try:
                conn.rollback()
                conn.autocommit = True
            except Exception:
                pass
            self.release_connection(conn)
            return {"success": False, "error": str(e)}

    def update_row(self, table_name, pk_value, data):
        """Updates an existing record by its primary key."""
        pk_col = TABLE_PRIMARY_KEYS_LOWER.get(table_name.lower(), "id")
        filtered_data = {}
        for k, v in data.items():
            if k.lower() == pk_col.lower():
                continue
            filtered_data[k] = None if (v == "" or v is None) else v
        
        if not filtered_data:
            raise ValueError("No fields to update")

        set_clauses = []
        vals = []
        for k, v in filtered_data.items():
            param_holder = "%s" if self.is_postgres else "?"
            set_clauses.append(f"{k} = {param_holder}")
            vals.append(v)
            
        vals.append(pk_value)
        pk_holder = "%s" if self.is_postgres else "?"
        
        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {pk_col} = {pk_holder};"
        
        conn = self.get_connection()
        try:
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute(sql, tuple(vals))
            conn.commit()
            conn.autocommit = True
            cur.close()
            self.release_connection(conn)
            self.invalidate_caches()
            return {"success": True, "message": f"Record updated in {table_name} successfully!"}
        except Exception as e:
            try:
                conn.rollback()
                conn.autocommit = True
            except Exception:
                pass
            self.release_connection(conn)
            return {"success": False, "error": str(e)}

    def delete_row(self, table_name, pk_value):
        """Deletes a record by its primary key."""
        pk_col = TABLE_PRIMARY_KEYS_LOWER.get(table_name.lower(), "id")
        pk_holder = "%s" if self.is_postgres else "?"
        sql = f"DELETE FROM {table_name} WHERE {pk_col} = {pk_holder};"
        
        conn = self.get_connection()
        try:
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute(sql, (pk_value,))
            conn.commit()
            conn.autocommit = True
            cur.close()
            self.release_connection(conn)
            self.invalidate_caches()
            return {"success": True, "message": f"Record #{pk_value} deleted from {table_name} successfully!"}
        except Exception as e:
            try:
                conn.rollback()
                conn.autocommit = True
            except Exception:
                pass
            self.release_connection(conn)
            return {"success": False, "error": str(e)}

# Global Instance
db = DatabaseManager()

