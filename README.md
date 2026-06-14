# Data-Analytics
Problem Statement 
The real estate market is vast and dynamic, with properties being listed, sold, and evaluated every day. Buyers, sellers, and agents often lack accessible tools to monitor trends, pricing, and sales performance. This project aims to build a Real Estate Listings Dashboard that uses SQL and Streamlit to:
Analyze property listings, agent performance, and sales patterns


Provide insights into pricing, time on market, and property types


Enable filtering by location, property type, price, and sales agent


Display interactive visuals like maps and bar charts for better understanding. 

Business Use Cases
Assist buyers and investors in making data-informed decisions


Help agents track sales performance and property types in demand


Understand pricing trends across regions and neighborhoods


Monitor time-on-market trends to improve sales strategies

Approach
1. Data Preparation
Use the provided datasets:
Read raw JSON files using Python


Flatten nested JSON structures (if any)


Standardize date, numeric, and boolean fields


Ensure date formats and price/area values are consistent


2. Database Creation
Store data in SQL using normalized relationships


Create views and indexes for performance


3. Data Analysis with SQL Queries
Use SQL to generate insights (detailed questions below)
4. Application Development with Streamlit
Create a user-friendly dashboard that allows:
Filtering based on city, property type, agent, and price range


Viewing maps of listings and bar/pie charts


Displaying SQL query outputs as tables and visuals


5. Deployment
Deploy on a local or cloud server to allow real-time access by stakeholders

Data Flow and Architecture
Data Storage:
SQL database with listings, agents, and sales etc. tables


Processing Pipeline:
Use SQL for aggregation, joins, and trend analysis


Deployment:
Streamlit UI for real-time insights and visualizations
