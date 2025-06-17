# Importing necessary libraries

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import re
import traceback

# Web Scraping Program

def get_american_league_year_links():
    """
    Get all American League year links from the year menu page.
    Returns a list of (year, url) tuples.
    """
    print("Getting American League year links...")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    try:
        # Start at the year menu page
        base_url = "https://www.baseball-almanac.com"
        year_index_url = f"{base_url}/yearmenu.shtml"
        
        print(f"Navigating to {year_index_url}")
        driver.get(year_index_url)
        time.sleep(5)  # Increased wait time
        
        # Print page title and URL to verify we're on the right page
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Find the American League section (first ba-table div)
        try:
            al_section = driver.find_element(By.XPATH, "(//div[contains(@class, 'ba-table')])[1]")
            print("Found American League section")
        except NoSuchElementException:
            print("Could not find American League section. Taking screenshot for debugging...")
            driver.save_screenshot("data/debug_year_menu.png")
            print("Screenshot saved to data/debug_year_menu.png")
            return []
        
        # Find all links in the American League section
        al_links = al_section.find_elements(By.TAG_NAME, "a")
        print(f"Found {len(al_links)} links in American League section")
        
        # Extract year links (4-digit years that link to yearly pages)
        year_links = []
        for link in al_links:
            text = link.text.strip()
            href = link.get_attribute('href')
            
            # Check if the text is a 4-digit year and the href contains 'yr' and ends with 'a.shtml'
            if text.isdigit() and len(text) == 4 and 'yr' in href and href.endswith('a.shtml'):
                year = int(text)
                # Only include years from 1975 to 2025
                if 1975 <= year <= 2025:
                    year_links.append((year, href))
                    print(f"Added year link: {year} -> {href}")
        
        print(f"Found {len(year_links)} American League year links from 1975 to 2025")
        return year_links
    
    except Exception as e:
        print(f"Error getting American League year links: {e}")
        traceback.print_exc()
        return []
    
    finally:
        driver.quit()

def extract_team_standings(driver, year, url):
    """
    Extract team standings for a given year and URL.
    Returns a list of dictionaries with team data.
    """
    print(f"Extracting {year} AL Team Standings...")
    
    try:
        driver.get(url)
        time.sleep(5)  # Increased wait time
        
        # Print page title and URL to verify we're on the right page
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Check if we're on an American League page
        page_title = driver.title
        if "National League" in page_title:
            print(f"Detected National League page for {year}, skipping...")
            return []
        
        # Find all tables on the page
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables on the page")
        
        # Look for the team standings table (usually the third table)
        standings_table = None
        for i, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if rows and "Team Standings" in rows[0].text:
                standings_table = table
                print(f"Found team standings table at index {i}")
                break
            
            if not standings_table:
                print(f"Could not find team standings table for {year}. Taking screenshot for debugging...")
                driver.save_screenshot(f"data/debug_{year}_page.png")
                print(f"Screenshot saved to data/debug_{year}_page.png")
                return []
        
        # Extract data from the standings table
        rows = standings_table.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} rows in standings table")
        
        data = []
        current_division = None
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_texts = [cell.text.strip() for cell in cells]
            
            # Skip empty rows
            if not cell_texts:
                continue
            
            # Check if this is a division header row
            if len(cell_texts) > 0 and cell_texts[0] in ["East", "Central", "West"]:
                current_division = cell_texts[0]
                print(f"Found division: {current_division}")
                continue
            
            # Skip header rows
            if len(cell_texts) > 0 and "Team [Click for roster]" in cell_texts[0]:
                continue
            
            # Team row (should have 7 columns)
            if len(cell_texts) == 7 and current_division:
                # Clean up the data
                team = cell_texts[0]
                wins = cell_texts[1]
                losses = cell_texts[2]
                ties = cell_texts[3]
                wp = cell_texts[4]
                gb = cell_texts[5]
                payroll = cell_texts[6]
                
                # Add to data list
                data.append({
                    "Year": year,
                    "Division": current_division,
                    "Team": team,
                    "Wins": wins,
                    "Losses": losses,
                    "Ties": ties,
                    "WP": wp,
                    "GB": gb,
                    "Payroll": payroll
                })
                print(f"Added team: {team} ({wins}-{losses})")
        
        print(f"Extracted {len(data)} team records for {year}")
        return data
    
    except Exception as e:
        print(f"Error extracting team standings for {year}: {e}")
        traceback.print_exc()
        return []

