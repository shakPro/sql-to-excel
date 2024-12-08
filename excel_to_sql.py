import sqlite3
import pandas as pd
import os
import re

def create_database(sql_file_path):
    print(f"Starting conversion of {sql_file_path}")
    
    # Verify file exists
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file not found at {sql_file_path}")
        return
        
    # Create output directory if it doesn't exist
    output_dir = "excel_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Excel files will be saved to: {output_dir}")
    
    # Connect to a temporary SQLite database
    conn = sqlite3.connect('temp_database.db')
    cursor = conn.cursor()
    
    # Read the SQL file with error handling
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            print("Reading SQL file...")
            sql_content = file.read()
            print(f"Successfully read {len(sql_content)} characters")
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(sql_file_path, 'r', encoding='latin1') as file:
                print("Reading SQL file with latin1 encoding...")
                sql_content = file.read()
                print(f"Successfully read {len(sql_content)} characters")
        except Exception as e:
            print(f"Error reading file with latin1 encoding: {str(e)}")
            return
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return
    
    # Print first few characters for debugging
    print("\nFirst 200 characters of SQL file:")
    print(sql_content[:200])
    print("\n")
    
    # Remove MySQL-specific syntax
    print("Cleaning SQL content...")
    sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)  # Remove comments
    sql_content = re.sub(r'ENGINE=.*?;', ';', sql_content)  # Remove ENGINE declarations
    sql_content = re.sub(r'COLLATE.*?(\s|,)', r'\1', sql_content)  # Remove COLLATE declarations
    sql_content = sql_content.replace('`', '"')  # Replace backticks with double quotes
    sql_content = re.sub(r'AUTO_INCREMENT', '', sql_content)  # Remove AUTO_INCREMENT
    
    # Remove other MySQL-specific statements
    sql_content = re.sub(r'SET \@.*?;', '', sql_content)  # Remove SET @ statements
    sql_content = re.sub(r'USE .*?;', '', sql_content)  # Remove USE statements
    sql_content = re.sub(r'CREATE DATABASE.*?;', '', sql_content)  # Remove CREATE DATABASE
    sql_content = re.sub(r'SET NAMES.*?;', '', sql_content)  # Remove SET NAMES
    sql_content = re.sub(r'SET character_set_client.*?;', '', sql_content)  # Remove character set
    sql_content = re.sub(r'SET FOREIGN_KEY_CHECKS.*?;', '', sql_content)  # Remove FK checks
    
    # Split into individual statements
    print("Splitting into statements...")
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    print(f"Found {len(statements)} SQL statements")
    
    tables_created = 0
    rows_inserted = 0
    
    print("\nExecuting statements...")
    for i, statement in enumerate(statements):
        if not statement:
            continue
            
        try:
            # Skip certain MySQL-specific statements
            if any(keyword in statement.upper() for keyword in ['SET ', 'USE ', 'CREATE DATABASE']):
                continue
                
            # Execute the statement
            cursor.execute(statement)
            
            if statement.upper().startswith('CREATE TABLE'):
                tables_created += 1
                print(f"Created table #{tables_created}")
            elif statement.upper().startswith('INSERT'):
                rows_inserted += cursor.rowcount
                if rows_inserted % 1000 == 0:
                    print(f"Inserted {rows_inserted} rows...")
                
        except sqlite3.Error as e:
            print(f"\nError executing statement #{i}:")
            print(f"Error: {e}")
            print(f"Statement preview: {statement[:200]}...")
            continue
    
    print(f"\nCreated {tables_created} tables")
    print(f"Inserted {rows_inserted} data rows")
    
    # Commit changes
    conn.commit()
    print("Successfully imported SQL file to temp_database.db")
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("No tables found in the database!")
        return
    
    print(f"\nFound {len(tables)} tables to export")
    
    # Export each table to Excel
    for table in tables:
        table_name = table[0]
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
            excel_path = os.path.join(output_dir, f"{table_name}.xlsx")
            df.to_excel(excel_path, index=False)
            print(f"Exported {table_name} to {excel_path} ({len(df)} rows)")
        except Exception as e:
            print(f"Error exporting {table_name}: {str(e)}")
    
    # Close connection
    conn.close()
    
    # Try to remove the temporary database
    try:
        os.remove('temp_database.db')
    except:
        print("Note: Could not remove temporary database file")

if __name__ == "__main__":
    sql_file = r"C:\Users\shahadat\Downloads\mra_mfi_mis_june_2021.sql"
    create_database(sql_file)
