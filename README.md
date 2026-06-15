# 🏠 Real Estate Market Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

A full-stack **Real Estate Data Analytics Platform** built with Python, MySQL, and Streamlit —
designed to transform raw property data into actionable business intelligence for real estate
professionals, investors, and market analysts.

---

## 📌 Project Overview

The real estate market generates vast amounts of transactional data that often goes underutilized.
This platform bridges the gap between raw data and strategic decision-making by providing:

- **End-to-end data pipeline** from raw JSON/CSV files into a structured MySQL database
- **25+ analytical SQL queries** covering pricing, agent performance, buyer behavior and market trends
- **Interactive Streamlit dashboard** with filters, visualizations, CRUD operations and live query execution
- **Business-ready insights** to support pricing strategy, agent evaluation and investment decisions

---

## 🗄️ Database Schema

The platform is built on **5 relational tables** storing 40,000+ records across the real estate lifecycle:

| Table | Records | Description |
|---|---|---|
| `listings` | 20,000+ | Property listings with city, type, price, sqft, location |
| `property_attributes` | 20,000+ | Bedrooms, bathrooms, furnishing, metro distance, amenities |
| `sales` | 720 | Closed sales with sale price, date sold, days on market |
| `buyers` | 20,000 | Buyer profiles, payment mode, loan details |
| `agents` | 50 | Agent profiles, commission rates, ratings, experience |

### Entity Relationship

agents ──< listings ──< sales
│
property_attributes
│
buyers
---

## 📊 Business Intelligence & Key Insights

### 🏙️ Market & Pricing Analysis
| Query | Business Question |
|---|---|
| Avg Price by City | Which cities command premium valuations? |
| Price per Sqft by Type | Where is the best value per square foot? |
| Price Bucket Distribution | How is inventory spread across price segments? |
| Year Built vs Price | Do newer constructions command higher prices? |
| City Rankings | Which markets are most expensive? |

### 🏗️ Property Attribute Analysis
| Query | Business Question |
|---|---|
| Furnishing Status Impact | How much does furnishing add to property value? |
| Metro Distance vs Price | Does proximity to metro drive up prices? |
| Bedrooms & Bathrooms | How do room counts affect pricing? |
| Parking & Power Backup | What is the premium for key amenities? |
| Rented vs Non-Rented | Do investment properties price differently? |

### 📈 Sales & Market Dynamics
| Query | Business Question |
|---|---|
| Monthly Sales Trend | When is the market most active? |
| Days on Market by City | Which cities have the fastest moving inventory? |
| Fastest Selling Property Types | Which property types sell quickest? |
| Sale-to-List Price Ratio | Are properties selling above or below asking? |
| % Sold Above List Price | How competitive is bidding in each city? |
| Listings > 90 Days | Which properties are struggling to sell? |
| Metro Distance vs Time on Market | Does location speed up or slow down sales? |
| Currently Unsold Properties | What inventory is still active? |

### 👤 Agent Performance Analysis
| Query | Business Question |
|---|---|
| Most Deals Closed | Who are the top performing agents? |
| Highest Revenue Agents | Which agents generate the most sales value? |
| Fastest Closing Agents | Who closes deals most efficiently? |
| Experience vs Deals Closed | Does seniority drive better results? |
| Rating vs Closing Speed | Do higher rated agents close faster? |
| Commission Earned per Agent | What is each agent's estimated earnings? |
| Most Active Listings | Which agents have the most unsold inventory? |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data Storage | MySQL 8.0 | Relational database for all 5 tables |
| Data Processing | Python 3.8+ | ETL pipeline, data cleaning, query execution |
| Data Manipulation | Pandas | DataFrame operations and transformations |
| Dashboard | Streamlit | Interactive web application |
| Visualizations | Plotly | Interactive charts and graphs |
| Mapping | Folium + streamlit-folium | Interactive property location maps |
| DB Connector | mysql-connector-python | Python to MySQL bridge |

