# Belgian Food Delivery Analysis

This project analyzes data from three major food delivery platforms in Belgium: Deliveroo, Takeaway, and Uber Eats, with a particular focus on pizza offerings. The primary goal is to consolidate data from these platforms, perform various analyses, and visualize the results to uncover insights about pricing, restaurant distribution, and value for money.
The project was completed in about two days as a part of a 7 month Data Science Bootcamp with BeCode.

## Features


- **Price Analysis:** Analysis of menu item price distributions.
- **Geospatial Analysis:**
    - Mapping restaurant concentration across Belgium.
    - Geocoding of restaurants to obtain postal codes where missing.
- **Pizza-Specific Analysis:**
    - Identification of top pizza restaurants.
    - "Pizza Value" analysis (price per cm²).
    - Choropleth maps to visualize pizza value by postal code.
- **Delivery Dead Zones:** Identification of areas with low delivery service coverage.
- **Data Consolidation:** Scripts to join data from `deliveroo.db`, `takeaway.db`, and `ubereats.db` into unified CSV files.


## Technologies Used

- Python
- pandas
- geopandas
- matplotlib
- requests
- tqdm

## Setup and Usage

### Prerequisites

1.  **Databases**: This repository does not include the raw data. You need to acquire the following SQLite databases and place them in the `databases/` directory:
    - `deliveroo.db`
    - `takeaway.db`
    - `ubereats.db`

2.  **Python Environment**: It is recommended to use a virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

### Installation

Install the required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Running the Analysis

1.  **Analysis**:
    The analysis scripts in each `analysis/` subdirectory are numbered to be run in sequence.

    ```bash
    # Example for Takeaway data
    python analysis/takeaway/1_price_distribution.py
    python analysis/takeaway/2_geocode_restaurants.py
    # ... and so on.
    ```


2.  **Join Datasets**:
    This script consolidates the data from the three databases into `all_restaurants.csv` and `all_menu_items.csv`.

    ```bash
    python utils/join_datasets.py
    ```

3.  **Run Combined Analysis**:
    Run the scripts in the `analysis/combined/` directory to generate the final analyses and visualizations.

    ```bash
    # Example: Generate pizza value map
    python analysis/combined/6_map_pizza_value.py
    ```

    You can run any of the scripts in the `analysis/combined/` directory to generate the specific outputs.

## Project Structure

```
.
├── analysis/           # Analysis scripts and their outputs
│   ├── combined/       # Scripts for combined analysis of all platforms
│   ├── deliveroo/      # Scripts for Deliveroo-specific analysis
│   ├── takeaway/       # Scripts for Takeaway-specific analysis
│   └── ubereats/       # Scripts for Uber Eats-specific analysis
├── databases/          # Folder for input SQLite databases (not included)
├── shapefiles/         # Geospatial data for Belgium
├── utils/              # Utility scripts (e.g., for joining datasets)
├── .gitignore
├── README.md           # This file
└── requirements.txt    # Python package requirements
```

## Outputs

The analysis scripts generate several outputs, which are saved in the `analysis/{platform}/` directories:

- **CSV files**:
  - `all_restaurants.csv`
  - `all_menu_items.csv`
  - `all_pizza_menu_items.csv`
  - `avg_pizza_price_by_city_all.csv`
- **Plots (`.png`)**:
  - Price distribution histograms.
  - Restaurants per location bar charts.
- **Maps (`.png`)**:
  - Restaurant concentration maps.
  - Choropleth maps showing pizza value and delivery dead zones.
