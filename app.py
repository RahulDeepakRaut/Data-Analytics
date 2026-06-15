import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
from streamlit_folium import st_folium
import folium
from datetime import date



# ── Page Config ───

st.set_page_config(
    page_title="Real Estate Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──

st.markdown("""
    <style>
        .main { background-color: #f5f7fa; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stSelectbox, .stMultiSelect { background-color: #ffffff; }
        h1 { color: #1a1a2e; }
        h2 { color: #16213e; }
        h3 { color: #0f3460; }
        .sidebar .sidebar-content { background-color: #1a1a2e; }
    </style>
""", unsafe_allow_html=True)

# ── DB Connection ───

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql369",
        database="real_estate",
        autocommit=True
    )

def run_query(query, params=None):
    try:
        con = get_connection()
        cursor = con.cursor(buffered=True)
        cursor.execute(query, params or ())
        columns = [desc[0] for desc in cursor.description]
        rows    = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        st.error(f"Query Error: {e}")
        return pd.DataFrame()

def run_action(query, params=None):
    try:
        con = get_connection()
        cursor = con.cursor(buffered=True)
        cursor.execute(query, params or ())
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Action Error: {e}")
        return False

# ── Sidebar Navigation ────

st.sidebar.image("https://img.icons8.com/color/96/000000/real-estate.png", width=80)
st.sidebar.title("🏠 Real Estate App")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home",
     "🎛️ Filters & Data",
     "📈 Visualizations",
     "🛠️ CRUD Operations",
     "🔍 SQL Queries"]
)

# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Home":
    st.title("🏠 Real Estate Intelligence Dashboard")
    st.markdown("### Welcome! Here's a quick overview of your database.")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    total_listings = run_query("SELECT COUNT(*) AS cnt FROM listings")
    total_sales    = run_query("SELECT COUNT(*) AS cnt FROM sales")
    total_agents   = run_query("SELECT COUNT(*) AS cnt FROM agents")
    total_buyers   = run_query("SELECT COUNT(*) AS cnt FROM buyers")
    total_props    = run_query("SELECT COUNT(*) AS cnt FROM property_attributes")

    col1.metric("🏘️ Total Listings",   f"{total_listings['cnt'][0]:,}")
    col2.metric("💰 Total Sales",       f"{total_sales['cnt'][0]:,}")
    col3.metric("👤 Total Agents",      f"{total_agents['cnt'][0]:,}")
    col4.metric("🛒 Total Buyers",      f"{total_buyers['cnt'][0]:,}")
    col5.metric("🏗️ Property Records",  f"{total_props['cnt'][0]:,}")

    st.markdown("---")

    col6, col7, col8 = st.columns(3)

    avg_price = run_query("SELECT ROUND(AVG(Price), 2) AS avg FROM listings")
    avg_sale  = run_query("SELECT ROUND(AVG(Sale_Price), 2) AS avg FROM sales")
    avg_days  = run_query("SELECT ROUND(AVG(Days_on_Market), 2) AS avg FROM sales")

    col6.metric("💵 Avg Listing Price",   f"${avg_price['avg'][0]:,.2f}")
    col7.metric("🤝 Avg Sale Price",       f"${avg_sale['avg'][0]:,.2f}")
    col8.metric("📅 Avg Days on Market",   f"{avg_days['avg'][0]} days")

    st.markdown("---")
    st.markdown("### 📋 Database Tables Overview")

    col9, col10 = st.columns(2)
    with col9:
        st.markdown("**Recent Listings**")
        st.dataframe(
            run_query("SELECT Listing_ID, City, Property_Type, Price, Date_Listed FROM listings ORDER BY Date_Listed DESC LIMIT 10"),
            use_container_width=True
        )
    with col10:
        st.markdown("**Recent Sales**")
        st.dataframe(
            run_query("SELECT Listing_ID, Sale_Price, Date_Sold, Days_on_Market FROM sales ORDER BY Date_Sold DESC LIMIT 10"),
            use_container_width=True
        )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — FILTERS & DATA
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🎛️ Filters & Data":
    st.title("🎛️ Filters & Data Explorer")
    st.markdown("---")

    # Load filter options
    cities         = run_query("SELECT DISTINCT City FROM listings ORDER BY City")["City"].tolist()
    prop_types     = run_query("SELECT DISTINCT Property_Type FROM listings ORDER BY Property_Type")["Property_Type"].tolist()
    agents         = run_query("SELECT Agent_ID, Name FROM agents ORDER BY Name")
    price_min_max  = run_query("SELECT MIN(Price), MAX(Price) FROM listings")
    date_min_max   = run_query("SELECT MIN(Date_Listed), MAX(Date_Listed) FROM listings")

    col1, col2 = st.columns(2)

    with col1:
        selected_cities     = st.multiselect("🏙️ City",          cities,     default=cities[:3])
        selected_prop_types = st.multiselect("🏗️ Property Type", prop_types, default=prop_types)
        selected_agent      = st.selectbox("👤 Agent",
            ["All"] + agents["Name"].tolist()
        )

    with col2:
        price_range = st.slider(
            "💰 Price Range ($)",
            min_value=int(price_min_max.iloc[0, 0]),
            max_value=int(price_min_max.iloc[0, 1]),
            value=(int(price_min_max.iloc[0, 0]), int(price_min_max.iloc[0, 1]))
        )
        date_range = st.date_input(
            "📅 Date Listed Range",
            value=(
                pd.to_datetime(date_min_max.iloc[0, 0]),
                pd.to_datetime(date_min_max.iloc[0, 1])
            )
        )

    st.markdown("---")

    # Build dynamic query
    city_filter  = "', '".join(selected_cities) if selected_cities else "', '".join(cities)
    ptype_filter = "', '".join(selected_prop_types) if selected_prop_types else "', '".join(prop_types)

    agent_join   = ""
    agent_filter = ""
    if selected_agent != "All":
        agent_id = agents[agents["Name"] == selected_agent]["Agent_ID"].values[0]
        agent_filter = f"AND l.Agent_ID = '{agent_id}'"

    query = f"""
        SELECT
            l.Listing_ID, l.City, l.Property_Type,
            ROUND(l.Price, 2) AS Price,
            l.Sqft, l.Date_Listed,
            l.Agent_ID,
            ROUND(l.Latitude, 4) AS Latitude,
            ROUND(l.Longitude, 4) AS Longitude
        FROM listings l
        WHERE l.City IN ('{city_filter}')
        AND l.Property_Type IN ('{ptype_filter}')
        AND l.Price BETWEEN {price_range[0]} AND {price_range[1]}
        AND l.Date_Listed BETWEEN '{date_range[0]}' AND '{date_range[1]}'
        {agent_filter}
        ORDER BY l.Date_Listed DESC
    """

    df = run_query(query)

    st.markdown(f"### 📋 Filtered Results — {len(df):,} Listings Found")
    st.dataframe(df, use_container_width=True, height=400)

    col3, col4, col5 = st.columns(3)
    if not df.empty:
        col3.metric("Total Listings", f"{len(df):,}")
        col4.metric("Avg Price",      f"${df['Price'].mean():,.2f}")
        col5.metric("Avg Sqft",       f"{df['Sqft'].mean():,.0f}")

    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        df.to_csv(index=False),
        file_name="filtered_listings.csv",
        mime="text/csv"
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Visualizations":
    st.title("📈 Visualizations")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Map",
        "📊 Bar Charts",
        "🥧 Pie Charts",
        "📈 Line Charts",
        "📋 Tables"
    ])

    # ── Tab 1: Map ────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("🗺️ Interactive Property Listings Map")
        map_data = run_query("""
            SELECT City, Latitude, Longitude, Property_Type,
                   ROUND(Price, 2) AS Price, Listing_ID
            FROM listings
            WHERE Latitude IS NOT NULL AND Longitude IS NOT NULL
            LIMIT 500
        """)

        if not map_data.empty:
            m = folium.Map(
                location=[map_data["Latitude"].mean(), map_data["Longitude"].mean()],
                zoom_start=5
            )
            colors = {"Apartment": "blue", "House": "red", "Condo": "green",
                      "Villa": "purple", "Townhouse": "orange"}

            for _, row in map_data.iterrows():
                folium.CircleMarker(
                    location=[row["Latitude"], row["Longitude"]],
                    radius=6,
                    color=colors.get(row["Property_Type"], "gray"),
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"<b>{row['Listing_ID']}</b><br>"
                        f"City: {row['City']}<br>"
                        f"Type: {row['Property_Type']}<br>"
                        f"Price: ${row['Price']:,.2f}",
                        max_width=200
                    )
                ).add_to(m)

            st_folium(m, width=1200, height=500)

            st.markdown("**Legends:**")
            color_emoji = {
                "blue"   : "🔵",
                "red"    : "🔴",
                "green"  : "🟢",
                "purple" : "🟣",
                "orange" : "🟠"
                }
            for ptype, color in colors.items():
                emoji = color_emoji.get(color, "⚪")
                st.markdown(f"{emoji} {color.capitalize()} = {ptype}")

    # ── Tab 2: Bar Charts ─────────────────────────────────────────────────────
    with tab2:
        st.subheader("📊 Bar Charts")

        col1, col2 = st.columns(2)

        with col1:
            avg_price_city = run_query("""
                SELECT City, ROUND(AVG(Price), 2) AS Avg_Price
                FROM listings GROUP BY City ORDER BY Avg_Price DESC
            """)
            fig1 = px.bar(
                avg_price_city, x="City", y="Avg_Price",
                title="Average Listing Price by City",
                color="Avg_Price", color_continuous_scale="Blues",
                labels={"Avg_Price": "Avg Price ($)"}
            )
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            listings_city = run_query("""
                SELECT City, COUNT(Listing_ID) AS Total_Listings
                FROM listings GROUP BY City ORDER BY Total_Listings DESC
            """)
            fig2 = px.bar(
                listings_city, x="City", y="Total_Listings",
                title="Number of Listings by City",
                color="Total_Listings", color_continuous_scale="Greens",
                labels={"Total_Listings": "Total Listings"}
            )
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            avg_price_type = run_query("""
                SELECT Property_Type, ROUND(AVG(Price), 2) AS Avg_Price
                FROM listings GROUP BY Property_Type ORDER BY Avg_Price DESC
            """)
            fig3 = px.bar(
                avg_price_type, x="Property_Type", y="Avg_Price",
                title="Average Price by Property Type",
                color="Property_Type",
                labels={"Avg_Price": "Avg Price ($)"}
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            agent_perf = run_query("""
                SELECT Name, deals_closed, rating
                FROM agents ORDER BY deals_closed DESC LIMIT 10
            """)
            fig4 = px.bar(
                agent_perf, x="Name", y="deals_closed",
                title="Top 10 Agents by Deals Closed",
                color="rating", color_continuous_scale="RdYlGn",
                labels={"deals_closed": "Deals Closed"}
            )
            fig4.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig4, use_container_width=True)

    # ── Tab 3: Pie Charts ─────────────────────────────────────────────────────
    with tab3:
        st.subheader("🥧 Pie Charts")

        col1, col2 = st.columns(2)

        with col1:
            prop_dist = run_query("""
                SELECT Property_Type, COUNT(*) AS Count
                FROM listings GROUP BY Property_Type
            """)
            fig5 = px.pie(
                prop_dist, names="Property_Type", values="Count",
                title="Distribution of Property Types",
                hole=0.4
            )
            st.plotly_chart(fig5, use_container_width=True)

        with col2:
            buyer_type = run_query("""
                SELECT buyer_type, COUNT(*) AS Count
                FROM buyers GROUP BY buyer_type
            """)
            fig6 = px.pie(
                buyer_type, names="buyer_type", values="Count",
                title="Distribution of Buyer Types",
                hole=0.4
            )
            st.plotly_chart(fig6, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            payment_mode = run_query("""
                SELECT payment_mode, COUNT(*) AS Count
                FROM buyers GROUP BY payment_mode
            """)
            fig7 = px.pie(
                payment_mode, names="payment_mode", values="Count",
                title="Distribution of Payment Modes",
                hole=0.4
            )
            st.plotly_chart(fig7, use_container_width=True)

        with col4:
            furnishing = run_query("""
                SELECT furnishing_status, COUNT(*) AS Count
                FROM property_attributes GROUP BY furnishing_status
            """)
            fig8 = px.pie(
                furnishing, names="furnishing_status", values="Count",
                title="Distribution of Furnishing Status",
                hole=0.4
            )
            st.plotly_chart(fig8, use_container_width=True)

    # ── Tab 4: Line Charts ────────────────────────────────────────────────────
    with tab4:
        st.subheader("📈 Line Charts")

        monthly_sales = run_query("""
            SELECT
                DATE_FORMAT(Date_Sold, '%Y-%m')  AS Month,
                COUNT(Listing_ID)                AS Total_Sales,
                ROUND(AVG(Sale_Price), 2)        AS Avg_Sale_Price,
                ROUND(SUM(Sale_Price), 2)        AS Total_Revenue,
                ROUND(AVG(Days_on_Market), 2)    AS Avg_Days
            FROM sales
            GROUP BY Month ORDER BY Month ASC
        """)

        fig9 = px.line(
            monthly_sales, x="Month", y="Total_Sales",
            title="Monthly Sales Trend",
            markers=True, labels={"Total_Sales": "Total Sales"}
        )
        fig9.update_traces(line_color="#0f3460", line_width=2)
        st.plotly_chart(fig9, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            fig10 = px.line(
                monthly_sales, x="Month", y="Avg_Sale_Price",
                title="Monthly Avg Sale Price Trend",
                markers=True, labels={"Avg_Sale_Price": "Avg Sale Price ($)"}
            )
            fig10.update_traces(line_color="#e94560", line_width=2)
            st.plotly_chart(fig10, use_container_width=True)

        with col2:
            fig11 = px.line(
                monthly_sales, x="Month", y="Avg_Days",
                title="Monthly Avg Days on Market Trend",
                markers=True, labels={"Avg_Days": "Avg Days on Market"}
            )
            fig11.update_traces(line_color="#0f9b58", line_width=2)
            st.plotly_chart(fig11, use_container_width=True)

        fig12 = px.bar(
            monthly_sales, x="Month", y="Total_Revenue",
            title="Monthly Total Revenue",
            color="Total_Revenue", color_continuous_scale="Viridis",
            labels={"Total_Revenue": "Total Revenue ($)"}
        )
        st.plotly_chart(fig12, use_container_width=True)

    # ── Tab 5: Table View ─────────────────────────────────────────────────────
    with tab5:
        st.subheader("📋 Table View with Pagination and Sorting")

        table_choice = st.selectbox(
            "Select Table",
            ["listings", "sales", "agents", "buyers", "property_attributes"]
        )

        page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
        page_num  = st.number_input("Page number", min_value=1, value=1, step=1)
        offset    = (page_num - 1) * page_size

        df_table = run_query(f"SELECT * FROM {table_choice} LIMIT {page_size} OFFSET {offset}")
        total    = run_query(f"SELECT COUNT(*) AS cnt FROM {table_choice}")["cnt"][0]

        st.markdown(f"Showing page **{page_num}** — Rows **{offset+1}** to **{min(offset+page_size, total)}** of **{total:,}** total")
        st.dataframe(df_table, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CRUD OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛠️ CRUD Operations":
    st.title("🛠️ CRUD Operations")
    st.markdown("---")

    table = st.selectbox(
        "Select Table",
        ["agents", "listings", "sales", "buyers", "property_attributes"]
    )

    crud_op = st.radio(
        "Operation",
        ["👁️ View", "➕ Add", "✏️ Update", "🗑️ Delete"],
        horizontal=True
    )

    st.markdown("---")

    # ── VIEW ──────────────────────────────────────────────────────────────────
    if crud_op == "👁️ View":
        st.subheader(f"👁️ View — {table}")
        limit = st.selectbox("Show rows", [10, 25, 50, 100])
        df    = run_query(f"SELECT * FROM {table} LIMIT {limit}")
        st.dataframe(df, use_container_width=True)
        st.info(f"Total records in **{table}**: {run_query(f'SELECT COUNT(*) AS cnt FROM {table}')['cnt'][0]:,}")

    # ── ADD ───────────────────────────────────────────────────────────────────
    elif crud_op == "➕ Add":
        st.subheader(f"➕ Add New Record — {table}")

        if table == "agents":
            with st.form("add_agent"):
                c1, c2 = st.columns(2)
                agent_id   = c1.text_input("Agent ID (e.g. A0051)")
                name       = c2.text_input("Name")
                phone      = c1.text_input("Phone")
                email      = c2.text_input("Email")
                comm_rate  = c1.number_input("Commission Rate", 0.0, 10.0, 2.0)
                deals      = c2.number_input("Deals Closed", 0, 1000, 0)
                rating     = c1.number_input("Rating", 0.0, 5.0, 4.0)
                exp        = c2.number_input("Experience Years", 0, 50, 1)
                avg_days   = c1.number_input("Avg Closing Days", 0, 365, 30)

                if st.form_submit_button("✅ Add Agent"):
                    success = run_action("""
                        INSERT INTO agents
                        (Agent_ID, Name, Phone, Email, commission_rate,
                         deals_closed, rating, experience_years, avg_closing_days)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (agent_id, name, phone, email, comm_rate,
                          deals, rating, exp, avg_days))
                    if success:
                        st.success(f"✅ Agent {agent_id} added successfully!")

        elif table == "listings":
            with st.form("add_listing"):
                c1, c2 = st.columns(2)
                listing_id   = c1.text_input("Listing ID (e.g. L99999)")
                city         = c2.text_input("City")
                prop_type    = c1.selectbox("Property Type", ["Apartment", "House", "Condo", "Villa", "Townhouse"])
                price        = c2.number_input("Price ($)", 0.0, 10000000.0, 500000.0)
                sqft         = c1.number_input("Sqft", 0.0, 100000.0, 1000.0)
                date_listed  = c2.date_input("Date Listed")
                agent_id     = c1.text_input("Agent ID")
                latitude     = c2.number_input("Latitude",  -90.0,  90.0, 37.0)
                longitude    = c1.number_input("Longitude", -180.0, 180.0, -122.0)

                if st.form_submit_button("✅ Add Listing"):
                    success = run_action("""
                        INSERT INTO listings
                        (Listing_ID, City, Property_Type, Price, Sqft,
                         Date_Listed, Agent_ID, Latitude, Longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (listing_id, city, prop_type, price, sqft,
                          str(date_listed), agent_id, latitude, longitude))
                    if success:
                        st.success(f"✅ Listing {listing_id} added successfully!")

        elif table == "sales":
            with st.form("add_sale"):
                c1, c2 = st.columns(2)
                listing_id  = c1.text_input("Listing ID")
                sale_price  = c2.number_input("Sale Price ($)", 0.0, 10000000.0, 500000.0)
                date_sold   = c1.date_input("Date Sold")
                days_market = c2.number_input("Days on Market", 0.0, 365.0, 30.0)

                if st.form_submit_button("✅ Add Sale"):
                    success = run_action("""
                        INSERT INTO sales
                        (Listing_ID, Sale_Price, Date_Sold, Days_on_Market)
                        VALUES (%s, %s, %s, %s)
                    """, (listing_id, sale_price, str(date_sold), days_market))
                    if success:
                        st.success(f"✅ Sale for {listing_id} added successfully!")

        elif table == "buyers":
            with st.form("add_buyer"):
                c1, c2 = st.columns(2)
                buyer_id      = c1.number_input("Buyer ID", 0, 999999, 0)
                sale_id       = c2.text_input("Sale ID")
                buyer_type    = c1.selectbox("Buyer Type", ["Individual", "Investor", "Corporate"])
                payment_mode  = c2.selectbox("Payment Mode", ["Cash", "Loan", "Mortgage"])
                loan_taken    = c1.selectbox("Loan Taken", [0, 1])
                loan_provider = c2.text_input("Loan Provider")
                loan_amount   = c1.number_input("Loan Amount ($)", 0, 100000000, 0)

                if st.form_submit_button("✅ Add Buyer"):
                    success = run_action("""
                        INSERT INTO buyers
                        (buyer_id, sale_id, buyer_type, payment_mode,
                         loan_taken, loan_provider, loan_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (buyer_id, sale_id, buyer_type, payment_mode,
                          loan_taken, loan_provider or None, loan_amount))
                    if success:
                        st.success(f"✅ Buyer {buyer_id} added successfully!")

        elif table == "property_attributes":
            with st.form("add_prop_attr"):
                c1, c2 = st.columns(2)
                attr_id      = c1.number_input("Attribute ID", 0, 999999, 0)
                listing_id   = c2.text_input("Listing ID")
                bedrooms     = c1.number_input("Bedrooms",    0, 20, 3)
                bathrooms    = c2.number_input("Bathrooms",   0, 20, 2)
                floor_num    = c1.number_input("Floor Number", 0, 200, 1)
                total_floors = c2.number_input("Total Floors", 0, 200, 5)
                year_built   = c1.number_input("Year Built",  1800, 2100, 2000)
                is_rented    = c2.selectbox("Is Rented", [0, 1])
                tenant_count = c1.number_input("Tenant Count", 0, 100, 0)
                furnishing   = c2.selectbox("Furnishing Status", ["Furnished", "Semi-Furnished", "Unfurnished"])
                metro_dist   = c1.number_input("Metro Distance (km)", 0.0, 100.0, 5.0)
                parking      = c2.selectbox("Parking Available", [0, 1])
                power        = c1.selectbox("Power Backup", [0, 1])

                if st.form_submit_button("✅ Add Property Attributes"):
                    success = run_action("""
                        INSERT INTO property_attributes
                        (attribute_id, listing_id, bedrooms, bathrooms, floor_number,
                         total_floors, year_built, is_rented, tenant_count,
                         furnishing_status, metro_distance_km, parking_available, power_backup)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (attr_id, listing_id, bedrooms, bathrooms, floor_num,
                          total_floors, year_built, is_rented, tenant_count,
                          furnishing, metro_dist, parking, power))
                    if success:
                        st.success("✅ Property attributes added successfully!")

    # ── UPDATE ────────────────────────────────────────────────────────────────
    elif crud_op == "✏️ Update":
        st.subheader(f"✏️ Update Record — {table}")

        if table == "agents":
            agent_id = st.text_input("Enter Agent ID to update (e.g. A0001)")
            if agent_id:
                df = run_query(f"SELECT * FROM agents WHERE Agent_ID = '{agent_id}'")
                if not df.empty:
                    with st.form("update_agent"):
                        c1, c2   = st.columns(2)
                        name     = c1.text_input("Name",         df["Name"][0])
                        phone    = c2.text_input("Phone",        df["Phone"][0])
                        email    = c1.text_input("Email",        df["Email"][0])
                        comm     = c2.number_input("Commission Rate",    value=float(df["commission_rate"][0]))
                        deals    = c1.number_input("Deals Closed",       value=int(df["deals_closed"][0]))
                        rating   = c2.number_input("Rating",             value=float(df["rating"][0]))
                        exp      = c1.number_input("Experience Years",   value=int(df["experience_years"][0]))
                        avg_days = c2.number_input("Avg Closing Days",   value=int(df["avg_closing_days"][0]))

                        if st.form_submit_button("✅ Update Agent"):
                            success = run_action("""
                                UPDATE agents SET Name=%s, Phone=%s, Email=%s,
                                commission_rate=%s, deals_closed=%s, rating=%s,
                                experience_years=%s, avg_closing_days=%s
                                WHERE Agent_ID=%s
                            """, (name, phone, email, comm, deals, rating, exp, avg_days, agent_id))
                            if success:
                                st.success(f"✅ Agent {agent_id} updated successfully!")
                else:
                    st.warning("Agent ID not found.")

        elif table == "listings":
            listing_id = st.text_input("Enter Listing ID to update (e.g. L00001)")
            if listing_id:
                df = run_query(f"SELECT * FROM listings WHERE Listing_ID = '{listing_id}'")
                if not df.empty:
                    with st.form("update_listing"):
                        c1, c2      = st.columns(2)
                        city        = c1.text_input("City",          df["City"][0])
                        prop_type   = c2.text_input("Property Type", df["Property_Type"][0])
                        price       = c1.number_input("Price",       value=float(df["Price"][0]))
                        sqft        = c2.number_input("Sqft",        value=float(df["Sqft"][0]))
                        agent_id    = c1.text_input("Agent ID",      df["Agent_ID"][0])

                        if st.form_submit_button("✅ Update Listing"):
                            success = run_action("""
                                UPDATE listings SET City=%s, Property_Type=%s,
                                Price=%s, Sqft=%s, Agent_ID=%s
                                WHERE Listing_ID=%s
                            """, (city, prop_type, price, sqft, agent_id, listing_id))
                            if success:
                                st.success(f"✅ Listing {listing_id} updated successfully!")
                else:
                    st.warning("Listing ID not found.")

        elif table == "sales":
            listing_id = st.text_input("Enter Listing ID to update sale (e.g. L00001)")
            if listing_id:
                df = run_query(f"SELECT * FROM sales WHERE Listing_ID = '{listing_id}'")
                if not df.empty:
                    with st.form("update_sale"):
                        c1, c2      = st.columns(2)
                        sale_price  = c1.number_input("Sale Price", value=float(df["Sale_Price"][0]))
                        days_market = c2.number_input("Days on Market", value=float(df["Days_on_Market"][0]))

                        if st.form_submit_button("✅ Update Sale"):
                            success = run_action("""
                                UPDATE sales SET Sale_Price=%s, Days_on_Market=%s
                                WHERE Listing_ID=%s
                            """, (sale_price, days_market, listing_id))
                            if success:
                                st.success(f"✅ Sale for {listing_id} updated successfully!")
                else:
                    st.warning("Listing ID not found in sales.")

        elif table == "buyers":
            buyer_id = st.number_input("Enter Buyer ID to update", min_value=0, step=1)
            if buyer_id:
                df = run_query(f"SELECT * FROM buyers WHERE buyer_id = {buyer_id}")
                if not df.empty:
                    with st.form("update_buyer"):
                        c1, c2        = st.columns(2)
                        buyer_type    = c1.text_input("Buyer Type",    df["buyer_type"][0])
                        payment_mode  = c2.text_input("Payment Mode",  df["payment_mode"][0])
                        loan_amount   = c1.number_input("Loan Amount", value=int(df["loan_amount"][0]))

                        if st.form_submit_button("✅ Update Buyer"):
                            success = run_action("""
                                UPDATE buyers SET buyer_type=%s,
                                payment_mode=%s, loan_amount=%s
                                WHERE buyer_id=%s
                            """, (buyer_type, payment_mode, loan_amount, buyer_id))
                            if success:
                                st.success(f"✅ Buyer {buyer_id} updated successfully!")
                else:
                    st.warning("Buyer ID not found.")

        elif table == "property_attributes":
            attr_id = st.number_input("Enter Attribute ID to update", min_value=0, step=1)
            if attr_id:
                df = run_query(f"SELECT * FROM property_attributes WHERE attribute_id = {attr_id}")
                if not df.empty:
                    with st.form("update_prop"):
                        c1, c2      = st.columns(2)
                        bedrooms    = c1.number_input("Bedrooms",   value=int(df["bedrooms"][0]))
                        bathrooms   = c2.number_input("Bathrooms",  value=int(df["bathrooms"][0]))
                        furnishing  = c1.text_input("Furnishing",   df["furnishing_status"][0])
                        metro_dist  = c2.number_input("Metro Distance (km)", value=float(df["metro_distance_km"][0]))
                        parking     = c1.selectbox("Parking Available", [0, 1], index=int(df["parking_available"][0]))
                        power       = c2.selectbox("Power Backup",      [0, 1], index=int(df["power_backup"][0]))

                        if st.form_submit_button("✅ Update Property"):
                            success = run_action("""
                                UPDATE property_attributes
                                SET bedrooms=%s, bathrooms=%s, furnishing_status=%s,
                                metro_distance_km=%s, parking_available=%s, power_backup=%s
                                WHERE attribute_id=%s
                            """, (bedrooms, bathrooms, furnishing,
                                  metro_dist, parking, power, attr_id))
                            if success:
                                st.success(f"✅ Property attribute {attr_id} updated successfully!")
                else:
                    st.warning("Attribute ID not found.")

    # ── DELETE ────────────────────────────────────────────────────────────────
    elif crud_op == "🗑️ Delete":
        st.subheader(f"🗑️ Delete Record — {table}")
        st.warning("⚠️ This action is permanent and cannot be undone!")

        if table == "agents":
            agent_id = st.text_input("Enter Agent ID to delete (e.g. A0001)")
            if agent_id:
                df = run_query(f"SELECT * FROM agents WHERE Agent_ID = '{agent_id}'")
                if not df.empty:
                    st.dataframe(df)
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        if run_action("DELETE FROM agents WHERE Agent_ID=%s", (agent_id,)):
                            st.success(f"✅ Agent {agent_id} deleted!")
                else:
                    st.warning("Agent ID not found.")

        elif table == "listings":
            listing_id = st.text_input("Enter Listing ID to delete (e.g. L00001)")
            if listing_id:
                df = run_query(f"SELECT * FROM listings WHERE Listing_ID = '{listing_id}'")
                if not df.empty:
                    st.dataframe(df)
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        if run_action("DELETE FROM listings WHERE Listing_ID=%s", (listing_id,)):
                            st.success(f"✅ Listing {listing_id} deleted!")
                else:
                    st.warning("Listing ID not found.")

        elif table == "sales":
            listing_id = st.text_input("Enter Listing ID to delete sale (e.g. L00001)")
            if listing_id:
                df = run_query(f"SELECT * FROM sales WHERE Listing_ID = '{listing_id}'")
                if not df.empty:
                    st.dataframe(df)
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        if run_action("DELETE FROM sales WHERE Listing_ID=%s", (listing_id,)):
                            st.success(f"✅ Sale for {listing_id} deleted!")
                else:
                    st.warning("Listing ID not found in sales.")

        elif table == "buyers":
            buyer_id = st.number_input("Enter Buyer ID to delete", min_value=0, step=1)
            if buyer_id:
                df = run_query(f"SELECT * FROM buyers WHERE buyer_id = {buyer_id}")
                if not df.empty:
                    st.dataframe(df)
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        if run_action("DELETE FROM buyers WHERE buyer_id=%s", (buyer_id,)):
                            st.success(f"✅ Buyer {buyer_id} deleted!")
                else:
                    st.warning("Buyer ID not found.")

        elif table == "property_attributes":
            attr_id = st.number_input("Enter Attribute ID to delete", min_value=0, step=1)
            if attr_id:
                df = run_query(f"SELECT * FROM property_attributes WHERE attribute_id = {attr_id}")
                if not df.empty:
                    st.dataframe(df)
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        if run_action("DELETE FROM property_attributes WHERE attribute_id=%s", (attr_id,)):
                            st.success(f"✅ Attribute {attr_id} deleted!")
                else:
                    st.warning("Attribute ID not found.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — SQL QUERIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 SQL Queries":
    st.title("🔍 SQL Queries Explorer")
    st.markdown("---")

    queries = {
        "1. Average Listing Price by City": """
            SELECT City, ROUND(AVG(Price), 2) AS Avg_Listing_Price
            FROM listings GROUP BY City ORDER BY Avg_Listing_Price DESC
        """,

        "2. Average Price Per Sqft by Property Type": """
            SELECT Property_Type, ROUND(AVG(Price / Sqft), 2) AS Avg_Price_Per_Sqft
            FROM listings WHERE Sqft > 0
            GROUP BY Property_Type ORDER BY Avg_Price_Per_Sqft DESC
        """,

        "3. Furnishing Status Impact on Price": """
            SELECT pa.furnishing_status, COUNT(l.Listing_ID) AS Total_Listings,
                   ROUND(AVG(l.Price), 2) AS Avg_Price,
                   ROUND(MIN(l.Price), 2) AS Min_Price,
                   ROUND(MAX(l.Price), 2) AS Max_Price
            FROM listings l
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY pa.furnishing_status ORDER BY Avg_Price DESC
        """,

        "4. Metro Distance Impact on Price": """
            SELECT
                CASE
                    WHEN pa.metro_distance_km <= 2  THEN '0-2 km'
                    WHEN pa.metro_distance_km <= 5  THEN '2-5 km'
                    WHEN pa.metro_distance_km <= 8  THEN '5-8 km'
                    WHEN pa.metro_distance_km <= 10 THEN '8-10 km'
                    ELSE 'Above 10 km'
                END AS Metro_Range,
                COUNT(l.Listing_ID) AS Total_Listings,
                ROUND(AVG(l.Price), 2) AS Avg_Price
            FROM listings l
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY Metro_Range ORDER BY Avg_Price DESC
        """,

        "5. Rented vs Non-Rented Properties": """
            SELECT
                CASE WHEN pa.is_rented = 1 THEN 'Rented' ELSE 'Not Rented' END AS Rental_Status,
                COUNT(l.Listing_ID) AS Total_Listings,
                ROUND(AVG(l.Price), 2) AS Avg_Price
            FROM listings l
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY pa.is_rented ORDER BY Avg_Price DESC
        """,

        "6. Bedrooms Impact on Price": """
            SELECT pa.bedrooms, COUNT(l.Listing_ID) AS Total_Listings,
                   ROUND(AVG(l.Price), 2) AS Avg_Price
            FROM listings l
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY pa.bedrooms ORDER BY pa.bedrooms ASC
        """,

        "7. Parking and Power Backup Impact": """
            SELECT
                CASE
                    WHEN pa.parking_available=1 AND pa.power_backup=1 THEN 'Parking + Power Backup'
                    WHEN pa.parking_available=1 AND pa.power_backup=0 THEN 'Parking Only'
                    WHEN pa.parking_available=0 AND pa.power_backup=1 THEN 'Power Backup Only'
                    ELSE 'Neither'
                END AS Amenity_Status,
                COUNT(l.Listing_ID) AS Total_Listings,
                ROUND(AVG(l.Price), 2) AS Avg_Price
            FROM listings l
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY pa.parking_available, pa.power_backup ORDER BY Avg_Price DESC
        """,

        "8. Year Built vs Listing Price": """
            SELECT pa.year_built, COUNT(l.Listing_ID) AS Total_Listings,
                   ROUND(AVG(l.Price), 2) AS Avg_Price
            FROM listings l
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY pa.year_built ORDER BY pa.year_built ASC
        """,

        "9. Cities with Highest Avg Property Prices": """
            SELECT City, COUNT(Listing_ID) AS Total_Listings,
                   ROUND(AVG(Price), 2) AS Avg_Price,
                   ROUND(MIN(Price), 2) AS Min_Price,
                   ROUND(MAX(Price), 2) AS Max_Price
            FROM listings GROUP BY City ORDER BY Avg_Price DESC
        """,

        "10. Property Price Bucket Distribution": """
            SELECT
                CASE
                    WHEN Price < 200000                    THEN 'Below 200K'
                    WHEN Price BETWEEN 200000 AND 599999   THEN '200K - 600K'
                    WHEN Price BETWEEN 600000 AND 999999   THEN '600K - 1M'
                    WHEN Price BETWEEN 1000000 AND 1499999 THEN '1M - 1.5M'
                    ELSE 'Above 1.5M'
                END AS Price_Bucket,
                COUNT(Listing_ID) AS Total_Listings,
                ROUND(AVG(Price), 2) AS Avg_Price
            FROM listings GROUP BY Price_Bucket ORDER BY Price_Bucket ASC
        """,

        "11. Average Days on Market by City": """
            SELECT l.City, COUNT(s.Listing_ID) AS Total_Sales,
                   ROUND(AVG(s.Days_on_Market), 2) AS Avg_Days_on_Market,
                   ROUND(AVG(s.Sale_Price), 2) AS Avg_Sale_Price
            FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
            GROUP BY l.City ORDER BY Avg_Days_on_Market ASC
        """,

        "12. Property Types That Sell Fastest": """
            SELECT l.Property_Type, COUNT(s.Listing_ID) AS Total_Sales,
                   ROUND(AVG(s.Days_on_Market), 2) AS Avg_Days_on_Market,
                   ROUND(AVG(s.Sale_Price), 2) AS Avg_Sale_Price
            FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
            GROUP BY l.Property_Type ORDER BY Avg_Days_on_Market ASC
        """,

        "13. Percentage Sold Above Listing Price": """
            SELECT l.City,
                   COUNT(s.Listing_ID) AS Total_Sales,
                   COUNT(CASE WHEN s.Sale_Price > l.Price THEN 1 END) AS Sold_Above,
                   ROUND(COUNT(CASE WHEN s.Sale_Price > l.Price THEN 1 END)
                         / COUNT(s.Listing_ID) * 100, 2) AS Pct_Above_List
            FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
            GROUP BY l.City ORDER BY Pct_Above_List DESC
        """,

        "14. Sale-to-List Price Ratio by City": """
            SELECT l.City, COUNT(s.Listing_ID) AS Total_Sales,
                   ROUND(AVG(l.Price), 2) AS Avg_List_Price,
                   ROUND(AVG(s.Sale_Price), 2) AS Avg_Sale_Price,
                   ROUND(AVG(s.Sale_Price / l.Price) * 100, 2) AS Avg_Ratio
            FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
            WHERE l.Price > 0 GROUP BY l.City ORDER BY Avg_Ratio DESC
        """,

        "15. Listings That Took More Than 90 Days": """
            SELECT s.Listing_ID, l.City, l.Property_Type,
                   ROUND(l.Price, 2) AS List_Price,
                   ROUND(s.Sale_Price, 2) AS Sale_Price,
                   ROUND(s.Days_on_Market, 2) AS Days_on_Market,
                   s.Date_Sold
            FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
            WHERE s.Days_on_Market > 90 ORDER BY s.Days_on_Market DESC
        """,

        "16. Metro Distance Effect on Time on Market": """
            SELECT
                CASE
                    WHEN pa.metro_distance_km <= 2  THEN '0-2 km'
                    WHEN pa.metro_distance_km <= 5  THEN '2-5 km'
                    WHEN pa.metro_distance_km <= 8  THEN '5-8 km'
                    WHEN pa.metro_distance_km <= 10 THEN '8-10 km'
                    ELSE 'Above 10 km'
                END AS Metro_Range,
                COUNT(s.Listing_ID) AS Total_Sales,
                ROUND(AVG(s.Days_on_Market), 2) AS Avg_Days_on_Market,
                ROUND(AVG(s.Sale_Price), 2) AS Avg_Sale_Price
            FROM sales s
            JOIN listings l ON s.Listing_ID = l.Listing_ID
            JOIN property_attributes pa ON l.Listing_ID = pa.listing_id
            GROUP BY Metro_Range ORDER BY Avg_Days_on_Market ASC
        """,

        "17. Monthly Sales Trend": """
            SELECT DATE_FORMAT(Date_Sold, '%Y-%m') AS Month,
                   COUNT(Listing_ID) AS Total_Sales,
                   ROUND(AVG(Sale_Price), 2) AS Avg_Sale_Price,
                   ROUND(SUM(Sale_Price), 2) AS Total_Revenue
            FROM sales GROUP BY Month ORDER BY Month ASC
        """,

        "18. Properties Currently Unsold": """
            SELECT
                l.Listing_ID,
                l.City,
                l.Property_Type,
                ROUND(l.Price, 2)           AS Listing_Price,
                l.Date_Listed,
                l.Agent_ID,
                DATEDIFF(CURDATE(), l.Date_Listed) AS Days_Since_Listed
            FROM listings l
            LEFT JOIN sales s ON l.Listing_ID = s.Listing_ID
            WHERE s.Listing_ID IS NULL
            ORDER BY Days_Since_Listed DESC
        """,

        "19. Agents Who Closed the Most Sales": """
            SELECT
                a.Agent_ID,
                a.Name,
                a.deals_closed,
                a.rating,
                a.experience_years,
                a.commission_rate,
                COUNT(s.Listing_ID)             AS Verified_Sales,
                ROUND(AVG(s.Sale_Price), 2)     AS Avg_Sale_Price,
                ROUND(AVG(s.Days_on_Market), 2) AS Avg_Days_to_Close
            FROM agents a
            LEFT JOIN listings l ON a.Agent_ID = l.Agent_ID
            LEFT JOIN sales s    ON l.Listing_ID = s.Listing_ID
            GROUP BY a.Agent_ID, a.Name, a.deals_closed,
                     a.rating, a.experience_years, a.commission_rate
            ORDER BY a.deals_closed DESC
        """,

        "20. Top Agents by Total Sales Revenue": """
            SELECT
                a.Agent_ID,
                a.Name,
                a.commission_rate,
                a.rating,
                COUNT(s.Listing_ID)                                         AS Total_Sales,
                ROUND(SUM(s.Sale_Price), 2)                                 AS Total_Revenue,
                ROUND(AVG(s.Sale_Price), 2)                                 AS Avg_Sale_Price,
                ROUND(SUM(s.Sale_Price) * a.commission_rate / 100, 2)      AS Est_Commission_Earned
            FROM agents a
            JOIN listings l ON a.Agent_ID   = l.Agent_ID
            JOIN sales s    ON l.Listing_ID = s.Listing_ID
            GROUP BY a.Agent_ID, a.Name, a.commission_rate, a.rating
            ORDER BY Total_Revenue DESC
        """,

        "21. Agents Who Close Deals Fastest": """
            SELECT
                a.Agent_ID,
                a.Name,
                a.avg_closing_days                          AS Recorded_Avg_Closing_Days,
                a.experience_years,
                a.rating,
                COUNT(s.Listing_ID)                         AS Total_Sales,
                ROUND(AVG(s.Days_on_Market), 2)             AS Actual_Avg_Days_on_Market,
                ROUND(MIN(s.Days_on_Market), 2)             AS Fastest_Sale_Days,
                ROUND(MAX(s.Days_on_Market), 2)             AS Slowest_Sale_Days
            FROM agents a
            JOIN listings l ON a.Agent_ID   = l.Agent_ID
            JOIN sales s    ON l.Listing_ID = s.Listing_ID
            GROUP BY a.Agent_ID, a.Name, a.avg_closing_days,
                     a.experience_years, a.rating
            ORDER BY Actual_Avg_Days_on_Market ASC
        """,

        "22. Does Experience Correlate with Deals Closed": """
            SELECT
                CASE
                    WHEN a.experience_years <= 5  THEN '0-5 Years'
                    WHEN a.experience_years <= 10 THEN '6-10 Years'
                    WHEN a.experience_years <= 15 THEN '11-15 Years'
                    WHEN a.experience_years <= 20 THEN '16-20 Years'
                    ELSE '20+ Years'
                END                                         AS Experience_Range,
                COUNT(a.Agent_ID)                           AS Total_Agents,
                ROUND(AVG(a.deals_closed), 2)               AS Avg_Deals_Closed,
                ROUND(AVG(a.rating), 2)                     AS Avg_Rating,
                ROUND(AVG(a.commission_rate), 2)            AS Avg_Commission_Rate,
                ROUND(AVG(a.avg_closing_days), 2)           AS Avg_Closing_Days,
                SUM(a.deals_closed)                         AS Total_Deals_Closed
            FROM agents a
            GROUP BY Experience_Range
            ORDER BY Avg_Deals_Closed DESC
        """,

        "23. Do Higher Rated Agents Close Deals Faster": """
            SELECT
                CASE
                    WHEN a.rating < 3.5 THEN 'Low    (Below 3.5)'
                    WHEN a.rating < 4.0 THEN 'Medium (3.5 - 4.0)'
                    WHEN a.rating < 4.5 THEN 'Good   (4.0 - 4.5)'
                    ELSE                     'Excellent (4.5+)'
                END                                         AS Rating_Category,
                COUNT(a.Agent_ID)                           AS Total_Agents,
                ROUND(AVG(a.rating), 2)                     AS Avg_Rating,
                ROUND(AVG(a.avg_closing_days), 2)           AS Avg_Closing_Days,
                ROUND(AVG(a.deals_closed), 2)               AS Avg_Deals_Closed,
                ROUND(AVG(s.Days_on_Market), 2)             AS Actual_Avg_Days_on_Market
            FROM agents a
            JOIN listings l ON a.Agent_ID   = l.Agent_ID
            JOIN sales s    ON l.Listing_ID = s.Listing_ID
            GROUP BY Rating_Category
            ORDER BY Avg_Closing_Days ASC
        """,

        "24. Average Commission Earned by Each Agent": """
            SELECT
                a.Agent_ID,
                a.Name,
                a.commission_rate,
                a.deals_closed,
                a.rating,
                COUNT(s.Listing_ID)                                         AS Verified_Sales,
                ROUND(AVG(s.Sale_Price), 2)                                 AS Avg_Sale_Price,
                ROUND(SUM(s.Sale_Price), 2)                                 AS Total_Revenue,
                ROUND(SUM(s.Sale_Price) * a.commission_rate / 100, 2)      AS Est_Total_Commission,
                ROUND(AVG(s.Sale_Price) * a.commission_rate / 100, 2)      AS Avg_Commission_Per_Sale
            FROM agents a
            JOIN listings l ON a.Agent_ID   = l.Agent_ID
            JOIN sales s    ON l.Listing_ID = s.Listing_ID
            GROUP BY a.Agent_ID, a.Name, a.commission_rate,
                     a.deals_closed, a.rating
            ORDER BY Est_Total_Commission DESC
        """,

        "25. Agents with Most Active Listings": """
            SELECT
                a.Agent_ID,
                a.Name,
                a.rating,
                a.experience_years,
                a.commission_rate,
                COUNT(l.Listing_ID)             AS Total_Listings,
                COUNT(CASE WHEN s.Listing_ID IS NULL
                      THEN 1 END)               AS Active_Unsold_Listings,
                COUNT(s.Listing_ID)             AS Sold_Listings,
                ROUND(AVG(l.Price), 2)          AS Avg_Listing_Price
            FROM agents a
            JOIN listings l  ON a.Agent_ID   = l.Agent_ID
            LEFT JOIN sales s ON l.Listing_ID = s.Listing_ID
            GROUP BY a.Agent_ID, a.Name, a.rating,
                     a.experience_years, a.commission_rate
            ORDER BY Active_Unsold_Listings DESC
        """

    }

    selected_query = st.selectbox("📂 Select a Query to Run", list(queries.keys()))

    st.markdown("**SQL Query:**")
    st.code(queries[selected_query], language="sql")

    if st.button("▶️ Run Query"):
        with st.spinner("Running query..."):
            df = run_query(queries[selected_query])
            if not df.empty:
                st.markdown(f"**Results — {len(df):,} rows returned:**")
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    "⬇️ Download Results as CSV",
                    df.to_csv(index=False),
                    file_name=f"{selected_query[:20].replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results returned.")