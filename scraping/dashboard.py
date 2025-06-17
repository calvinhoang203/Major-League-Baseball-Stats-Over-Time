# Import libraries
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# Dashboard Streamlit

# Set up page
st.set_page_config(
    page_title="MLB History Dashboard",
    page_icon="⚾",
    layout="wide"
)

def connect_to_db():
    """Connect to database"""
    db_path = "database/mlb_history.db"
    
    if not os.path.exists(db_path):
        st.error("Database not found. Run db_import.py first.")
        st.stop()
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        st.error(f"Database error: {e}")
        st.stop()

def load_data(conn, table_name):
    """Load data from table"""
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        st.error(f"Error loading {table_name}: {e}")
        return None

def main():
    """Main dashboard function"""
    st.title("MLB History Dashboard")
    st.write("Baseball data from 1975-2025")
    
    # Connect to database
    conn = connect_to_db()
    
    # Navigation
    st.sidebar.title("Choose Data")
    page = st.sidebar.radio("Select:", [
        "World Series Champions", 
        "AL MVP Winners", 
        "Team Standings"
    ])
    
    # Show selected page
    if page == "World Series Champions":
        show_champions(conn)
    elif page == "AL MVP Winners":
        show_mvp_winners(conn)
    elif page == "Team Standings":
        show_standings(conn)
    
    conn.close()

def show_champions(conn):
    """Show World Series champions"""
    st.header("World Series Champions")
    
    # Load data
    df = load_data(conn, "world_series_champions_1975_to_2025")
    if df is None:
        return
    
    # Year filter
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    
    year_range = st.slider("Year Range", min_year, max_year, (min_year, max_year))
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    
    # Count championships by team
    champion_counts = filtered_df['World_Series_Champion'].value_counts().reset_index()
    champion_counts.columns = ['Team', 'Championships']
    
    # Bar chart
    fig = px.bar(
        champion_counts, 
        x='Team', 
        y='Championships',
        title=f"Championships {year_range[0]}-{year_range[1]}",
        color='Championships'
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.subheader("Championship Timeline")
    fig2 = px.scatter(
        filtered_df,
        x='Year',
        y='World_Series_Champion',
        color='League',
        title="Champions by Year"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Show data
    st.subheader("Data")
    st.dataframe(filtered_df)

def show_mvp_winners(conn):
    """Show AL MVP winners"""
    st.header("American League MVP Winners")
    
    # Load data
    df = load_data(conn, "american_league_mvp_winners_1975_to_2025")
    if df is None:
        return
    
    # Year filter
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    
    year_range = st.slider("Year Range", min_year, max_year, (min_year, max_year))
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    
    # MVP count by team
    team_counts = filtered_df['Team'].value_counts().reset_index()
    team_counts.columns = ['Team', 'MVP_Count']
    
    # Bar chart
    fig = px.bar(
        team_counts, 
        x='Team', 
        y='MVP_Count',
        title=f"MVP Winners by Team {year_range[0]}-{year_range[1]}",
        color='MVP_Count'
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # MVP by position
    position_counts = filtered_df['Position'].value_counts().reset_index()
    position_counts.columns = ['Position', 'Count']
    
    fig2 = px.pie(
        position_counts,
        values='Count',
        names='Position',
        title="MVP Winners by Position"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Show data
    st.subheader("Data")
    st.dataframe(filtered_df)

def show_standings(conn):
    """Show team standings"""
    st.header("American League Standings")
    
    # Load data
    df = load_data(conn, "american_league_standings_1975_to_2025")
    if df is None:
        return
    
    # Year filter
    years = sorted(df['Year'].unique())
    selected_year = st.selectbox("Select Year", years, index=len(years)-1)
    
    year_df = df[df['Year'] == selected_year]
    
    # Wins by division
    fig = px.bar(
        year_df,
        x='Team',
        y='Wins',
        color='Division',
        title=f"{selected_year} AL Standings",
        hover_data=['Losses', 'WP']
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Payroll vs Wins (if payroll data exists)
    if 'Payroll' in year_df.columns and year_df['Payroll'].notna().any():
        fig2 = px.scatter(
            year_df,
            x='Payroll',
            y='Wins',
            color='Division',
            hover_name='Team',
            title=f"{selected_year} Payroll vs Wins"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Show data
    st.subheader("Data")
    st.dataframe(year_df)

if __name__ == "__main__":
    main() 