import os
import random
import datetime
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, connect_timeout=20)

def run_schema(cursor):
    print(" Executing schema_leather.sql to build tables...")
    with open("schema_leather.sql", "r", encoding="utf-8") as f:
        ddl = f.read()
    cursor.execute(ddl)
    print(" Database tables created successfully.")

def seed_database():
    conn = get_db_connection()
    conn.autocommit = False
    cur = conn.cursor()

    try:
        run_schema(cur)

        print("\n Seeding Master & Support Tables...")
        # 1. Settings
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
        cur.executemany("INSERT INTO Settings (SettingKey, SettingValue, Description) VALUES (%s, %s, %s);", settings_data)

        # 2. Addresses
        addresses_data = [
            ("Warehouse", "104 Artisan Boulevard", "Bay 4 Industrial Estate", "Florence", "Tuscany", "50123"),
            ("Workshop", "45 Tannery Row", "Suite 2B", "Kanpur", "Uttar Pradesh", "208001"),
            ("HQ", "742 Evergreen Terrace", "Floor 3", "Austin", "Texas", "78701"),
            ("Supplier Hub", "12 Santa Croce Way", "Depot 8", "Pisa", "Tuscany", "56121"),
            ("Shipping", "88 High Street", "Dock 1", "London", "Greater London", "EC1A 1BB")
        ]
        cur.executemany("INSERT INTO Addresses (AddressType, AddressLine1, AddressLine2, City, State, Pincode) VALUES (%s, %s, %s, %s, %s, %s);", addresses_data)

        # 3. Employees
        employees_data = [
            ("Victoria Vance", "Chief Operations Officer", "+1-512-555-0199", "v.vance@aethelgard.com", "Active"),
            ("Marcus Sterling", "Master Leather Guild Supervisor", "+1-512-555-0182", "m.sterling@aethelgard.com", "Active"),
            ("Aanya Sen", "Quality Assurance & Finishing Lead", "+91-98765-43210", "a.sen@aethelgard.com", "Active"),
            ("Julian Croft", "Head of E-Commerce & CRM", "+1-512-555-0144", "j.croft@aethelgard.com", "Active"),
            ("Derek O'Connor", "Procurement & Logistics Manager", "+1-512-555-0176", "d.oconnor@aethelgard.com", "Active"),
            ("Sofia Morales", "Digital Marketing & Brand Strategist", "+1-512-555-0163", "s.morales@aethelgard.com", "Active")
        ]
        cur.executemany("INSERT INTO Employees (EmployeeName, Designation, Phone, Email, Status) VALUES (%s, %s, %s, %s, %s);", employees_data)

        # 4. Suppliers
        suppliers_data = [
            ("Tuscan Heritage Tannery S.p.A.", "Giovanni Moretti", "+39-055-123456", "sales@tuscantannery.it", "Via del Cuoio 44", "Santa Croce sull'Arno", "Pisa", "IT98765432100"),
            ("Ganges Prime Leather Works", "Vikram Rathore", "+91-512-2345678", "exports@gangesleather.in", "Jajmau Industrial Area", "Kanpur", "Uttar Pradesh", "09AAACG1234F1Z8"),
            ("Solid Brass & Hardware Foundry", "Arthur Pendelton", "+44-20-7946-0912", "orders@solidbrasscraft.co.uk", "Forge Road 12", "Birmingham", "West Midlands", "GB123456789"),
            ("Coats & Clark Waxed Threads", "Clara Schmidt", "+49-30-891234", "service@coatsclark.de", "Fadenstrasse 9", "Stuttgart", "Baden-Württemberg", "DE812345678"),
            ("Fiebing's Leather Dye & Edge Balm", "Thomas Miller", "+1-414-555-0130", "supplies@fiebingsusa.com", "516 S 2nd St", "Milwaukee", "Wisconsin", "US391283912"),
            ("Pelle Naturale Organic Vegetable Leathers", "Matteo Ricci", "+39-055-789012", "matteo@pellenaturale.it", "Piazza Santa Croce 8", "Florence", "Tuscany", "IT11223344556")
        ]
        cur.executemany("INSERT INTO Suppliers (SupplierName, ContactPerson, Phone, Email, Address, City, State, GSTIN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", suppliers_data)

        # 5. Raw Materials
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
        cur.executemany("INSERT INTO RawMaterials (MaterialName, MaterialType, Unit, Description) VALUES (%s, %s, %s, %s);", raw_materials_data)

        # 6. Purchases & PurchaseDetails
        print(" Seeding Purchases & Procurement Details...")
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
        cur.executemany("INSERT INTO Purchases (SupplierID, PurchaseDate, TotalAmount, PaymentStatus) VALUES (%s, %s, %s, %s);", purchases_seed)

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
        cur.executemany("INSERT INTO PurchaseDetails (PurchaseID, MaterialID, Quantity, UnitPrice, TotalPrice) VALUES (%s, %s, %s, %s, %s);", purchase_details_seed)

        # 7. Artisans
        print(" Seeding Artisans & Master Craftsmen...")
        artisans_data = [
            ("Marco Bellini", "+39-340-1122334", "Master Saddle Stitcher & Bag Maker", 160.00, "Active"),
            ("Rajesh Kumar Sharma", "+91-94150-88776", "Pattern Cutting & Edge Burnishing", 110.00, "Active"),
            ("Elena Rostova", "+44-7700-900123", "Wallet & Small Leather Goods Artisan", 140.00, "Active"),
            ("Samuel K. Wright", "+1-512-555-0189", "Heavy Belt & Tooling Specialist", 150.00, "Active"),
            ("Anita Verma", "+91-98390-11223", "Lining, Hardware & Assembly Expert", 105.00, "Active"),
            ("Matteo Rossi", "+39-348-9988776", "Leather Dyeing & Vintage Patina Finisher", 155.00, "Active"),
            ("Liam Henderson", "+1-512-555-0177", "Embroidery & Laser Engraving Artisan", 130.00, "Active")
        ]
        cur.executemany("INSERT INTO Artisans (ArtisanName, Phone, Specialization, DailyRate, Status) VALUES (%s, %s, %s, %s, %s);", artisans_data)

        # 8. Categories & Products
        print(" Seeding Categories, Products & Variants...")
        categories_data = [
            ("Handcrafted Wallets", "Minimalist bifold, trifold, cardholders and passport sleeves crafted with full-grain leather.", "Active"),
            ("Luxury Bags & Briefcases", "Vegetable-tanned leather messenger bags, heritage briefcases and weekend duffels.", "Active"),
            ("Full-Grain Leather Belts", "Solid brass buckled heavy duty full-grain harness and dress belts.", "Active"),
            ("Leather Travel Gear", "Duffel bags, dopp kits, luggage tags and passport organizers.", "Active"),
            ("Desk & Tech Folios", "MacBook leather sleeves, iPad cases, mousepads and luxury desk mats.", "Active"),
            ("Leather Jackets & Vests", "Custom tailored genuine leather bomber, biker, and café racer jackets.", "Active")
        ]
        cur.executemany("INSERT INTO Categories (CategoryName, Description, Status) VALUES (%s, %s, %s);", categories_data)

        products_data = [
            # Category 1: Handcrafted Wallets
            (1, "The Heritage Bifold Wallet", "Classic 6-pocket vegetable-tanned leather bifold with hidden cash flap and hand-stitched edges.", 45.00, 115.00, True),
            (1, "The Slim Cardholder Sleeve", "Ultra-thin 4-slot minimalist leather cardholder with central cash stash.", 20.00, 55.00, True),
            (1, "The Passport Travel Wallet", "Full-grain passport holder with boarding pass pocket, card slots and pen loop.", 38.00, 95.00, True),
            # Category 2: Luxury Bags & Briefcases
            (2, "The Executive Briefcase 15\"", "Full-grain vegetable-tanned leather briefcase with solid brass hardware, laptop divider and key lanyard.", 180.00, 480.00, True),
            (2, "The Artisan Messenger Satchel", "Classic over-the-shoulder messenger bag with quick-release brass buckles and reinforced base.", 140.00, 360.00, True),
            (2, "The Florence Leather Tote Bag", "Spacious open-top women's tote handcrafted from pull-up cowhide with inner zipped pocket.", 110.00, 290.00, True),
            # Category 3: Full-Grain Leather Belts
            (3, "The Old-World Harness Belt 1.5\"", "Heavy 10 oz English bridle leather belt with solid cast brass roller buckle and beveled edges.", 32.00, 85.00, True),
            (3, "The Formal Feathered Dress Belt", "Slim 1.25\" vegetable-tanned calfskin belt with feathered edge profile and brushed nickel hardware.", 35.00, 95.00, True),
            # Category 4: Leather Travel Gear
            (4, "The Nomad Weekender Duffel 45L", "Flight-ready 45L luxury leather duffel with shoe compartment, luggage tag and heavy brass zippers.", 220.00, 580.00, True),
            (4, "The Master Dopp Kit / Toiletry Bag", "Water-resistant lined leather shaving kit bag with wide mouth frame opening.", 30.00, 80.00, True),
            # Category 5: Desk & Tech Folios
            (5, "The Executive Desk Pad Mat (Large)", "Smooth vegetable-tanned desk blotter with hand-burnished edges and non-slip backing.", 45.00, 120.00, True),
            (5, "The MacBook Pro Leather Folio Sleeve", "Snug fit padded leather folio with magnetic flap closure and plush microfiber lining.", 40.00, 110.00, True),
            # Category 6: Leather Jackets & Vests
            (6, "The Café Racer Moto Jacket", "Top-grain cowhide motorcycle jacket with antique brass zippers, quilted shoulders and breathable satin lining.", 260.00, 690.00, True),
            (6, "The Vintage Flight Bomber Jacket", "Classic sheepskin shearling collar leather bomber with ribbed storm cuffs and flap cargo pockets.", 310.00, 780.00, True)
        ]
        cur.executemany("INSERT INTO Products (CategoryID, ProductName, Description, BasePrice, SellingPrice, IsActive) VALUES (%s, %s, %s, %s, %s, %s);", products_data)

        # 9. ProductVariants
        variants_data = [
            # Product 1: Heritage Bifold (1)
            (1, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "WAL-HER-TAN", 0.00, True),
            (1, "Espresso Brown", "Standard", "Crazy Horse Buffalo", "WAL-HER-BRN", 0.00, True),
            (1, "Obsidian Black", "Standard", "Nappa Calfskin", "WAL-HER-BLK", 5.00, True),
            # Product 2: Slim Cardholder (2)
            (2, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "CRD-SLM-TAN", 0.00, True),
            (2, "Burgundy Wine", "Standard", "Full Grain Veg-Tanned", "CRD-SLM-BUR", 0.00, True),
            (2, "Espresso Brown", "Standard", "Crazy Horse Buffalo", "CRD-SLM-BRN", 0.00, True),
            # Product 3: Passport Wallet (3)
            (3, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "PAS-TRV-TAN", 0.00, True),
            (3, "Obsidian Black", "Standard", "Nappa Calfskin", "PAS-TRV-BLK", 0.00, True),
            # Product 4: Executive Briefcase 15" (4)
            (4, "Cognac Brown", "15-Inch", "Full Grain Veg-Tanned", "BAG-BRF-COG-15", 0.00, True),
            (4, "Obsidian Black", "15-Inch", "Full Grain Veg-Tanned", "BAG-BRF-BLK-15", 20.00, True),
            # Product 5: Artisan Messenger Satchel (5)
            (5, "Espresso Brown", "Medium", "Crazy Horse Buffalo", "BAG-MSG-BRN-M", 0.00, True),
            (5, "Saddle Tan", "Medium", "Full Grain Veg-Tanned", "BAG-MSG-TAN-M", 0.00, True),
            # Product 6: Florence Tote (6)
            (6, "Warm Chestnut", "Large", "Full Grain Veg-Tanned", "TOT-FLO-CHE-L", 0.00, True),
            (6, "Obsidian Black", "Large", "Full Grain Veg-Tanned", "TOT-FLO-BLK-L", 0.00, True),
            # Product 7: Old-World Harness Belt (7)
            (7, "Saddle Tan", "34-Inch", "Full Grain Veg-Tanned", "BLT-HAR-TAN-34", 0.00, True),
            (7, "Saddle Tan", "36-Inch", "Full Grain Veg-Tanned", "BLT-HAR-TAN-36", 0.00, True),
            (7, "Espresso Brown", "34-Inch", "Full Grain Veg-Tanned", "BLT-HAR-BRN-34", 0.00, True),
            (7, "Espresso Brown", "36-Inch", "Full Grain Veg-Tanned", "BLT-HAR-BRN-36", 0.00, True),
            # Product 8: Formal Dress Belt (8)
            (8, "Obsidian Black", "34-Inch", "Nappa Calfskin", "BLT-DRS-BLK-34", 0.00, True),
            (8, "Obsidian Black", "36-Inch", "Nappa Calfskin", "BLT-DRS-BLK-36", 0.00, True),
            # Product 9: Nomad Weekender Duffel (9)
            (9, "Saddle Tan", "45L Standard", "Full Grain Veg-Tanned", "DUF-NOM-TAN-45", 0.00, True),
            (9, "Espresso Brown", "45L Standard", "Crazy Horse Buffalo", "DUF-NOM-BRN-45", 0.00, True),
            # Product 10: Master Dopp Kit (10)
            (10, "Saddle Tan", "Standard", "Full Grain Veg-Tanned", "DOP-MST-TAN", 0.00, True),
            (10, "Espresso Brown", "Standard", "Crazy Horse Buffalo", "DOP-MST-BRN", 0.00, True),
            # Product 11: Desk Pad Mat (11)
            (11, "Saddle Tan", "90x40cm", "Full Grain Veg-Tanned", "DSK-MAT-TAN", 0.00, True),
            (11, "Espresso Brown", "90x40cm", "Full Grain Veg-Tanned", "DSK-MAT-BRN", 0.00, True),
            # Product 12: MacBook Folio (12)
            (12, "Cognac Brown", "14-Inch", "Full Grain Veg-Tanned", "FOL-MAC-COG-14", 0.00, True),
            (12, "Cognac Brown", "16-Inch", "Full Grain Veg-Tanned", "FOL-MAC-COG-16", 15.00, True),
            # Product 13: Café Racer Jacket (13)
            (13, "Obsidian Black", "Large", "Top Grain Cowhide", "JKT-RAC-BLK-L", 0.00, True),
            (13, "Vintage Brown", "Large", "Top Grain Cowhide", "JKT-RAC-BRN-L", 0.00, True),
            # Product 14: Bomber Jacket (14)
            (14, "Dark Brown", "Large", "Top Grain Cowhide", "JKT-BOM-BRN-L", 0.00, True)
        ]
        cur.executemany("INSERT INTO ProductVariants (ProductID, Color, Size, MaterialType, SKU, AdditionalPrice, IsActive) VALUES (%s, %s, %s, %s, %s, %s, %s);", variants_data)

        # 10. Inventory
        print(" Seeding Inventory Stock Levels...")
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
        cur.executemany("INSERT INTO Inventory (VariantID, QuantityInHand, ReservedQuantity, ReorderLevel, Location) VALUES (%s, %s, %s, %s, %s);", inventory_seed)

        # 11. Production & ProductionMaterials & FinishedProducts
        print(" Seeding Manufacturing & Production Batches...")
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
        cur.executemany("INSERT INTO Production (ArtisanID, ProductionDate, BatchNo, Status, Notes) VALUES (%s, %s, %s, %s, %s);", production_seed)

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
        cur.executemany("INSERT INTO ProductionMaterials (ProductionID, MaterialID, QuantityUsed, Remarks) VALUES (%s, %s, %s, %s);", production_materials_seed)

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
        cur.executemany("INSERT INTO FinishedProducts (ProductionID, ProductID, QuantityProduced, UnitCost, ProductionCost) VALUES (%s, %s, %s, %s, %s);", finished_products_seed)

        # 12. Customers
        print(" Seeding Customers & CRM Data...")
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
        cur.executemany("INSERT INTO Customers (CustomerName, Phone, Email, Address, City, State, Pincode, JoinedDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", customers_data)

        # 13. Leads
        leads_data = [
            ("Jonathan Archer", "+1-214-555-0111", "j.archer@enterprise.com", "Instagram Ads", "2026-09-10", "Qualified"),
            ("Kavita Mehta", "+91-98110-44332", "kavita.m@delhicouture.in", "Luxury Craft Fair", "2026-09-12", "Converted"),
            ("Henrietta Clark", "+44-7700-900555", "h.clark@oxfordalumni.org", "Google Search", "2026-09-15", "Contacted"),
            ("Vikramaditya Rao", "+91-97000-88112", "v.rao@hyderabadtech.com", "Website Signup", "2026-09-18", "New"),
            ("Charlotte Laurent", "+33-6-1234-5678", "c.laurent@bordeauxwine.fr", "Instagram Ads", "2026-09-22", "Qualified"),
            ("Brandon Walsh", "+1-310-555-0129", "b.walsh@beverlyhills.net", "Referral", "2026-09-25", "Contacted")
        ]
        cur.executemany("INSERT INTO Leads (LeadName, Phone, Email, Source, LeadDate, Status) VALUES (%s, %s, %s, %s, %s, %s);", leads_data)

        # 14. CRM Interactions
        crm_interactions_data = [
            (1, "Phone Call", "Custom Monogram Inquiry", "Customer requested golden debossed initials 'A.H.' on the briefcase lid.", "2026-08-15 14:30:00", "2026-08-18", "Julian Croft"),
            (2, "WhatsApp Chat", "Leather Swatch Request", "Sent physical swatch kit for Tan vs Chestnut tote options.", "2026-08-20 11:15:00", "2026-08-24", "Julian Croft"),
            (3, "Email Newsletter", "VIP Autumn Collection Preview", "Engaged with promotional preview, clicked on weekender duffel.", "2026-09-01 09:00:00", None, "System Marketing"),
            (4, "Phone Call", "Bespoke Luggage Set Consultation", "Discussed matching 3-piece luggage set in Cognac leather.", "2026-09-10 16:45:00", "2026-09-20", "Victoria Vance"),
            (7, "Support Ticket", "Belt Sizing Guidance", "Assisted client in sizing up from 34\" to 36\" for waist size 33.", "2026-09-14 10:20:00", None, "Derek O'Connor"),
            (9, "WhatsApp Chat", "Corporate Gifting Inquiry", "Requested quote for 25 custom debossed bifold wallets for tech summit.", "2026-09-22 13:00:00", "2026-10-05", "Sofia Morales")
        ]
        cur.executemany("INSERT INTO CRM_Interactions (CustomerID, InteractionType, Subject, Description, InteractionDate, NextFollowUpDate, CreatedBy) VALUES (%s, %s, %s, %s, %s, %s, %s);", crm_interactions_data)

        # 15. Discounts & Promotions
        discounts_data = [
            ("LEATHERLUX10", "Percentage", 10.00, 100.00, "2026-08-01", "2026-12-31", True),
            ("CRAFT20", "Percentage", 20.00, 250.00, "2026-09-01", "2026-10-31", True),
            ("HERITAGE50", "Fixed Amount", 50.00, 400.00, "2026-08-15", "2026-11-30", True),
            ("WELCOME15", "Percentage", 15.00, 50.00, "2026-01-01", "2026-12-31", True)
        ]
        cur.executemany("INSERT INTO Discounts_Promotions (Code, DiscountType, DiscountValue, MinOrderAmount, StartDate, EndDate, IsActive) VALUES (%s, %s, %s, %s, %s, %s, %s);", discounts_data)

        # 16. Orders, OrderDetails, Payments, Shipments
        print(" Seeding Sales Orders, Line Items, Payments & Shipments...")
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
        cur.executemany("INSERT INTO Orders (CustomerID, OrderDate, OrderStatus, TotalAmount, DiscountAmount, ShippingAmount, GrandTotal) VALUES (%s, %s, %s, %s, %s, %s, %s);", orders_seed)

        order_details_seed = [
            (1, 9, 1, 480.00, 48.00, 432.00),   # Briefcase Cognac
            (2, 13, 1, 290.00, 0.00, 290.00),   # Tote Chestnut
            (3, 21, 1, 580.00, 50.00, 530.00),  # Nomad Duffel
            (3, 1, 1, 115.00, 0.00, 115.00),    # Heritage Bifold Tan
            (4, 21, 1, 580.00, 58.00, 522.00),  # Nomad Duffel
            (5, 7, 1, 95.00, 10.00, 85.00),     # Passport Wallet
            (5, 15, 1, 85.00, 7.00, 78.00),     # Belt Tan
            (6, 11, 1, 360.00, 0.00, 360.00),   # Messenger Satchel
            (7, 15, 1, 85.00, 0.00, 85.00),     # Harness Belt
            (8, 31, 1, 780.00, 78.00, 702.00),  # Bomber Jacket
            (9, 10, 2, 500.00, 50.00, 950.00),  # 2x Briefcase Black
            (9, 27, 1, 150.00, 50.00, 100.00),  # Folio Sleeve
            (10, 1, 2, 115.00, 23.00, 207.00),  # 2x Bifold Tan
            (11, 29, 1, 690.00, 69.00, 621.00), # Café Racer Jacket
            (12, 9, 1, 480.00, 47.00, 433.00)   # Briefcase Cognac
        ]
        cur.executemany("INSERT INTO OrderDetails (OrderID, VariantID, Quantity, UnitPrice, Discount, TotalPrice) VALUES (%s, %s, %s, %s, %s, %s);", order_details_seed)

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
        cur.executemany("INSERT INTO Payments (OrderID, PaymentDate, PaymentMethod, Amount, TransactionID, PaymentStatus) VALUES (%s, %s, %s, %s, %s, %s);", payments_seed)

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
        cur.executemany("INSERT INTO Shipments (OrderID, ShippingDate, CourierName, TrackingNo, ShippingAddress, DeliveryStatus, DeliveredDate) VALUES (%s, %s, %s, %s, %s, %s, %s);", shipments_seed)

        # 17. Returns
        returns_seed = [
            (7, 9, "2026-09-20", "Belt was 2 inches larger than anticipated for client trousers.", "Refund Processed", 85.00),
            (5, 7, "2026-09-15", "Customer requested exchange for Saddle Tan passport sleeve instead of Black.", "Approved", 0.00)
        ]
        cur.executemany("INSERT INTO Returns (OrderID, OrderDetailID, ReturnDate, Reason, ReturnStatus, RefundAmount) VALUES (%s, %s, %s, %s, %s, %s);", returns_seed)

        # 18. Expenses
        print(" Seeding Business Expenses...")
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
        cur.executemany("INSERT INTO Expenses (ExpenseDate, ExpenseType, Description, Amount, PaidTo, PaymentMethod) VALUES (%s, %s, %s, %s, %s, %s);", expenses_seed)

        conn.commit()
        print("\n SUCCESS! All 24 tables for Handmade Leather Products populated with rich seed data!")

    except Exception as e:
        conn.rollback()
        print(f"\n Error seeding database: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_database()
