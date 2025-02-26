
import pymysql
import os
from graphviz import Digraph

def generate_db_diagram(host, port, user, password, db_name, output_file="db_diagram"):
    """Generate a database diagram using Graphviz"""
    try:
        # Connect to database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Create a new directed graph
        dot = Digraph(comment='CBO Database Schema')
        dot.attr('node', shape='record', style='filled', fillcolor='lightblue')
        
        # Get table structures
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
        """, (db_name,))
        
        tables = cursor.fetchall()
        
        # Process each table
        for table in tables:
            table_name = table[0]
            
            # Get column information
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_key
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (db_name, table_name))
            
            columns = cursor.fetchall()
            
            # Format table node
            table_label = f"{{{table_name}|"
            for col in columns:
                col_name, data_type, is_nullable, column_key = col
                pk_marker = "PK" if column_key == "PRI" else ""
                nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                table_label += f"{pk_marker} {col_name} : {data_type} {nullable}\\l"
            table_label += "}"
            
            dot.node(table_name, label=table_label)
        
        # Get foreign key relationships
        cursor.execute("""
            SELECT
                table_name, column_name,
                referenced_table_name, referenced_column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = %s
                AND referenced_table_name IS NOT NULL
        """, (db_name,))
        
        relations = cursor.fetchall()
        
        # Add edges for foreign key relationships
        for relation in relations:
            table, column, ref_table, ref_column = relation
            dot.edge(table, ref_table, label=f"{column} -> {ref_column}")
        
        # Close connection
        conn.close()
        
        # Render the diagram
        dot.render(output_file, format='pdf', cleanup=True)
        print(f"Database diagram has been saved to {output_file}.pdf")
        return True
    
    except Exception as e:
        print(f"Error generating database diagram: {str(e)}")
        return False

if __name__ == "__main__":
    # Database connection parameters
    host = "t1brime-dev.ru"
    port = 3306
    user = "toonbrime"
    password = "Bebra228"
    db_name = "CBO"
    
    # Generate diagram
    generate_db_diagram(host, port, user, password, db_name)
