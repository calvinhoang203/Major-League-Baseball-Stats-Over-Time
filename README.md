# Major League Baseball Stats Over Time

This project scrapes, analyzes, and visualizes historical Major League Baseball data from baseball-almanac.com. It includes four main components:

1. **Web Scraper**: Collects MLB historical data including World Series champions, league leaders in hitting and pitching, and team standings.
2. **Database Import**: Imports the scraped data into a SQLite database.
3. **Database Query**: Provides a command-line interface for querying the database.
4. **Dashboard**: Visualizes the data using Streamlit.

## Project Structure

```
├── data/                  # Directory for CSV files
├── database/              # Directory for SQLite database
├── scraping/              # Python scripts
│   ├── web_scraper.py     # Scrapes data from baseball-almanac.com
│   ├── db_import.py       # Imports CSV files into SQLite database
│   ├── db_query.py        # Command-line interface for querying the database
│   └── dashboard.py       # Streamlit dashboard for visualizing the data
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Major-League-Baseball-Stats-Over-Time.git
   cd Major-League-Baseball-Stats-Over-Time
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Chrome and ChromeDriver for Selenium:
   - Download Chrome from https://www.google.com/chrome/
   - Download ChromeDriver from https://sites.google.com/chromium.org/driver/ and make sure it's in your PATH

## Usage

### 1. Scrape Data

Run the web scraper to collect data from baseball-almanac.com:

```
python scraping/web_scraper.py
```

This will create CSV files in the `data/` directory.

### 2. Import Data into Database

Import the CSV files into a SQLite database:

```
python scraping/db_import.py
```

This will create a SQLite database file in the `database/` directory.

### 3. Query the Database

Run the command-line interface to query the database:

```
python scraping/db_query.py
```

This will start an interactive session where you can:
- Show table structure
- Run custom SQL queries
- Run predefined queries

### 4. Visualize Data

Run the Streamlit dashboard to visualize the data:

```
streamlit run scraping/dashboard.py
```

This will start a local web server and open the dashboard in your browser.

## Features

- **Web Scraper**:
  - Scrapes World Series champions, hitting leaders, pitching leaders, and team standings
  - Handles missing data and different table structures
  - Uses a user agent to avoid being blocked

- **Database Import**:
  - Imports CSV files into a SQLite database
  - Creates separate tables for each dataset
  - Cleans column names for SQL compatibility

- **Database Query**:
  - Provides a command-line interface for querying the database
  - Supports custom SQL queries
  - Includes predefined queries for common analyses

- **Dashboard**:
  - Visualizes data using interactive charts
  - Allows filtering by year range
  - Supports custom analysis with SQL queries


## Acknowledgments

- Data source: [Baseball Almanac](https://www.baseball-almanac.com/)
- Built with Python, Selenium, Pandas, SQLite, and Streamlit