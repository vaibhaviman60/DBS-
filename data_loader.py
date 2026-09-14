import pandas as pd
import os
from pathlib import Path

# Global DataFrames - loaded once at app startup
inventory_df = None
purchase_orders_df = None
suppliers_df = None
employees_df = None
customers_df = None

def load_all_data():
    """
    Load all CSV files from the /data directory into pandas DataFrames.
    This runs once when the Flask app starts, so we don't reload CSVs per request.
    
    Returns: dict with all loaded DataFrames
    """
    global inventory_df, purchase_orders_df, suppliers_df, employees_df, customers_df
    
    # Get the path to the /data folder
    data_path = Path(__file__).parent / 'data'
    
    print(f"[DATA LOADER] Loading CSVs from {data_path}...")
    
    try:
        # Read each CSV file
        inventory_df = pd.read_csv(data_path / 'inventory.csv')
        print(f"  ✓ Loaded inventory.csv: {len(inventory_df)} rows")
        
        purchase_orders_df = pd.read_csv(data_path / 'purchase_orders.csv')
        print(f"  ✓ Loaded purchase_orders.csv: {len(purchase_orders_df)} rows")
        
        suppliers_df = pd.read_csv(data_path / 'suppliers.csv')
        print(f"  ✓ Loaded suppliers.csv: {len(suppliers_df)} rows")
        
        employees_df = pd.read_csv(data_path / 'employees.csv')
        print(f"  ✓ Loaded employees.csv: {len(employees_df)} rows")
        
        customers_df = pd.read_csv(data_path / 'customers.csv')
        print(f"  ✓ Loaded customers.csv: {len(customers_df)} rows")
        
        print("[DATA LOADER] All CSVs loaded successfully!\n")
        
        return {
            'inventory': inventory_df,
            'purchase_orders': purchase_orders_df,
            'suppliers': suppliers_df,
            'employees': employees_df,
            'customers': customers_df
        }
    except Exception as e:
        print(f"[ERROR] Failed to load CSV files: {e}")
        raise

def get_inventory():
    """Returns the cached inventory DataFrame"""
    return inventory_df

def get_purchase_orders():
    """Returns the cached purchase orders DataFrame"""
    return purchase_orders_df

def get_suppliers():
    """Returns the cached suppliers DataFrame"""
    return suppliers_df

def get_employees():
    """Returns the cached employees DataFrame"""
    return employees_df

def get_customers():
    """Returns the cached customers DataFrame"""
    return customers_df