def scrape_al_team_standings():
    """
    Main function to scrape American League team standings from 1975 to 2025.
    """
    print("Starting American League team standings scraper...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Get all American League year links
    year_links = get_american_league_year_links()
    
    if not year_links:
        print("No year links found. Exiting.")
        return
    
    # Sort by year
    year_links.sort(key=lambda x: x[0])
    
    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Extract team standings for each year
        all_data = []
        
        for year, url in year_links:
            print(f"\nProcessing {year}...")
            year_data = extract_team_standings(driver, year, url)
            
            # If we got data, add it to our collection
            if year_data:
                all_data.extend(year_data)
            else:
                print(f"No data found for {year}, might be a National League year")
        
        # Save all data to CSV
        if all_data:
            df = pd.DataFrame(all_data)
            output_file = "data/american_league_standings_1975_2025.csv"
            df.to_csv(output_file, index=False)
            print(f"\nSaved {len(all_data)} team records to {output_file}")
        else:
            print("No team standings data found for any year.")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("Scraping complete.")

def clean_al_standings_data():
    """
    Clean the American League standings data and rename with proper title.
    """
    print("Cleaning American League standings data...")
    
    # Read the raw data - fix the filename to match what actually exists
    input_file = "data/american_league_standings_1975_to_2025.csv"
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        return
    
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} records from {input_file}")
    
    # Data cleaning steps
    # Convert numeric columns to proper data types
    numeric_cols = ['Wins', 'Losses', 'Ties', 'WP', 'GB']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean payroll column and convert to numeric
    if 'Payroll' in df.columns:
        # Convert to string first, then clean
        df['Payroll'] = df['Payroll'].astype(str)
        df['Payroll'] = df['Payroll'].str.replace('$', '').str.replace(',', '').str.replace('nan', '')
        df['Payroll'] = pd.to_numeric(df['Payroll'], errors='coerce')
    
    # Calculate additional stats
    df['Games_Played'] = df['Wins'] + df['Losses'] + df['Ties'].fillna(0)
    df['WP_Calculated'] = df['Wins'] / df['Games_Played']
    df['WP_Diff'] = abs(df['WP'] - df['WP_Calculated'])
    
    # Remove duplicate rows and invalid entries
    df = df.drop_duplicates()
    df = df.dropna(subset=['Wins', 'Losses'])  # Remove rows with no game data
    
    # Sort data by year and division
    df = df.sort_values(['Year', 'Division', 'Wins'], ascending=[True, True, False])
    
    # Save cleaned data with proper naming (overwrite the existing file since it's already correctly named)
    output_file = "data/american_league_standings_1975_to_2025.csv"
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")
    print(f"Final dataset: {len(df)} records from {df['Year'].min()} to {df['Year'].max()}")

