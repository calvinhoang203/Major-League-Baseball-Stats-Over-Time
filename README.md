# MLB History Data Analysis Dashboard

Baseball statistics analysis project with web scraping, database storage, and interactive visualizations.

## Project Overview

This project collects Major League Baseball historical data from 1975-2025 and presents it through an interactive dashboard. The data includes World Series champions, American League MVP winners, and team standings.

## Features

- **Web Scraping**: Automated data collection using Selenium
- **Database Storage**: SQLite database with organized tables
- **Interactive Dashboard**: Streamlit web application with visualizations
- **Data Analysis**: Statistical insights and trends over 50 years

## Setup Instructions

### Requirements
- Python 3.8+
- Chrome browser (for web scraping)

### Installation

Clone the repository:
```bash
git clone <your-repo-url>
cd Major-League-Baseball-Stats-Over-Time
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Programs

Run all programs in order:

**Web Scraper** (collects and cleans data):
```bash
python scraping/web_scraper.py
```

**Database Import** (creates SQLite database):
```bash
python scraping/db_import.py
```

**Database Query** (command-line interface):
```bash
python scraping/db_query.py
```

**Dashboard** (interactive web app):
```bash
streamlit run scraping/dashboard.py
```

## Data Sources

- World Series Champions (1975-2025)
- American League MVP Winners (1975-2025)  
- American League Team Standings (2003-2018)

## Dashboard Features

- **Interactive filters**: Year ranges and team selection
- **Multiple visualizations**: Bar charts, scatter plots, pie charts
- **Real-time updates**: Charts respond to user input
- **Data tables**: Raw data viewing and exploration

## Project Structure

```
├── scraping/
│   ├── web_scraper.py      # Data collection and cleaning
│   ├── db_import.py        # CSV to SQLite conversion
│   ├── db_query.py         # Command-line database queries
│   └── dashboard.py        # Streamlit web dashboard
├── data/                   # Generated CSV files
├── database/               # SQLite database
└── requirements.txt        # Python dependencies
```

## Technologies Used

- **Python**: Core programming language
- **Selenium**: Web scraping automation
- **Pandas**: Data manipulation and analysis
- **SQLite**: Database storage
- **Streamlit**: Web dashboard framework
- **Plotly**: Interactive visualizations

## Dashboard Screenshot

![Dashboard](dashboard_screenshot.png)
*Interactive MLB History Dashboard showing World Series champions over time*

---

*Code the Dream Capstone Project - Python Data Analysis & Visualization*