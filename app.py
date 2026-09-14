from flask import Flask, render_template, jsonify, request
import pandas as pd
from data_loader import load_all_data, get_inventory, get_purchase_orders, get_suppliers, get_employees, get_customers
from logic import get_alerts, get_status, reorder_priority_score

app = Flask(__name__)

# Load all CSV data at app startup (only once)
print("\n[APP] Initializing Flask app...")
load_all_data()
print("[APP] All data loaded. Flask app ready!\n")

# ===================== FRONTEND ROUTES =====================

@app.route('/')
def index():
    """
    Render the main dashboard page.
    This serves the converted HTML template.
    """
    return render_template('dashboard.html')

# ===================== API ROUTES (JSON) =====================

@app.route('/api/kpis')
def api_kpis():
    """
    Return computed summary KPIs for the dashboard.
    
    Returns JSON with:
    - total_stock_value: sum of (current_stock × unit_cost)
    - open_po_count: number of open/pending purchase orders
    - critical_alert_count: number of 'critical' status items
    - low_alert_count: number of 'low' status items
    - total_inventory_value: total replacement value of all stock
    """
    inventory_df = get_inventory()
    purchase_orders_df = get_purchase_orders()
    
    if inventory_df is None or len(inventory_df) == 0:
        return jsonify({
            'total_stock_value': 0,
            'open_po_count': 0,
            'critical_alert_count': 0,
            'low_alert_count': 0,
            'total_inventory_value': 0
        })
    
    # Total stock value (current stock at unit cost)
    inventory_df['stock_value'] = inventory_df['current_stock'] * inventory_df.get('unit_cost', 0)
    total_stock_value = inventory_df['stock_value'].sum()
    
    # Open/pending purchase orders
    open_pos = purchase_orders_df[
        purchase_orders_df['status'].isin(['open', 'pending', 'Open', 'Pending'])
    ]
    open_po_count = len(open_pos)
    
    # Count critical and low alerts
    inventory_df['inv_status'] = inventory_df.apply(get_status, axis=1)
    critical_count = (inventory_df['inv_status'] == 'critical').sum()
    low_count = (inventory_df['inv_status'] == 'low').sum()
    
    # Total inventory replacement value (reorder_qty × unit_cost) for all items
    if 'reorder_qty' in inventory_df.columns:
        inventory_df['reorder_value'] = inventory_df.get('reorder_qty', 0) * inventory_df.get('unit_cost', 0)
    else:
        inventory_df['reorder_value'] = inventory_df['current_stock'] * inventory_df.get('unit_cost', 0)
    
    total_inventory_value = inventory_df['reorder_value'].sum()
    
    return jsonify({
        'total_stock_value': round(float(total_stock_value), 2),
        'open_po_count': int(open_po_count),
        'critical_alert_count': int(critical_count),
        'low_alert_count': int(low_count),
        'total_inventory_value': round(float(total_inventory_value), 2)
    })

@app.route('/api/inventory')
def api_inventory():
    """
    Return all inventory items as JSON.
    Optional filter by warehouse_id query param: /api/inventory?warehouse_id=123
    """
    inventory_df = get_inventory()
    
    if inventory_df is None or len(inventory_df) == 0:
        return jsonify([])
    
    # Optional warehouse filter
    warehouse_id = request.args.get('warehouse_id')
    if warehouse_id and 'warehouse_id' in inventory_df.columns:
        inventory_df = inventory_df[inventory_df['warehouse_id'] == int(warehouse_id)]
    
    # Add status column
    inventory_df['status'] = inventory_df.apply(get_status, axis=1)
    
    return jsonify(inventory_df.to_dict('records'))

@app.route('/api/alerts')
def api_alerts():
    """
    Return critical and low-stock alerts (items below reorder point).
    Each alert includes reorder priority score and classification.
    """
    alerts = get_alerts()
    return jsonify(alerts)

@app.route('/api/purchase-orders')
def api_purchase_orders():
    """
    Return all purchase orders as JSON.
    Optional filter by status query param: /api/purchase-orders?status=open
    """
    po_df = get_purchase_orders()
    
    if po_df is None or len(po_df) == 0:
        return jsonify([])
    
    # Optional status filter
    status_filter = request.args.get('status')
    if status_filter:
        po_df = po_df[po_df['status'].str.lower() == status_filter.lower()]
    
    return jsonify(po_df.to_dict('records'))

@app.route('/api/suppliers')
def api_suppliers():
    """
    Return all suppliers as JSON.
    """
    suppliers_df = get_suppliers()
    
    if suppliers_df is None or len(suppliers_df) == 0:
        return jsonify([])
    
    return jsonify(suppliers_df.to_dict('records'))

@app.route('/api/employees')
def api_employees():
    """
    Return all employees as JSON.
    """
    employees_df = get_employees()
    
    if employees_df is None or len(employees_df) == 0:
        return jsonify([])
    
    return jsonify(employees_df.to_dict('records'))

@app.route('/api/customers')
def api_customers():
    """
    Return all customers as JSON.
    """
    customers_df = get_customers()
    
    if customers_df is None or len(customers_df) == 0:
        return jsonify([])
    
    return jsonify(customers_df.to_dict('records'))

# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors gracefully."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors gracefully."""
    return jsonify({'error': 'Internal server error'}), 500

# ===================== DEBUG MODE =====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 JODO BACKEND RUNNING")
    print("="*60)
    print("\n📍 Open your browser and go to:")
    print("   http://127.0.0.1:5000")
    print("\n📊 API Endpoints:")
    print("   GET  /api/kpis               → Summary metrics")
    print("   GET  /api/inventory          → All inventory items")
    print("   GET  /api/alerts             → Critical stock alerts")
    print("   GET  /api/purchase-orders    → All purchase orders")
    print("   GET  /api/suppliers          → All suppliers")
    print("   GET  /api/employees          → All employees")
    print("   GET  /api/customers          → All customers")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
