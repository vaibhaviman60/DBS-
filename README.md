# 🎯 Jodo — AI-Powered ERP Dashboard

## Quick Start Guide

This is a **Flask + Pandas + HTML/JS** dashboard for inventory management. Backend loads CSV data, calculates alerts, and exposes JSON APIs. Frontend fetches and displays everything dynamically.

---

## 📋 What You Have

```
jodo/
├── app.py                    # Flask app (routes + API endpoints)
├── data_loader.py            # Loads CSVs into memory at startup
├── logic.py                  # Business logic (status, reorder scoring)
├── requirements.txt          # Python dependencies
├── data/                     # CSV files
│   ├── inventory.csv
│   ├── purchase_orders.csv
│   ├── suppliers.csv
│   ├── employees.csv
│   └── customers.csv
├── templates/
│   └── dashboard.html        # Main HTML (Jinja2 template)
└── static/
    ├── style.css             # All styling
    └── script.js             # Fetches APIs, renders tables/KPIs
```

---

## 🚀 Installation & Run

### Step 1: Clone or Pull the Code

```bash
# If you're on the branch already
git pull origin jodo-backend-integration

# Or clone the whole repo
git clone https://github.com/prachi-shah-ds/DBS-.git
cd DBS-
```

### Step 2: Create a Python Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What this installs:**
- `Flask` — web framework
- `pandas` — CSV data handling
- `python-dotenv` — environment variables (optional for now)
- `Werkzeug` — WSGI utilities

### Step 4: Run the Flask Server

```bash
python app.py
```

**You'll see:**
```
[APP] Initializing Flask app...
[DATA LOADER] Loading CSVs from .../data...
  ✓ Loaded inventory.csv: 18 rows
  ✓ Loaded purchase_orders.csv: 10 rows
  ✓ Loaded suppliers.csv: 5 rows
  ✓ Loaded employees.csv: 9 rows
  ✓ Loaded customers.csv: 10 rows
[DATA LOADER] All CSVs loaded successfully!

============================================================
🚀 JODO BACKEND RUNNING
============================================================

📍 Open your browser and go to:
   http://127.0.0.1:5000

📊 API Endpoints:
   GET  /api/kpis               → Summary metrics
   GET  /api/inventory          → All inventory items
   GET  /api/alerts             → Critical stock alerts
   GET  /api/purchase-orders    → All purchase orders
   GET  /api/suppliers          → All suppliers
   GET  /api/employees          → All employees
   GET  /api/customers          → All customers

============================================================
```

### Step 5: Open Your Browser

👉 Go to: **http://127.0.0.1:5000**

You should see:
- **Top nav** with Jodo branding
- **Left sidebar** with navigation
- **4 KPI cards** (Stock Value, Open POs, Alerts, Total Inventory Value) — populated from `/api/kpis`
- **Stock Alerts table** — populated from `/api/alerts`
- **All Inventory table** — populated from `/api/inventory`
- **Quick Stats** card on the right

---

## 🧪 Testing the APIs

In a new terminal (while server is running):

```bash
# Get KPIs
curl http://127.0.0.1:5000/api/kpis

# Get alerts
curl http://127.0.0.1:5000/api/alerts

# Get all inventory
curl http://127.0.0.1:5000/api/inventory

# Get only open purchase orders
curl http://127.0.0.1:5000/api/purchase-orders?status=open
```

Each returns JSON. Check your browser's **Console** (F12 → Console) to see fetch logs.

---

## 📝 How It Works (Plain English)

### 1. **Startup** (app.py)
   - Flask starts
   - `load_all_data()` runs once → reads 5 CSVs into pandas DataFrames
   - DataFrames stay in memory (fast, no re-reading per request)

### 2. **Frontend Loads** (dashboard.html)
   - User opens http://127.0.0.1:5000
   - Browser renders HTML (nav, sidebar, tables, KPI placeholders)
   - JavaScript (script.js) runs on page load

### 3. **Fetch Data** (script.js)
   ```javascript
   fetch('/api/kpis')        // Get KPI numbers
   fetch('/api/alerts')      // Get low-stock items
   fetch('/api/inventory')   // Get all products
   ```

