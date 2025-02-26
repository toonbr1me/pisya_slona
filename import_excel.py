
import pandas as pd
import pymysql
import os
import sys

def process_partners_data(excel_path):
    """Process the Partners Excel file data"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Clean data (remove empty rows, etc.)
        df = df.dropna(subset=['name', 'inn'])  # Require at least name and INN
        
        # Process data (example: split address into city, street, building)
        # This is a placeholder - adjust according to actual Excel structure
        if 'address' in df.columns:
            # Split address into components if it's in a single column
            df[['city', 'street', 'building']] = df['address'].str.split(',', expand=True)
            df = df.drop('address', axis=1)
        
        # Process director name if it's in a single column
        if 'director_name' in df.columns:
            # Split full name into components
            df[['director_lastname', 'director_firstname', 'director_middlename']] = df['director_name'].str.split(' ', expand=True)
            df = df.drop('director_name', axis=1)
            
        return df
    except Exception as e:
        print(f"Error processing Partners data: {str(e)}")
        return None

def process_products_data(excel_path):
    """Process the Partner_products Excel file data"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Clean data (remove empty rows, etc.)
        df = df.dropna(subset=['partner_id', 'product_name'])
        
        return df
    except Exception as e:
        print(f"Error processing Products data: {str(e)}")
        return None

def import_to_database(host, port, user, password, db_name):
    """Import processed Excel data to MySQL database"""
    try:
        # Process Excel files
        partners_df = process_partners_data("Ресурсы/Partners_import.xlsx")
        products_df = process_products_data("Ресурсы/Partner_products_import.xlsx")
        
        if partners_df is None or products_df is None:
            return False
        
        # Connect to database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Import Partners data
        for _, row in partners_df.iterrows():
            # Create SQL query with proper escaping
            query = """
            INSERT INTO Partners (
                name, type, city, street, building,
                director_lastname, director_firstname, director_middlename,
                phone, email, inn, rating
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Extract values from dataframe
            values = (
                row.get('name', ''),
                row.get('type', 'ООО'),
                row.get('city', ''),
                row.get('street', ''),
                row.get('building', ''),
                row.get('director_lastname', ''),
                row.get('director_firstname', ''),
                row.get('director_middlename', ''),
                row.get('phone', ''),
                row.get('email', ''),
                row.get('inn', ''),
                int(row.get('rating', 0))
            )
            
            # Execute query
            cursor.execute(query, values)
        
        # Import Partner_products data
        for _, row in products_df.iterrows():
            query = """
            INSERT INTO Partner_products (
                partner_id, product_name, product_code, price
            ) VALUES (%s, %s, %s, %s)
            """
            
            values = (
                int(row.get('partner_id', 0)),
                row.get('product_name', ''),
                row.get('product_code', ''),
                float(row.get('price', 0))
            )
            
            cursor.execute(query, values)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Data imported successfully")
        return True
    except Exception as e:
        print(f"Error importing data to database: {str(e)}")
        return False

if __name__ == "__main__":
    # Database connection parameters
    host = "t1brime-dev.ru"
    port = 3306
    user = "toonbrime"
    password = "Bebra228"
    db_name = "CBO"
    
    # Run import
    success = import_to_database(host, port, user, password, db_name)
    
    if success:
        print("Excel data successfully imported to database")
    else:
        print("Failed to import Excel data")
