# Importing necessary libraries
import pandas as pd
import sqlite3
import os
import glob

def import_csv_to_db():
    """
    Import CSV files from the data directory into a SQLite database.
    Each CSV file becomes a separate table in the database.
    """
    # Make sure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect("database/mlb_history.db")
    cursor = conn.cursor()
    
    # Find all CSV files in the data directory
    csv_files = glob.glob("data/*.csv")
    
    if not csv_files:
        print("No CSV files found in the data directory.")
        return
    
    # Process each CSV file
    for csv_file in csv_files:
        try:
            # Get table name from file name (without extension)
            table_name = os.path.basename(csv_file).split('.')[0]
            
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Clean up column names (remove spaces and special characters)
            df.columns = [col.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '') for col in df.columns]
            
            # Import to SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            print(f"Imported {len(df)} records from {csv_file} to table {table_name}")
            
            # Show table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"Table structure for {table_name}:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()
            
        except Exception as e:
            print(f"Error importing {csv_file}: {e}")
    
    # Close the database connection
    conn.close()
    print("Database import complete!")

if __name__ == "__main__":
    import_csv_to_db() 