### 4. **Render** (script.js + style.css)
   - Data arrives as JSON
   - JavaScript loops through rows, builds HTML tables
   - CSS styles them (purple brand, status pills, etc.)

### 5. **Calculate Alerts** (logic.py)
   - `get_status(row)` → compares `current_stock` to `safety_stock` and `reorder_point`
   - `reorder_priority_score()` → scores each low-stock item by urgency
   - `get_alerts()` → returns all items below reorder point, sorted by urgency

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
   → You didn't activate the venv or install requirements
   → Run: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
   → Then: `pip install -r requirements.txt`

### "FileNotFoundError: data/inventory.csv"
   → The CSV files are missing or in the wrong folder
   → Make sure you have a `data/` folder with all 5 CSVs
   → Check: `ls data/` (Mac/Linux) or `dir data` (Windows)

### Dashboard loads but tables are empty
   → Open browser **Console** (F12)
   → Look for red errors
   → If you see CORS errors or 404s, check that the Flask server is running
   → Refresh the page (Ctrl+R or Cmd+R)

### Flask server won't start
   → Is port 5000 already in use?
   → Try: `python app.py` (it will print the error)
   → Or use a different port: Edit `app.py` last line to `app.run(debug=True, port=8000)`

---

## 📊 CSV Columns Reference

Make sure your CSVs have these columns:

**inventory.csv:**
- `product_id`, `product_name`, `category`, `current_stock`, `safety_stock`, `reorder_point`, `unit_cost`, `lead_time_days`, `warehouse_id`

**purchase_orders.csv:**
- `product_id`, `status` (must be 'open', 'pending', or 'Delivered')

**suppliers.csv, employees.csv, customers.csv:**
- Whatever columns you have — they'll all be JSON-serialized

---

## 🎯 What's Next?

1. ✅ Get the dashboard running locally
2. ✅ Verify all tables populate with real data
3. ✅ Test the APIs in browser Console
4. 🔜 Add more pages (Customers, Suppliers, Analytics)
5. 🔜 Add filtering & search
6. 🔜 Add the AI chat assistant (Jule)
7. 🔜 Deploy to production (Heroku, AWS, etc.)

---

## 💡 Key Files Explained

### `app.py`
Flask application. Defines routes and API endpoints. When you request `/api/kpis`, Flask calls the `api_kpis()` function, which uses `get_inventory()` and `get_purchase_orders()` to fetch data, calculates metrics, and returns JSON.

### `data_loader.py`
Loads CSVs once at startup into global pandas DataFrames. Other files import functions like `get_inventory()` to fetch the cached data (no disk I/O per request).

### `logic.py`
Business logic. Functions like `get_status()` and `reorder_priority_score()` operate on DataFrame rows to classify inventory and score urgency.

### `templates/dashboard.html`
HTML template. Uses Jinja2 syntax `{{ url_for(...) }}` to link CSS/JS. Defines the UI structure (nav, tables, KPI cards).

### `static/script.js`
JavaScript. On page load, fetches from `/api/kpis`, `/api/alerts`, `/api/inventory`, then renders HTML and inserts into the DOM.

### `static/style.css`
CSS. All styling (colors, layout, responsive design).

---

## ✅ Checklist Before Asking for Help

- [ ] I activated the virtual environment (`source venv/bin/activate`)
- [ ] I installed dependencies (`pip install -r requirements.txt`)
- [ ] I ran `python app.py` and saw "🚀 JODO BACKEND RUNNING"
- [ ] I opened http://127.0.0.1:5000 in my browser
- [ ] I see the Jodo dashboard (nav, sidebar, KPI cards, tables)
- [ ] I opened Console (F12) and see no red errors
- [ ] I tested an API endpoint: `curl http://127.0.0.1:5000/api/kpis`

---

## 📧 Questions?

If you get stuck:
1. Check the terminal output (where Flask is running)
2. Check the browser Console (F12 → Console tab)
3. Verify the CSV files are in `data/` folder
4. Make sure all 5 CSVs have the expected columns

**Good luck! 🚀**
