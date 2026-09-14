import pandas as pd
from data_loader import get_inventory, get_purchase_orders

def get_status(row):
    """
    Determine stock status by comparing current_stock to safety_stock and reorder_point.
    
    Args:
        row: a pandas Series (single inventory row)
    
    Returns:
        str: 'out' (0 stock), 'critical' (< safety), 'low' (< reorder), 'ok' (healthy)
    """
    current_stock = row.get('current_stock', 0)
    safety_stock = row.get('safety_stock', 0)
    reorder_point = row.get('reorder_point', 0)
    
    if current_stock == 0:
        return 'out'
    elif current_stock < safety_stock:
        return 'critical'
    elif current_stock < reorder_point:
        return 'low'
    else:
        return 'ok'

def reorder_priority_score(inventory_row, purchase_orders_df):
    """
    Calculate reorder priority score using the exact formula:
    
    score = (stock_deficit_ratio × 0.5) + (outgoing_pressure_ratio × 0.3) + (delivery_urgency_ratio × 0.2)
    
    Args:
        inventory_row: pandas Series (single inventory item)
        purchase_orders_df: DataFrame of all purchase orders
    
    Returns:
        dict: {
            'score': float (0–1),
            'classification': str ('Urgent', 'Soon', or 'Monitor')
        }
    """
    current_stock = inventory_row.get('current_stock', 0)
    reorder_point = inventory_row.get('reorder_point', 1)
    lead_time_days = inventory_row.get('lead_time_days', 1)
    sku_id = inventory_row.get('product_id')  # or sku_id, depending on your CSV column name
    
    # 1. Stock Deficit Ratio
    # If current_stock >= reorder_point, this is 0 (no deficit).
    # If current_stock < reorder_point, this is (1 - current/reorder), clamped to 0–1.
    stock_deficit_ratio = max(0, 1 - (current_stock / reorder_point)) if reorder_point > 0 else 0
    
    # 2. Outgoing Pressure Ratio
    # Count open/pending POs for this product. Divide by max POs across all products.
    if purchase_orders_df is not None and len(purchase_orders_df) > 0:
        # Filter for this product and open/pending status
        open_pos = purchase_orders_df[
            (purchase_orders_df['product_id'] == sku_id) &
            (purchase_orders_df['status'].isin(['open', 'pending', 'Open', 'Pending']))
        ]
        open_po_count = len(open_pos)
        
        # Find the maximum number of open POs for any single product
        max_pos_per_product = purchase_orders_df[
            purchase_orders_df['status'].isin(['open', 'pending', 'Open', 'Pending'])
        ].groupby('product_id').size().max() or 1
        
        outgoing_pressure_ratio = open_po_count / max_pos_per_product if max_pos_per_product > 0 else 0
    else:
        outgoing_pressure_ratio = 0
    
    # 3. Delivery Urgency Ratio
    # Shorter lead time = higher urgency (inverse relationship).
    delivery_urgency_ratio = 1 / max(lead_time_days, 1)
    
    # Clamp urgency to 0–1 range
    delivery_urgency_ratio = min(1, delivery_urgency_ratio)
    
    # Final Score
    score = (
        (stock_deficit_ratio * 0.5) +
        (outgoing_pressure_ratio * 0.3) +
        (delivery_urgency_ratio * 0.2)
    )
    
    # Classify
    if score > 0.7:
        classification = 'Urgent'
    elif score >= 0.4:
        classification = 'Soon'
    else:
        classification = 'Monitor'
    
    return {
        'score': round(score, 2),
        'classification': classification
    }

def get_alerts():
    """
    Return all inventory items where current_stock < reorder_point,
    each enriched with reorder score and classification.
    Sorted by score descending (most urgent first).
    
    Returns:
        list of dicts, each with inventory row data + score + classification
    """
    inventory_df = get_inventory()
    purchase_orders_df = get_purchase_orders()
    
    if inventory_df is None or len(inventory_df) == 0:
        return []
    
    # Find all items below reorder point
    alerts = inventory_df[
        inventory_df['current_stock'] < inventory_df['reorder_point']
    ].copy()
    
    if len(alerts) == 0:
        return []
    
    # Add score and classification to each alert
    alerts['status'] = alerts.apply(get_status, axis=1)
    alerts['reorder_data'] = alerts.apply(
        lambda row: reorder_priority_score(row, purchase_orders_df),
        axis=1
    )
    
    # Extract score and classification into separate columns
    alerts['score'] = alerts['reorder_data'].apply(lambda x: x['score'])
    alerts['classification'] = alerts['reorder_data'].apply(lambda x: x['classification'])
    
    # Drop the helper column
    alerts = alerts.drop('reorder_data', axis=1)
    
    # Sort by score descending
    alerts = alerts.sort_values('score', ascending=False)
    
    # Convert to list of dicts for JSON serialization
    return alerts.to_dict('records')