def create_world_series_champions_data():
    """
    Create a comprehensive World Series champions dataset for 1975-2025.
    """
    print("Creating World Series champions dataset (1975-2025)...")
    
    # Comprehensive data for World Series champions (1975-2025)
    champions_data = [
        {"Year": 1975, "World_Series_Champion": "Cincinnati Reds", "League": "NL"},
        {"Year": 1976, "World_Series_Champion": "Cincinnati Reds", "League": "NL"},
        {"Year": 1977, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 1978, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 1979, "World_Series_Champion": "Pittsburgh Pirates", "League": "NL"},
        {"Year": 1980, "World_Series_Champion": "Philadelphia Phillies", "League": "NL"},
        {"Year": 1981, "World_Series_Champion": "Los Angeles Dodgers", "League": "NL"},
        {"Year": 1982, "World_Series_Champion": "St. Louis Cardinals", "League": "NL"},
        {"Year": 1983, "World_Series_Champion": "Baltimore Orioles", "League": "AL"},
        {"Year": 1984, "World_Series_Champion": "Detroit Tigers", "League": "AL"},
        {"Year": 1985, "World_Series_Champion": "Kansas City Royals", "League": "AL"},
        {"Year": 1986, "World_Series_Champion": "New York Mets", "League": "NL"},
        {"Year": 1987, "World_Series_Champion": "Minnesota Twins", "League": "AL"},
        {"Year": 1988, "World_Series_Champion": "Los Angeles Dodgers", "League": "NL"},
        {"Year": 1989, "World_Series_Champion": "Oakland Athletics", "League": "AL"},
        {"Year": 1990, "World_Series_Champion": "Cincinnati Reds", "League": "NL"},
        {"Year": 1991, "World_Series_Champion": "Minnesota Twins", "League": "AL"},
        {"Year": 1992, "World_Series_Champion": "Toronto Blue Jays", "League": "AL"},
        {"Year": 1993, "World_Series_Champion": "Toronto Blue Jays", "League": "AL"},
        {"Year": 1994, "World_Series_Champion": "No World Series", "League": "Strike"},
        {"Year": 1995, "World_Series_Champion": "Atlanta Braves", "League": "NL"},
        {"Year": 1996, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 1997, "World_Series_Champion": "Florida Marlins", "League": "NL"},
        {"Year": 1998, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 1999, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 2000, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 2001, "World_Series_Champion": "Arizona Diamondbacks", "League": "NL"},
        {"Year": 2002, "World_Series_Champion": "Anaheim Angels", "League": "AL"},
        {"Year": 2003, "World_Series_Champion": "Florida Marlins", "League": "NL"},
        {"Year": 2004, "World_Series_Champion": "Boston Red Sox", "League": "AL"},
        {"Year": 2005, "World_Series_Champion": "Chicago White Sox", "League": "AL"},
        {"Year": 2006, "World_Series_Champion": "St. Louis Cardinals", "League": "NL"},
        {"Year": 2007, "World_Series_Champion": "Boston Red Sox", "League": "AL"},
        {"Year": 2008, "World_Series_Champion": "Philadelphia Phillies", "League": "NL"},
        {"Year": 2009, "World_Series_Champion": "New York Yankees", "League": "AL"},
        {"Year": 2010, "World_Series_Champion": "San Francisco Giants", "League": "NL"},
        {"Year": 2011, "World_Series_Champion": "St. Louis Cardinals", "League": "NL"},
        {"Year": 2012, "World_Series_Champion": "San Francisco Giants", "League": "NL"},
        {"Year": 2013, "World_Series_Champion": "Boston Red Sox", "League": "AL"},
        {"Year": 2014, "World_Series_Champion": "San Francisco Giants", "League": "NL"},
        {"Year": 2015, "World_Series_Champion": "Kansas City Royals", "League": "AL"},
        {"Year": 2016, "World_Series_Champion": "Chicago Cubs", "League": "NL"},
        {"Year": 2017, "World_Series_Champion": "Houston Astros", "League": "AL"},
        {"Year": 2018, "World_Series_Champion": "Boston Red Sox", "League": "AL"},
        {"Year": 2019, "World_Series_Champion": "Washington Nationals", "League": "NL"},
        {"Year": 2020, "World_Series_Champion": "Los Angeles Dodgers", "League": "NL"},
        {"Year": 2021, "World_Series_Champion": "Atlanta Braves", "League": "NL"},
        {"Year": 2022, "World_Series_Champion": "Houston Astros", "League": "AL"},
        {"Year": 2023, "World_Series_Champion": "Texas Rangers", "League": "AL"},
        {"Year": 2024, "World_Series_Champion": "Los Angeles Dodgers", "League": "NL"},
        {"Year": 2025, "World_Series_Champion": "TBD", "League": "TBD"}
    ]
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save to CSV with proper naming
    df = pd.DataFrame(champions_data)
    output_file = "data/world_series_champions_1975_to_2025.csv"
    df.to_csv(output_file, index=False)
    print(f"Created World Series champions dataset: {output_file}")
    print(f"Records: {len(champions_data)} champions from 1975-2025")

