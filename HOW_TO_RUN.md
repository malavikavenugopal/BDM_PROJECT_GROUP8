# 🚀 How to Run the Handmade Leather Products BDM Platform

This guide provides step-by-step instructions to set up, seed, and run the **Handmade Leather Products Business Data Management (BDM) & MIS/CRUD Platform**.

---

## ⚡ Option 1: 1-Click Launch (Windows)

Simply double-click the **`run_dashboard.bat`** file in the project folder. It will:
1. Verify Python and dependencies.
2. Launch the Flask backend server.
3. Automatically open `http://localhost:5000` in your default browser.

---

## 🛠 Option 2: Step-by-Step Manual Execution

### Step 1: Open Your Terminal / PowerShell
Navigate to the project root directory:
```powershell
cd c:\Users\athir\OneDrive\Desktop\Malavika\BDM\Assignment
```

---

### Step 2: Install Required Dependencies
Ensure all required Python packages are installed:
```bash
pip install -r requirements.txt
```

---

### Step 3: Configure Database Connection (Optional)
The project includes a dual-engine database manager:
- **Cloud Supabase PostgreSQL** (Primary)
- **Local Pre-Seeded SQLite Database** (Automatic Fallback)

Open [`.env`](file:///.env) to check or update your connection string:
```env
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@[YOUR_HOST]:5432/postgres
```

> **Note**: If Supabase credentials are not provided or if you are offline, the system seamlessly and automatically runs on the included, fully-seeded local SQLite database (`leather_products.db`).

---

### Step 4: (Optional) Seed the Database
To re-create and populate all 24 relational tables with fresh, realistic handmade leather goods data:
```bash
python seed_leather_data.py
```

---

### Step 5: Start the Web Server
Launch the Flask backend server:
```bash
python server.py
```

You should see output similar to:
```text
================================================================================
* AETHELGARD LEATHERWORKS - BDM & MIS PLATFORM ACTIVE
* Database Engine: Local SQLite Engine (or Supabase PostgreSQL)
* Active URL:      http://localhost:5000
================================================================================
```

---

### Step 6: Open the Dashboard in Your Browser
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🎯 Features to Test in the Dashboard

1. **Connected Dropdown Selectors**:
   - In the **All Tables & CRUD Explorer**, select `PurchaseDetails` or `OrderDetails`.
   - Click **`+ Add New Record`**.
   - Notice that instead of raw numbers, you select materials, products, artisans, and suppliers by **human-readable names**.

2. **⚡ Real-Time Auto-Calculations**:
   - In `PurchaseDetails`: Enter `Quantity` = `890` and `UnitPrice` = `7008`.
   - Watch `TotalPrice` compute live with the formula badge (`890 × $7,008.00 = $6,237,120.00`).
   - In `Products`: Change `BasePrice` and `SellingPrice` to see live Gross Profit Margin % calculation.

3. **CRUD Operations**:
   - **Create**: Add a new supplier, customer, or product.
   - **Read & Search**: Filter records instantly with the search bar.
   - **Update**: Click **Edit** to modify any row.
   - **Delete**: Click **Delete** with automatic confirmation prompts.
   - **Export CSV**: Click **Export CSV** to download any table's data.

4. **Executive Analytics**:
   - Click the **Executive & Financial Analytics** tab to view live revenue, inventory valuations, and category charts.

5. **Ad-Hoc SQL Runner**:
   - Click the **SQL Query Runner** tab to write custom SQL queries against the 24 tables and inspect live result grids.

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| `Port 5000 already in use` | Change port in `server.py` (`app.run(port=5001)`) or close existing python processes. |
| `psycopg2 connection error` | Ensure your IP is allowlisted on Supabase, or continue using the automatic local SQLite fallback. |
| `Missing module error` | Run `pip install -r requirements.txt` to install all dependencies. |
