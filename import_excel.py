import pandas as pd
import pymysql
import os
import sys

def process_partners_data(excel_path):
    """Process the Partners Excel file data"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Print column names for debugging
        print("Available columns in partners file:", df.columns.tolist())
        
        # Map the Excel columns to the database columns
        column_mapping = {
            'Наименование партнера': 'name',
            'Тип партнера': 'type',
            'ИНН': 'inn',
            'Рейтинг': 'rating',
            'Город': 'city',
            'Улица': 'street',
            'Дом': 'building',
            'Фамилия директора': 'director_lastname',
            'Имя директора': 'director_firstname',
            'Отчество директора': 'director_middlename',
            'Телефон партнера': 'phone',
            'Электронная почта партнера': 'email'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Check required columns
        required_columns = ['name', 'inn']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns in partners file: {missing_columns}")
            return None
        
        # Clean data (remove empty rows, etc.)
        df = df.dropna(subset=['name', 'inn'])  # Require at least name and INN
        
        return df
    except Exception as e:
        print(f"Error processing Partners data: {str(e)}")
        return None

def process_products_data(excel_path):
    """Process the Partner_products Excel file data"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Print column names for debugging
        print("Available columns in products file:", df.columns.tolist())
        
        # Map Excel columns to database columns
        column_mapping = {
            'Наименование партнера': 'partner_id',  # Will need conversion to ID
            'Продукция': 'product_name',
            'Количество продукции': 'count_product',  # Using quantity field correctly
            'Дата продажи': 'date_sale'  # Using date field
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Generate a product code
        df['product_code'] = df['product_name'].str.slice(0, 10).str.upper().str.replace(' ', '_')
        
        # Add default price if not present
        if 'price' not in df.columns:
            df['price'] = 0  # Default price, will be updated later
        
        # Check required columns
        required_columns = ['partner_id', 'product_name', 'count_product', 'date_sale']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns in products file: {missing_columns}")
            return None
        
        return df
    except Exception as e:
        print(f"Error processing Products data: {str(e)}")
        return None

def get_partner_id_map(host, port, user, password, db_name):
    """Get a mapping of partner names to IDs"""
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Partners")
        rows = cursor.fetchall()
        conn.close()
        
        # Create a mapping of name -> id
        return {row[1]: row[0] for row in rows}
    except Exception as e:
        print(f"Error getting partner ID map: {str(e)}")
        return {}

def import_to_database(host, port, user, password, db_name):
    """Import processed Excel data to MySQL database"""
    try:
        # Process Excel files
        partners_df = process_partners_data("Ресурсы/Partners_import.xlsx")
        
        if partners_df is None:
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
        
        # First, import Partners data
        print("Importing partner data...")
        for _, row in partners_df.iterrows():
            # Create SQL query with proper escaping to prevent SQL injection
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
        
        # Commit changes to save partner data
        conn.commit()
        print(f"Imported {len(partners_df)} partners successfully")
        
        # Now get partner ID mapping
        partner_id_map = get_partner_id_map(host, port, user, password, db_name)
        
        # Now import Products data
        products_df = process_products_data("Ресурсы/Partner_products_import.xlsx")
        
        if products_df is None:
            conn.close()
            return False
        
        print("Importing product data...")
        imported_count = 0
        for _, row in products_df.iterrows():
            # Map partner name to partner_id
            partner_name = row.get('partner_id')
            if isinstance(partner_name, (int, float)):
                # If it's already a number, use it directly
                partner_id = int(partner_name)
            else:
                # Otherwise look up in the mapping
                partner_id = partner_id_map.get(partner_name)
                
            if not partner_id:
                print(f"Warning: Could not find partner ID for '{partner_name}'")
                continue
                
            query = """
            INSERT INTO Partner_products (
                partner_id, product_name, product_code, price, count_product, date_sale
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                partner_id,
                row.get('product_name', ''),
                row.get('product_code', ''),
                float(row.get('price', 0)),
                int(row.get('count_product', 1)),
                row.get('date_sale')
            )
            
            cursor.execute(query, values)
            imported_count += 1
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print(f"Imported {imported_count} products successfully")
        print("Data imported successfully")
        return True
    except Exception as e:
        print(f"Error importing data to database: {str(e)}")
        return False

def create_database_and_tables(host, port, user, password, db_name):
    """Create the database and tables if they don't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        
        # Switch to the database
        cursor.execute(f"USE {db_name}")
        
        # Create Partners table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Partners (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(20) NOT NULL,
            city VARCHAR(100),
            street VARCHAR(100),
            building VARCHAR(20),
            director_lastname VARCHAR(50),
            director_firstname VARCHAR(50),
            director_middlename VARCHAR(50),
            phone VARCHAR(20),
            email VARCHAR(100),
            inn VARCHAR(20) UNIQUE NOT NULL,
            rating INT
        )
        """)
        
        # Create Partner_products table with sales history fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Partner_products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            partner_id INT NOT NULL,
            product_name VARCHAR(100) NOT NULL,
            product_code VARCHAR(50) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            count_product INT DEFAULT 1,
            date_sale DATE,
            FOREIGN KEY (partner_id) REFERENCES Partners(id) ON DELETE CASCADE
        )
        """)
        
        conn.commit()
        conn.close()
        
        print("Database and tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating database and tables: {str(e)}")
        return False

if __name__ == "__main__":
    # Database connection parameters
    host = "t1brime-dev.ru"
    port = 3306
    user = "toonbrime"
    password = "Bebra228"
    db_name = "CBO"
    
    # First create database and tables if they don't exist
    if create_database_and_tables(host, port, user, password, db_name):
        # Then import data
        success = import_to_database(host, port, user, password, db_name)
        
        if success:
            print("Excel data successfully imported to database")
        else:
            print("Failed to import Excel data")
    else:
        print("Failed to set up database structure")