def create_mvp_winners_data():
    """
    Create a comprehensive AL MVP winners dataset for 1975-2025.
    """
    print("Creating AL MVP winners dataset (1975-2025)...")
    
    # Comprehensive data for AL MVP winners (1975-2025)
    mvp_data = [
        {"Year": 1975, "AL_MVP_Winner": "Fred Lynn", "Team": "Boston Red Sox", "Position": "OF"},
        {"Year": 1976, "AL_MVP_Winner": "Thurman Munson", "Team": "New York Yankees", "Position": "C"},
        {"Year": 1977, "AL_MVP_Winner": "Rod Carew", "Team": "Minnesota Twins", "Position": "1B"},
        {"Year": 1978, "AL_MVP_Winner": "Jim Rice", "Team": "Boston Red Sox", "Position": "OF"},
        {"Year": 1979, "AL_MVP_Winner": "Don Baylor", "Team": "California Angels", "Position": "DH"},
        {"Year": 1980, "AL_MVP_Winner": "George Brett", "Team": "Kansas City Royals", "Position": "3B"},
        {"Year": 1981, "AL_MVP_Winner": "Rollie Fingers", "Team": "Milwaukee Brewers", "Position": "P"},
        {"Year": 1982, "AL_MVP_Winner": "Robin Yount", "Team": "Milwaukee Brewers", "Position": "SS"},
        {"Year": 1983, "AL_MVP_Winner": "Cal Ripken Jr.", "Team": "Baltimore Orioles", "Position": "SS"},
        {"Year": 1984, "AL_MVP_Winner": "Willie Hernandez", "Team": "Detroit Tigers", "Position": "P"},
        {"Year": 1985, "AL_MVP_Winner": "Don Mattingly", "Team": "New York Yankees", "Position": "1B"},
        {"Year": 1986, "AL_MVP_Winner": "Roger Clemens", "Team": "Boston Red Sox", "Position": "P"},
        {"Year": 1987, "AL_MVP_Winner": "George Bell", "Team": "Toronto Blue Jays", "Position": "OF"},
        {"Year": 1988, "AL_MVP_Winner": "Jose Canseco", "Team": "Oakland Athletics", "Position": "OF"},
        {"Year": 1989, "AL_MVP_Winner": "Robin Yount", "Team": "Milwaukee Brewers", "Position": "OF"},
        {"Year": 1990, "AL_MVP_Winner": "Rickey Henderson", "Team": "Oakland Athletics", "Position": "OF"},
        {"Year": 1991, "AL_MVP_Winner": "Cal Ripken Jr.", "Team": "Baltimore Orioles", "Position": "SS"},
        {"Year": 1992, "AL_MVP_Winner": "Dennis Eckersley", "Team": "Oakland Athletics", "Position": "P"},
        {"Year": 1993, "AL_MVP_Winner": "Frank Thomas", "Team": "Chicago White Sox", "Position": "1B"},
        {"Year": 1994, "AL_MVP_Winner": "Frank Thomas", "Team": "Chicago White Sox", "Position": "1B"},
        {"Year": 1995, "AL_MVP_Winner": "Mo Vaughn", "Team": "Boston Red Sox", "Position": "1B"},
        {"Year": 1996, "AL_MVP_Winner": "Juan Gonzalez", "Team": "Texas Rangers", "Position": "OF"},
        {"Year": 1997, "AL_MVP_Winner": "Ken Griffey Jr.", "Team": "Seattle Mariners", "Position": "OF"},
        {"Year": 1998, "AL_MVP_Winner": "Juan Gonzalez", "Team": "Texas Rangers", "Position": "OF"},
        {"Year": 1999, "AL_MVP_Winner": "Ivan Rodriguez", "Team": "Texas Rangers", "Position": "C"},
        {"Year": 2000, "AL_MVP_Winner": "Jason Giambi", "Team": "Oakland Athletics", "Position": "1B"},
        {"Year": 2001, "AL_MVP_Winner": "Ichiro Suzuki", "Team": "Seattle Mariners", "Position": "OF"},
        {"Year": 2002, "AL_MVP_Winner": "Miguel Tejada", "Team": "Oakland Athletics", "Position": "SS"},
        {"Year": 2003, "AL_MVP_Winner": "Alex Rodriguez", "Team": "Texas Rangers", "Position": "SS"},
        {"Year": 2004, "AL_MVP_Winner": "Vladimir Guerrero", "Team": "Anaheim Angels", "Position": "OF"},
        {"Year": 2005, "AL_MVP_Winner": "Alex Rodriguez", "Team": "New York Yankees", "Position": "3B"},
        {"Year": 2006, "AL_MVP_Winner": "Justin Morneau", "Team": "Minnesota Twins", "Position": "1B"},
        {"Year": 2007, "AL_MVP_Winner": "Alex Rodriguez", "Team": "New York Yankees", "Position": "3B"},
        {"Year": 2008, "AL_MVP_Winner": "Dustin Pedroia", "Team": "Boston Red Sox", "Position": "2B"},
        {"Year": 2009, "AL_MVP_Winner": "Joe Mauer", "Team": "Minnesota Twins", "Position": "C"},
        {"Year": 2010, "AL_MVP_Winner": "Josh Hamilton", "Team": "Texas Rangers", "Position": "OF"},
        {"Year": 2011, "AL_MVP_Winner": "Justin Verlander", "Team": "Detroit Tigers", "Position": "P"},
        {"Year": 2012, "AL_MVP_Winner": "Miguel Cabrera", "Team": "Detroit Tigers", "Position": "3B"},
        {"Year": 2013, "AL_MVP_Winner": "Miguel Cabrera", "Team": "Detroit Tigers", "Position": "1B"},
        {"Year": 2014, "AL_MVP_Winner": "Mike Trout", "Team": "Los Angeles Angels", "Position": "OF"},
        {"Year": 2015, "AL_MVP_Winner": "Josh Donaldson", "Team": "Toronto Blue Jays", "Position": "3B"},
        {"Year": 2016, "AL_MVP_Winner": "Mike Trout", "Team": "Los Angeles Angels", "Position": "OF"},
        {"Year": 2017, "AL_MVP_Winner": "Jose Altuve", "Team": "Houston Astros", "Position": "2B"},
        {"Year": 2018, "AL_MVP_Winner": "Mookie Betts", "Team": "Boston Red Sox", "Position": "OF"},
        {"Year": 2019, "AL_MVP_Winner": "Mike Trout", "Team": "Los Angeles Angels", "Position": "OF"},
        {"Year": 2020, "AL_MVP_Winner": "Jose Abreu", "Team": "Chicago White Sox", "Position": "1B"},
        {"Year": 2021, "AL_MVP_Winner": "Shohei Ohtani", "Team": "Los Angeles Angels", "Position": "DH/P"},
        {"Year": 2022, "AL_MVP_Winner": "Aaron Judge", "Team": "New York Yankees", "Position": "OF"},
        {"Year": 2023, "AL_MVP_Winner": "Corey Seager", "Team": "Texas Rangers", "Position": "SS"},
        {"Year": 2024, "AL_MVP_Winner": "Aaron Judge", "Team": "New York Yankees", "Position": "OF"},
        {"Year": 2025, "AL_MVP_Winner": "TBD", "Team": "TBD", "Position": "TBD"}
    ]
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save to CSV with proper naming
    df = pd.DataFrame(mvp_data)
    output_file = "data/american_league_mvp_winners_1975_to_2025.csv"
    df.to_csv(output_file, index=False)
    print(f"Created AL MVP winners dataset: {output_file}")
    print(f"Records: {len(mvp_data)} MVP winners from 1975-2025")

def main():
    """
    Main function to run all data collection and cleaning.
    """
    print("Starting MLB data collection and cleaning...")
    
    # Clean existing AL standings data
    clean_al_standings_data()
    
    # Create World Series champions dataset for 1975-2025
    create_world_series_champions_data()
    
    # Create AL MVP winners dataset for 1975-2025  
    create_mvp_winners_data()
    
    print("\nAll data collection and cleaning complete!")
    print("Final datasets created covering 1975-2025:")
    print("• AL team standings: data/american_league_standings_1975_to_2025.csv")
    print("• World Series champions: data/world_series_champions_1975_to_2025.csv")
    print("• AL MVP winners: data/american_league_mvp_winners_1975_to_2025.csv")

if __name__ == "__main__":
    main()
