import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import plotly.io as pio
import time
import plotly.colors as pc

from streamlit_lottie import st_lottie
import requests
from prophet import Prophet
from sklearn.linear_model import LinearRegression
import calendar


def prophet_forecast(df, date_col, value_col, title):
    data = df[[date_col, value_col]].copy()
    data.columns = ['ds', 'y']
    data = data.dropna()
    data = data.groupby('ds').sum().reset_index()

    model = Prophet()
    model.fit(data)

    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)

    fig = px.line(forecast, x='ds', y='yhat', title=title)
    fig.add_scatter(x=data['ds'], y=data['y'], mode='lines', name='Actual')

    return fig, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)



def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()



# Set Streamlit page config
# ========== LOGIN PAGE ========== #

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def login():
    st.title("🔐 Login to Continue")
    

    col1, col2 = st.columns([1, 1.1])

    with col1:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 👤 User Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if username == "admin" and password == "1234":
                    st.session_state.logged_in = True
                    st.success("✅ Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

    with col2:
        lottie_animation = load_lottie_url("https://lottie.host/15847374-7799-4412-8e52-458f231e36c1/bhYbHj214g.json")
        st_lottie(lottie_animation, speed=1, height=300, key="login_anim")


#page congiguration
st.set_page_config(page_title= "Supply Chain Analysis",
                   page_icon= '🧑🏼‍💻',
                   layout= "wide",initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align: center; color: white;'> Automotive Supply Chain Analytics 🤖</h1>", unsafe_allow_html=True)

#=========hide the streamlit main and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

def home_screen():
    st.markdown("""
    Supply Chain Management (SCM) Web Application to help manufacturing industries manage 
                ****inventory, demand forecasting, supplier management, logistics tracking, and production planning**** efficiently.
    """)
    if st.button("Start Analysis"):
       st.session_state.page = "analysis"
    # Create two-column layout
    col_left, col_right = st.columns([1, 1.3])

    with col_left:
        # Supply Chain Animation (Lottie or GIF via HTML)
        # Add a little space then center the Start button
        #st.markdown("### 📦 Supply Chain Animation")
        lottie_supply_chain = load_lottie_url("https://lottie.host/3297fc66-971c-4bb3-b95a-dff01665c381/XlPMCvzUrV.json")  # change this to another if needed
        st_lottie(lottie_supply_chain, speed=1, height=300, key="supplychain")

    with col_right:
        st.markdown("""
        <div style='background-color: rgba(255, 255, 255, 0.1); padding: 25px 30px; 
                    border-radius: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2); 
                    text-align: left; backdrop-filter: blur(3px);'>
            <h3 style='color: #f9f9f9;'>🚀 Key Features</h3>
            <ul style='line-height: 1.8; font-size: 16px; color: #f1f1f1;'>
                <li> <strong>Real-time Inventory Management</strong> – Track stock levels, FIFO/LIFO, and stock movements.</li>
                <li> <strong>Supplier & Procurement Management</strong> – Maintain supplier data, purchase orders, and lead times.</li>
                <li> <strong>Production Planning & Forecasting</strong> – Use machine learning models (Python) for demand forecasting.</li>
                <li> <strong>Logistics & Delivery Tracking</strong> – Track shipments, delays, and optimize routes.</li>
                <li> <strong>Quality Control & Audits</strong> – Integrate with Power Apps 5S Audit system for tracking defects.</li>
                <li> <strong>Data-Driven Decision Making</strong> – Power BI dashboards for KPI tracking (lead time, order fulfillment).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
   


# Initialize login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Show login if not authenticated
if not st.session_state.logged_in:
    login()
    st.stop()   




if "page" not in st.session_state:
    st.session_state.page = "home"
    st.session_state.date_range = None
    st.session_state.supplier_filter = []
    st.session_state.category_filter = []
    st.session_state.status_filter = []

# Function to calculate fiscal week
def calculate_fiscal_week(date):
    fiscal_start = pd.Timestamp(year=date.year if date.month >= 4 else date.year - 1, month=4, day=1)
    return ((date - fiscal_start).days // 7) + 1


def analysis_screen():
    with st.sidebar:
        st.header("📁 Upload Your Dataset")
        uploaded_file = st.file_uploader("Upload your Supply Chain file", type="csv")

    if uploaded_file:
        try:
            df_check = pd.read_csv(uploaded_file)
        except pd.errors.EmptyDataError:
            st.error("❌ The uploaded file is empty or not readable. Please check your CSV.")
            return

        expected_column_count = 10
        if df_check.shape[1] != expected_column_count:
            st.error(f"⚠️ Please upload a file with exactly {expected_column_count} columns. Currently found {df_check.shape[1]} columns.")
            return

        df = df_check.copy()
    

        try:
            df['OrderDate'] = pd.to_datetime(df['OrderDate'])
            df['DeliveryDate'] = pd.to_datetime(df['DeliveryDate'])
        except Exception as e:
            st.error("⚠️ Failed to parse 'OrderDate' or 'DeliveryDate' columns. Please ensure correct datetime format.")
            return

        df.dropna(subset=['OrderDate', 'DeliveryDate'], inplace=True)

        df['OrderDateOnly'] = df['OrderDate'].dt.date
        df['OrderYear'] = df['OrderDate'].dt.year
        df['OrderMonth'] = df['OrderDate'].dt.to_period("M").astype(str)
        df['OrderWeek'] = df['OrderDate'].apply(calculate_fiscal_week)
        df['DeliveryWeek'] = df['DeliveryDate'].apply(calculate_fiscal_week)
        df['LeadTime'] = (df['DeliveryDate'] - df['OrderDate']).dt.days

        min_date = df['OrderDateOnly'].min()
        max_date = df['OrderDateOnly'].max()

        with st.sidebar:
            if st.session_state.date_range is None:
                st.session_state.date_range = (min_date, max_date)
            st.session_state.date_range = st.slider("Select Date Range:", min_value=min_date, max_value=max_date, value=st.session_state.date_range)
            st.session_state.supplier_filter = st.multiselect("Filter by Supplier:", df['Supplier'].unique(), default=st.session_state.supplier_filter)
            st.session_state.category_filter = st.multiselect("Filter by Category:", df['Category'].unique(), default=st.session_state.category_filter)
            st.session_state.status_filter = st.multiselect("Filter by Status:", df['Status'].unique(), default=st.session_state.status_filter)

        df = df[(df['OrderDateOnly'] >= st.session_state.date_range[0]) & (df['OrderDateOnly'] <= st.session_state.date_range[1])]
        if st.session_state.supplier_filter:
            df = df[df['Supplier'].isin(st.session_state.supplier_filter)]
        if st.session_state.category_filter:
            df = df[df['Category'].isin(st.session_state.category_filter)]
        if st.session_state.status_filter:
            df = df[df['Status'].isin(st.session_state.status_filter)]


        # Placeholder messages with delay
        placeholder = st.empty()
        with placeholder:
            st.info("Please wait proccessing...!")

        time.sleep(2)
        placeholder.empty()

       

        # Enhanced KPIs with animations
        st.markdown("""
        <style>
        .kpi-card {
            background-color: #f1f3f6;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .kpi-title {
            font-size: 18px;
            color: #555;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #2a2a2a;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Orders</div>
            <div class="kpi-value">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Deliveries</div>
            <div class="kpi-value">{df['DeliveryDate'].count():,}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Lead Time</div>
            <div class="kpi-value">{df['LeadTime'].mean():.2f} Days</div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                    "Overview", "Category", "Supplier", "Orders", "Time-Series", "YoY Comparison", "Forecast"
                                                            ])

        with tab1:
            # Dataset Preview
            st.subheader("📄 Dataset Preview")

            st.dataframe(df_check.head(), use_container_width=True)

            st.subheader("📄 Manipulated Dataset Preview")
            st.dataframe(df.head(), use_container_width=True)

            # Place inside a tab like Overview or YoY
                                
            st.subheader("📥 Export Dataset")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download Cleaned Dataset",
                data=csv,
                file_name='supply_chain_report.csv',
                mime='text/csv'
            )

            # Dataset Info
            st.subheader("Dataset Overview")
    
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Records", df.shape[0])
            col2.metric("Total Columns", df_check.shape[1])
            col3.metric("Updated Columns", df.shape[1])
            col4.metric("Unique Suppliers", df['Supplier'].nunique())

            # Data Types
            with st.expander("📚 Column Data Types"):
                st.write(df.dtypes)

            # Descriptive Stats
            with st.expander("Descriptive Statistics"):
                st.write(df.describe())

            # Date Ranges
            st.subheader("📅 Order & Delivery Timeline")
            col1, col2 = st.columns(2)
            col1.write(f"**Order Date Range:** {df['OrderDate'].min()} to {df['OrderDate'].max()}")
            col2.write(f"**Delivery Date Range:** {df['DeliveryDate'].min()} to {df['DeliveryDate'].max()}")
        
        with tab2:
            
            st.subheader("📦 Category: Stock vs Ordered Comparison")

            # Group and sum the quantities
            category_group = df.groupby('Category')[['StockQuantity', 'OrderQuantity']].sum().reset_index()

            # Melt to long format for better control over labels
            category_melted = category_group.melt(id_vars='Category', value_vars=['StockQuantity', 'OrderQuantity'],
                                                var_name='Metric', value_name='Quantity')

            # Format numbers with commas
            category_melted['Label'] = category_melted['Quantity'].apply(lambda x: f"{x:,.0f}")

            # Define custom color map
            color_map = {
                'StockQuantity': '#4CAF50',   # Green
                'OrderQuantity': '#E1EEBC'    # green light
            }

            # Create plot
            fig1 = px.bar(
                category_melted,
                y='Category',
                x='Quantity',
                color='Metric',
                text='Label',
                orientation='h',
                barmode='group',
                title="Stock vs Ordered Quantity by Category",
                labels={'Quantity': 'Quantity', 'Metric': 'Metric'},
                color_discrete_map=color_map
            )

            fig1.update_traces(textposition='outside')

            st.plotly_chart(fig1)
            # Get value counts for each category
            category_counts = df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']

            # Generate a gradient color scale (e.g., Viridis or custom)
            gradient_colors = px.colors.sequential.YlGnBu  # You can try Viridis, Blues, etc.

            # Match colors to counts (sorted from high to low)
            category_counts = category_counts.sort_values(by='Count', ascending=False).reset_index(drop=True)
            category_counts['Color'] = gradient_colors[:len(category_counts)]

            # Create pie chart with custom color map
            fig2 = px.pie(
                category_counts,
                names='Category',
                values='Count',
                title="Components Distribution by Category",
                hole=0.5,
                color='Category',
                color_discrete_map=dict(zip(category_counts['Category'], category_counts['Color']))
            )

            st.plotly_chart(fig2)

        with tab3:
            st.info("Please select Category and Status filters to get detailed insights")
            st.subheader("🏷️ Supplier Overview")

            fig3 = px.line(df.groupby(['OrderDate', 'Supplier']).size().reset_index(name='Orders'),
                          x='OrderDate', y='Orders', color='Supplier', title="Supplier Order Trend")
            st.plotly_chart(fig3, use_container_width=True)

            col1, col2 = st.columns(2)
            with col2:
                fig4 = px.pie(df, names='Supplier', title="Supplier Distribution", hole=0.5)
                st.plotly_chart(fig4, use_container_width=True)
                       


            with col1:
                st.subheader("⏱️ ****Average Lead Time by Supplier****")
                lead_time_df = df.groupby('Supplier')['LeadTime'].agg(['mean', 'std']).reset_index()
                lead_time_df.columns = ['Supplier', 'Avg Lead Time', 'Std Deviation']
                lead_time_df = lead_time_df.sort_values(by='Avg Lead Time', ascending=False)
                lead_time_df.index = range(1, len(lead_time_df) + 1)  # Add serial numbers starting from 1
                st.dataframe(lead_time_df, use_container_width=True)

            st.subheader("📊 Supplier Performance Comparison")
    
            performance = df.groupby('Supplier').agg(
                Orders=('OrderQuantity', 'sum'),
                Stock=('StockQuantity', 'sum'),
            ).reset_index()

            # Use custom labels with commas
            performance['OrdersLabel'] = performance['Orders'].apply(lambda x: f"{x:,}")
            performance['StockLabel'] = performance['Stock'].apply(lambda x: f"{x:,}")

            # Melt for long format (to handle text per bar)
            perf_long = performance.melt(id_vars='Supplier', value_vars=['Orders', 'Stock'],
                                        var_name='Metric', value_name='Value')

            # Add custom labels for display
            perf_long['Label'] = perf_long['Value'].apply(lambda x: f"{x:,}")

            bar_fig = px.bar(
                perf_long,
                x='Supplier',
                y='Value',
                color='Metric',
                barmode='group',
                text='Label',
                title="Total Orders vs Stock by Supplier"
            )

            bar_fig.update_traces(textposition='outside')
            st.plotly_chart(bar_fig, use_container_width=True)


        with tab4:
            st.subheader("📋 Order Status by Supplier")

            # Count of each status per supplier
            status_by_supplier = df.groupby(['Supplier', 'Status']).size().reset_index(name='Count')

            # Format counts with commas for labels
            status_by_supplier['Label'] = status_by_supplier['Count'].apply(lambda x: f"{x:,}")

            # Define light-to-dark gradient colors for statuses
            gradient_colors = {
                'Delivered': '#89AC46',  #  green
                'Ordered':   '#FBF8EF',  # white
                'Shifted':   '#B4EBE6',  # light green
                'Delayed':   '#F16767'   # red
            }

            # Create horizontal grouped bar chart
            fig5 = px.bar(status_by_supplier,
                        y='Supplier',
                        x='Count',
                        color='Status',
                        text='Label',
                        color_discrete_map=gradient_colors,
                        barmode='group',
                        orientation='h',
                        title="Supplier-wise Order Status Distribution",
                        labels={'Count': 'Number of Orders', 'Status': 'Order Status'})
            
            fig5.update_traces(textposition='outside')
            # Increase bar spacing
            fig5.update_layout(width=1000,height=700,bargap=0.2, bargroupgap=0.33)
            st.plotly_chart(fig5)

    


            fig6 = px.pie(df, names='Status', title="Order Distribution", hole=0.5)
            st.plotly_chart(fig6)





        with tab5:
            st.info("Please select Category and Status filters to get detailed insights")
            st.subheader("📈 Time-Series: Orders & Deliveries")
            
            
            order_data = df.groupby(['OrderDate', 'Supplier']).size().reset_index(name='Orders')
            delivery_data = df.groupby(['DeliveryDate', 'Supplier']).size().reset_index(name='Deliveries')
            fig7 = px.line(order_data, x='OrderDate', y='Orders', color='Supplier', title="Orders Over Time", markers=True)
            st.plotly_chart(fig7)
            
            
            fig8 = px.line(delivery_data, x='DeliveryDate', y='Deliveries', color='Supplier', title="Deliveries Over Time", markers=True)
            st.plotly_chart(fig8)


        with tab6:
            st.subheader("📆 Year-over-Year (YoY) Orders")
            yoy = df.groupby(['OrderYear', 'OrderMonth']).size().reset_index(name='Orders')
            fig9 = px.line(yoy, x='OrderMonth', y='Orders', color='OrderYear', markers=True, title="YoY Order Trend by Month")
            st.plotly_chart(fig9)

        with tab7:
            st.subheader("📈 Predicted Supplier Performance (Next 6 Months)")

            with st.expander('💡 **How Machine Learning predicted this?**'):
                st.markdown("""
            

                    A simple Linear Regression model was used which analyzes how orders changed over time (`MonthNumber`)
                    and how each supplier (`SupplierCode`) contributes to those trends.

                    - The model assumes a linear relationship between time & order quantity.
                    - Suppliers with increasing past trend show higher forecast.
                    - Suppliers with inconsistent or flat history receive lower future predictions.

                    This approach helps project **supplier-wise demand planning** for the next 6 months.
                    """)

            # Prepare base features
            df['MonthNumber'] = df['OrderDate'].dt.month + 12 * (df['OrderDate'].dt.year - df['OrderDate'].dt.year.min())
            df['SupplierCode'] = df['Supplier'].astype('category').cat.codes

            # Train Linear Regression model
            X = df[['MonthNumber', 'SupplierCode']]
            y = df['OrderQuantity']
            model = LinearRegression()
            model.fit(X, y)

            # Forecasting for next 6 months
            suppliers = df['Supplier'].unique()
            supplier_codes = dict(zip(suppliers, df['Supplier'].astype('category').cat.codes))
            future_month_base = df['MonthNumber'].max()
            
            future_data = []
            future_dates = pd.date_range(start=df['OrderDate'].max() + pd.DateOffset(months=1), periods=6, freq='MS')
            for i, dt in enumerate(future_dates):
                for supplier, code in supplier_codes.items():
                    future_data.append({
                        'Supplier': supplier,
                        'MonthNumber': future_month_base + i + 1,
                        'SupplierCode': code,
                        'MonthYear': dt.strftime('%b-%Y')
                    })

            future_months = pd.DataFrame(future_data)
            future_months['PredictedOrders'] = model.predict(future_months[['MonthNumber', 'SupplierCode']])


            # Table
            #st.dataframe(future_months[['Supplier', 'MonthYear', 'PredictedOrders']].round(2), use_container_width=True)

            # Trend chart
            fig_pred = px.line(
                future_months,
                x='MonthYear',
                y='PredictedOrders',
                color='Supplier',
                markers=True,
                title="Forecasted Orders for Next 6 Months by Supplier"
            )
            fig_pred.update_layout(xaxis_title="Month-Year", yaxis_title="Predicted Order Quantity")
            st.plotly_chart(fig_pred, use_container_width=True)




            # INSIGHT - one high and one low performer
            st.markdown("### 📌 Prediction Insights")

            order_avg = df.groupby('Supplier')['OrderQuantity'].mean().reset_index(name='HistoricalAvg')
            prediction_avg = future_months.groupby('Supplier')['PredictedOrders'].mean().reset_index(name='ForecastedAvg')

            merged_avg = pd.merge(order_avg, prediction_avg, on='Supplier')
            merged_avg['Change'] = merged_avg['ForecastedAvg'] - merged_avg['HistoricalAvg']
            merged_avg['ChangeType'] = merged_avg['Change'].apply(lambda x: 'Increase' if x > 0 else 'Decrease')

            # Get one high and one low
            high_perf = merged_avg.sort_values(by='Change', ascending=False).head(1)
            low_perf = merged_avg.sort_values(by='Change', ascending=True).head(1)

            # Display insight
            if not high_perf.empty:
                row = high_perf.iloc[0]
                st.markdown(f"""
                🟢 **High Performer: {row['Supplier']}**
                - Average historical orders: **{row['HistoricalAvg']:.1f}**
                - Forecasted average: **{row['ForecastedAvg']:.1f}**
                - This supplier is expected to perform better due to strong historical trend.
                """)

            if not low_perf.empty:
                row = low_perf.iloc[0]
                st.markdown(f"""
                🔴 **Low Performer: {row['Supplier']}**
                - Average historical orders: **{row['HistoricalAvg']:.1f}**
                - Forecasted average: **{row['ForecastedAvg']:.1f}**
                - This supplier may face decline possibly due to irregular supply or reduced recent demand.
                """)

            with st.expander("💡 How Prophet Forecasting Works"):
                st.markdown("""
                **Prophet** is a powerful time series forecasting model developed by Facebook.  
                It's built to handle business data with:
                
                - **Trend changes** (e.g., demand increasing over time)
                - **Seasonality** (e.g., monthly or yearly cycles)
                - **Missing data** or outliers (e.g., supply disruptions)
                
                ---
                
                ### How Prophet Works:
                
                - **Trend**: Captures long-term growth or decline in orders or stock levels.
                - **Seasonality**: Learns repeating patterns, like month-end stock dips or quarterly spikes.
                - **Holidays** (optional): Adjusts forecasts if holidays impact delivery or procurement.
                
                ---
                
                ### What Makes Prophet Suitable for Supply Chain:
                
                - Handles **daily or monthly data** effortlessly
                - Can work with **incomplete data**
                - Easy to interpret: breaks down forecast into **trend + seasonality**
                - Ideal for forecasting metrics like:
                    - 📦 StockQuantity
                    - ⏱️ LeadTime
                    - 📅 OrderQuantity
                
                ---
                
                #### 🧑🏼‍💻Behind the Scenes:
                
                Prophet fits your data to a curve using advanced statistics and projects that forward.
                This gives businesses early warning to **prepare inventory, plan logistics, or engage suppliers**.
                """)


            st.subheader("Forecast Using Prophet (6-Months Ahead)")

            # Prophet Forecasting for selected supplier
            if st.checkbox("🔮 Forecast for Selected Supplier (Prophet)"):
                st.subheader("📈 Forecast Orders for a Supplier")

                supplier_selected = st.selectbox("Select Supplier", df['Supplier'].unique())
                supplier_df = df[df['Supplier'] == supplier_selected]

                prophet_data = supplier_df.groupby('OrderDate').agg({'OrderQuantity': 'sum'}).reset_index()
                prophet_data.columns = ['ds', 'y']

                model = Prophet()
                model.fit(prophet_data)

                future = model.make_future_dataframe(periods=180)
                forecast = model.predict(future)

                fig1 = px.line(forecast, x='ds', y='yhat',
                            title=f"📈 Forecasted Order Quantity for {supplier_selected} (Prophet)",
                            labels={'ds': 'Date', 'yhat': 'Predicted Orders'})
                fig1.add_scatter(x=prophet_data['ds'], y=prophet_data['y'], mode='lines', name='Actual')
                st.plotly_chart(fig1, use_container_width=True)

                forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)
                st.dataframe(forecast_display.rename(columns={
                    'ds': 'Date', 'yhat': 'Forecast', 'yhat_lower': 'Lower Bound', 'yhat_upper': 'Upper Bound'
                }), use_container_width=True)

            # Prophet-based forecasting for Lead Time or Stock
            if st.checkbox("⚙️ Show Prophet Forecasts for Lead Time / Stock Level"):
                forecast_option = st.radio("Select Forecast Type", ["Lead Time", "Stock Level"])
                if forecast_option == "Lead Time":
                    fig, table = prophet_forecast(df, "OrderDate", "LeadTime", "📈 Forecasted Lead Time")
                else:
                    fig, table = prophet_forecast(df, "OrderDate", "StockQuantity", "📦 Forecasted Stock Levels")

                st.plotly_chart(fig, use_container_width=True)
               # st.dataframe(table, use_container_width=True)

            # Comparison Chart
            if st.checkbox("📊 Compare Historical vs Forecasted Supplier Orders"):
                comparison_df = merged_avg.melt(id_vars='Supplier', 
                                                value_vars=['HistoricalAvg', 'ForecastedAvg'],
                                                var_name='Metric', value_name='AvgOrders')

                fig_comp = px.bar(comparison_df, x='Supplier', y='AvgOrders', color='Metric',
                                barmode='group', text='AvgOrders',
                                title="Supplier-Wise Avg Order Comparison")
                fig_comp.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                st.plotly_chart(fig_comp, use_container_width=True)

            
      



        #st.subheader("📥 Export Analytical Report")
        #csv = df.describe().to_csv().encode('utf-8')
        #st.download_button("📄 Download Descriptive Stats CSV", data=csv, file_name="descriptive_report.csv", mime="text/csv")

    else:
        st.warning("📤 Please upload a file to begin analysis.")

if st.session_state.page == "home":
    home_screen()
else:
    analysis_screen()














