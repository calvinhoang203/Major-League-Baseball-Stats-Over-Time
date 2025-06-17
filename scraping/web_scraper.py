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

if __name__ == "__main__":
    scrape_al_team_standings()
