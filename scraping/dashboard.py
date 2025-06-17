# Importing necessary libraries
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

# Set up the Streamlit page
st.set_page_config(
    page_title="MLB History Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def connect_to_db():
    """Connect to the SQLite database"""
    db_path = "database/mlb_history.db"
    
    if not os.path.exists(db_path):
        st.error(f"Database file not found: {db_path}")
        st.error("Please run the database import program first.")
        st.stop()
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()

def get_tables(conn):
    """Get all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        st.error("No tables found in the database.")
        st.stop()
    
    return [table[0] for table in tables]

def load_data(conn, table_name):
    """Load data from a table into a DataFrame"""
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        st.error(f"Error loading data from {table_name}: {e}")
        return None

def main():
    """Main function to run the Streamlit app"""
    st.title("MLB History Dashboard")
    st.write("Explore Major League Baseball historical data through interactive visualizations.")
    
    # Connect to database
    conn = connect_to_db()
    
    # Get available tables
    tables = get_tables(conn)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "World Series Champions", "Hitting Leaders", "Pitching Leaders", "Team Standings", "Custom Analysis"])
    
    if page == "Overview":
        show_overview(conn, tables)
    
    elif page == "World Series Champions":
        show_world_series_champions(conn)
    
    elif page == "Hitting Leaders":
        show_hitting_leaders(conn)
    
    elif page == "Pitching Leaders":
        show_pitching_leaders(conn)
    
    elif page == "Team Standings":
        show_team_standings(conn)
    
    elif page == "Custom Analysis":
        show_custom_analysis(conn, tables)
    
    # Close database connection
    conn.close()

def show_overview(conn, tables):
    """Show overview of the database"""
    st.header("Database Overview")
    
    st.write("This dashboard provides interactive visualizations of Major League Baseball historical data.")
    st.write("The database contains the following tables:")
    
    for table in tables:
        st.write(f"- **{table}**: {get_table_description(table)}")
    
    st.write("Use the sidebar to navigate to different sections of the dashboard.")

def get_table_description(table_name):
    """Get a description of a table"""
    descriptions = {
        "mlb_champions": "World Series champions by year",
        "hitting_leaders": "League leaders in hitting statistics",
        "pitching_leaders": "League leaders in pitching statistics",
        "team_standings": "Team standings by year"
    }
    
    return descriptions.get(table_name, "No description available")

def show_world_series_champions(conn):
    """Show visualizations for World Series champions"""
    st.header("World Series Champions")
    
    # Load data
    df = load_data(conn, "mlb_champions")
    if df is None:
        return
    
    # Convert Year to numeric
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Filter by year range
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    
    st.subheader("Filter by Year Range")
    year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))
    
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    
    # Count champions by team
    champion_counts = filtered_df['World_Series_Champion'].value_counts().reset_index()
    champion_counts.columns = ['Team', 'Count']
    
    # Create bar chart
    fig = px.bar(
        champion_counts, 
        x='Team', 
        y='Count',
        title=f"World Series Champions ({year_range[0]}-{year_range[1]})",
        labels={'Team': 'Team', 'Count': 'Number of Championships'},
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Team",
        yaxis_title="Number of Championships",
        xaxis={'categoryorder': 'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show timeline of champions
    st.subheader("Timeline of World Series Champions")
    
    fig = px.scatter(
        filtered_df,
        x='Year',
        y='World_Series_Champion',
        title=f"World Series Champions Timeline ({year_range[0]}-{year_range[1]})",
        labels={'Year': 'Year', 'World_Series_Champion': 'Team'},
        color='World_Series_Champion',
        size_max=10
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Team",
        xaxis={'tickmode': 'linear', 'tick0': 5, 'dtick': 5}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

def show_hitting_leaders(conn):
    """Show visualizations for hitting leaders"""
    st.header("Hitting Leaders")
    
    # Load data
    df = load_data(conn, "hitting_leaders")
    if df is None:
        return
    
    # Convert numeric columns
    numeric_columns = ['AVG', 'G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter by year range if Year column exists
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        min_year = int(df['Year'].min())
        max_year = int(df['Year'].max())
        
        st.subheader("Filter by Year Range")
        year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))
        
        filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    else:
        filtered_df = df
    
    # Select statistic to visualize
    st.subheader("Select Statistic to Visualize")
    stat_options = [col for col in numeric_columns if col in df.columns]
    selected_stat = st.selectbox("Select statistic", stat_options)
    
    # Create bar chart
    fig = px.bar(
        filtered_df.sort_values(by=selected_stat, ascending=False).head(20),
        x='Player',
        y=selected_stat,
        title=f"Top 20 Players by {selected_stat}",
        labels={'Player': 'Player', selected_stat: selected_stat},
        color=selected_stat,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Player",
        yaxis_title=selected_stat,
        xaxis={'categoryorder': 'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

def show_pitching_leaders(conn):
    """Show visualizations for pitching leaders"""
    st.header("Pitching Leaders")
    
    # Load data
    df = load_data(conn, "pitching_leaders")
    if df is None:
        return
    
    # Convert numeric columns
    numeric_columns = ['W', 'L', 'ERA', 'G', 'GS', 'CG', 'SHO', 'SV', 'IP', 'H', 'R', 'ER', 'HR', 'BB', 'SO']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter by year range if Year column exists
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        min_year = int(df['Year'].min())
        max_year = int(df['Year'].max())
        
        st.subheader("Filter by Year Range")
        year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))
        
        filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    else:
        filtered_df = df
    
    # Select statistic to visualize
    st.subheader("Select Statistic to Visualize")
    stat_options = [col for col in numeric_columns if col in df.columns]
    selected_stat = st.selectbox("Select statistic", stat_options)
    
    # Determine if higher or lower is better
    lower_is_better = selected_stat in ['ERA', 'L']
    sort_ascending = lower_is_better
    
    # Create bar chart
    fig = px.bar(
        filtered_df.sort_values(by=selected_stat, ascending=sort_ascending).head(20),
        x='Player',
        y=selected_stat,
        title=f"Top 20 Players by {selected_stat}",
        labels={'Player': 'Player', selected_stat: selected_stat},
        color=selected_stat,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Player",
        yaxis_title=selected_stat,
        xaxis={'categoryorder': 'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

def show_team_standings(conn):
    """Show visualizations for team standings"""
    st.header("Team Standings")
    
    # Load data
    df = load_data(conn, "team_standings")
    if df is None:
        return
    
    # Convert numeric columns
    numeric_columns = ['Year', 'W', 'L', 'PCT', 'GB']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter by year range
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    
    st.subheader("Filter by Year Range")
    year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))
    
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    
    # Select year to visualize
    st.subheader("Select Year to Visualize")
    year_options = sorted(filtered_df['Year'].unique(), reverse=True)
    selected_year = st.selectbox("Select year", year_options)
    
    year_df = filtered_df[filtered_df['Year'] == selected_year]
    
    # Create bar chart for wins
    fig = px.bar(
        year_df.sort_values(by='W', ascending=False),
        x='Team',
        y='W',
        title=f"Team Wins in {selected_year}",
        labels={'Team': 'Team', 'W': 'Wins'},
        color='W',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Team",
        yaxis_title="Wins",
        xaxis={'categoryorder': 'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create scatter plot for wins vs losses
    fig = px.scatter(
        year_df,
        x='W',
        y='L',
        text='Team',
        title=f"Wins vs Losses in {selected_year}",
        labels={'W': 'Wins', 'L': 'Losses'},
        color='PCT',
        color_continuous_scale='Viridis'
    )
    
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        xaxis_title="Wins",
        yaxis_title="Losses"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

def show_custom_analysis(conn, tables):
    """Show custom analysis options"""
    st.header("Custom Analysis")
    
    st.write("Select tables to join and analyze:")
    
    # Select tables to join
    selected_tables = st.multiselect("Select tables", tables)
    
    if len(selected_tables) < 1:
        st.warning("Please select at least one table.")
        return
    
    # Load data from selected tables
    dfs = {}
    for table in selected_tables:
        dfs[table] = load_data(conn, table)
    
    # Show data preview
    st.subheader("Data Preview")
    
    for table, df in dfs.items():
        st.write(f"**{table}**")
        st.dataframe(df.head())
    
    # Custom query
    st.subheader("Custom SQL Query")
    
    query = st.text_area("Enter your SQL query", """
    SELECT * FROM mlb_champions
    ORDER BY Year DESC
    LIMIT 10
    """)
    
    if st.button("Run Query"):
        try:
            result_df = pd.read_sql_query(query, conn)
            st.write(f"Query returned {len(result_df)} rows.")
            st.dataframe(result_df)
            
            # Visualize results
            st.subheader("Visualize Results")
            
            # Select columns to visualize
            numeric_columns = result_df.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_columns) >= 2:
                x_col = st.selectbox("Select X-axis", numeric_columns)
                y_col = st.selectbox("Select Y-axis", numeric_columns)
                
                fig = px.scatter(
                    result_df,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} vs {x_col}",
                    labels={x_col: x_col, y_col: y_col},
                    color=numeric_columns[0] if numeric_columns else None,
                    color_continuous_scale='Viridis'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Not enough numeric columns for visualization.")
        
        except Exception as e:
            st.error(f"Error running query: {e}")

if __name__ == "__main__":
    main() 