---

## 📁 Project Structure
real-estate-intelligence/

│
├── data
│   ├── agents_cleaned.json
│   ├── buyers_cleaned.json
│   ├── listings_final_expanded.json
│   ├── property_attributes_final_expanded.json
│   └── sales_cleaned.csv
│
├── database/
│   ├── insert_agents.py
│   ├── insert_buyers.py
│   ├── insert_listings.py
│   ├── insert_property_attributes.py
│   ├── insert_sales.sql
│   └── schema.sql
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md
---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/real-estate-intelligence.git
cd real-estate-intelligence
```

### 2. Install Dependencies
```bash
pip install streamlit plotly pandas mysql-connector-python folium streamlit-folium
```

### 3. Configure MySQL
```python
# Update connection details in app.py
con = mysql.connector.connect(
    host     = "localhost",
    user     = "your_username",
    password = "your_password",
    database = "real_estate"
)
```

### 4. Load Data into MySQL
```bash
# Run each insert script in order
python database/insert_agents.py
python database/insert_buyers.py
python database/insert_listings.py
python database/insert_property_attributes.py

# For sales — run insert_sales.sql directly in MySQL Workbench
# File → Open SQL Script → insert_sales.sql → Run
```

### 5. Launch the App
```bash
streamlit run app.py
```

---

## 🖥️ Application Pages

### 🏠 Home
- 8 KPI metrics — total listings, sales, agents, buyers, avg price, avg sale price, avg days on market
- Recent listings and recent sales preview tables

### 🎛️ Filters & Data Explorer
- Multi-select city filter
- Property type dropdown
- Price range slider
- Agent searchable dropdown
- Date range picker for listing date
- Downloadable filtered results as CSV

### 📈 Visualizations
- **Map Tab** — Interactive Folium map with color-coded property markers by type
- **Bar Charts** — Avg price by city, listings by city, price by property type, top agents by deals
- **Pie Charts** — Property type distribution, buyer type, payment mode, furnishing status
- **Line Charts** — Monthly sales trend, avg sale price trend, avg days on market trend, monthly revenue
- **Table View** — Paginated and sortable view of all 5 database tables

### 🛠️ CRUD Operations
Full **Create, Read, Update, Delete** support for all 5 tables:
- `agents` — manage agent profiles and performance metrics
- `listings` — add, edit or remove property listings
- `sales` — record and manage closed transactions
- `buyers` — maintain buyer profiles and loan details
- `property_attributes` — update property features and amenities

### 🔍 SQL Queries Explorer
- 25 business intelligence queries in dropdown format
- Live SQL code display for each query
- Results rendered as interactive sortable tables
- One-click CSV download for every query result

---

## 📈 Sample Business Insights

> Based on the analytical queries built into this platform, here are the types of insights
> real estate professionals can extract:

- 🏙️ **City Pricing** — Identify which cities have the highest avg listing prices to guide investment decisions
- ⚡ **Market Speed** — Discover which property types and cities have the fastest turnaround to optimize listing strategy
- 🤝 **Agent ROI** — Evaluate agent performance by deals closed, revenue generated and commission earned
- 🏗️ **Amenity Premium** — Quantify exactly how much parking, power backup and metro proximity add to property value
- 📅 **Seasonality** — Track monthly sales trends to time listings for maximum market activity
- 💰 **Pricing Strategy** — Use sale-to-list ratios to set competitive asking prices in each market
- 🔍 **Stale Inventory** — Identify listings sitting unsold for 90+ days to trigger repricing or remarketing

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository
2. Create your feature branch `git checkout -b feature/AmazingFeature`
3. Commit your changes `git commit -m 'Add some AmazingFeature'`
4. Push to the branch `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

Built with ❤️ for real estate data analytics.
Turning property data into business intelligence — one query at a time.

---

*If you found this project useful, please consider giving it a ⭐ on GitHub!*
