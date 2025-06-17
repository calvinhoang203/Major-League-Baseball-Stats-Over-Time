# Importing necessary libraries
import sqlite3
import pandas as pd
import os
import sys

def connect_to_db():
    """Connect to the SQLite database"""
    db_path = "database/mlb_history.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("Please run the database import program first.")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def list_tables(conn):
    """Show all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("No tables found in the database.")
        return
    
    print("Available tables:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table[0]}")
    
    return [table[0] for table in tables]

def describe_table(conn, table_name):
    """Show the structure of a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    if not columns:
        print(f"Table {table_name} not found or has no columns.")
        return
    
    print(f"\nStructure of table {table_name}:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    return [col[1] for col in columns]

def execute_query(conn, query):
    """Run a SQL query and return results as a DataFrame"""
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error running query: {e}")
        return None

def run_interactive_query():
    """Run the interactive query tool"""
    conn = connect_to_db()
    
    print("MLB History Database Query Tool")
    print("===============================")
    
    # Show available tables
    tables = list_tables(conn)
    if not tables:
        conn.close()
        return
    
    while True:
        print("\nOptions:")
        print("1. Show table structure")
        print("2. Run a custom query")
        print("3. Run a predefined query")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            # Show table structure
            table_name = input("Enter table name: ")
            describe_table(conn, table_name)
        
        elif choice == '2':
            # Run a custom query
            query = input("Enter your SQL query: ")
            if query.lower() == 'exit':
                continue
            
            df = execute_query(conn, query)
            if df is not None:
                print(f"\nQuery returned {len(df)} rows.")
                print(df)
        
        elif choice == '3':
            # Run a predefined query
            print("\nPredefined Queries:")
            print("1. World Series Champions by Year")
            print("2. Top 10 Hitting Leaders by Batting Average")
            print("3. Top 10 Pitching Leaders by ERA")
            print("4. Team Standings by Year")
            print("5. Join World Series Champions with Team Standings")
            
            query_choice = input("\nEnter your choice (1-5): ")
            
            if query_choice == '1':
                query = "SELECT * FROM mlb_champions ORDER BY Year DESC"
                df = execute_query(conn, query)
                if df is not None:
                    print(f"\nQuery returned {len(df)} rows.")
                    print(df)
            
            elif query_choice == '2':
                query = "SELECT * FROM hitting_leaders ORDER BY AVG DESC LIMIT 10"
                df = execute_query(conn, query)
                if df is not None:
                    print(f"\nQuery returned {len(df)} rows.")
                    print(df)
            
            elif query_choice == '3':
                query = "SELECT * FROM pitching_leaders ORDER BY ERA ASC LIMIT 10"
                df = execute_query(conn, query)
                if df is not None:
                    print(f"\nQuery returned {len(df)} rows.")
                    print(df)
            
            elif query_choice == '4':
                query = "SELECT * FROM team_standings ORDER BY Year DESC"
                df = execute_query(conn, query)
                if df is not None:
                    print(f"\nQuery returned {len(df)} rows.")
                    print(df)
            
            elif query_choice == '5':
                query = """
                SELECT c.Year, c.World_Series_Champion, t.Team, t.W, t.L, t.PCT
                FROM mlb_champions c
                JOIN team_standings t ON c.Year = t.Year AND c.World_Series_Champion = t.Team
                ORDER BY c.Year DESC
                """
                df = execute_query(conn, query)
                if df is not None:
                    print(f"\nQuery returned {len(df)} rows.")
                    print(df)
            
            else:
                print("Invalid choice.")
        
        elif choice == '4':
            # Exit
            print("Exiting...")
            break
        
        else:
            print("Invalid choice.")
    
    conn.close()

if __name__ == "__main__":
    run_interactive_query() 