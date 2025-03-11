import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .main {
        background-color: #f5f6fa;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .st-emotion-cache-1y4p8pa {
        padding: 2rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load dataset function with proper date handling
@st.cache_data
def load_data():
    file_path = "data/aircrahesFull_2024.csv"  # Update the actual file path
    df = pd.read_csv(file_path)

    # Ensure 'Year', 'Month', and 'Day' exist before processing
    if all(col in df.columns for col in ['Year', 'Month', 'Day']):
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        df['Month'] = df['Month'].map(month_map)
        df['Day'].fillna(1, inplace=True)
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
    else:
        st.error("Year, Month, or Day column is missing from the dataset.")
    return df

# Load data
df = load_data()

# Sidebar with enhanced styling
with st.sidebar:
    st.header("🔍 Filter Data")
    selected_year = st.select_slider("📅 Select Year", 
                                    options=sorted(df['Year'].unique()),
                                    value=(1940, int(df['Year'].max())))
    selected_country = st.selectbox("🌍 Select Country", 
                                   ["All"] + sorted(df['Country/Region'].dropna().unique().tolist()))
    selected_airline = st.selectbox("✈️ Select Airline", 
                                   ["All"] + sorted(df['Operator'].dropna().unique().tolist()))

# Apply filters
filtered_df = df[(df['Year'] >= selected_year[0]) & (df['Year'] <= selected_year[1])]
if selected_country != "All":
    filtered_df = filtered_df[filtered_df['Country/Region'] == selected_country]
if selected_airline != "All":
    filtered_df = filtered_df[filtered_df['Operator'] == selected_airline]

# Main content
st.title("✈️ Air Crash Analysis Dashboard")
st.markdown("### Aviation Safety Insights Through Data Visualization")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">📅 Total Crashes<br><h2 style="color:#3498db;">{}</h2></div>'.format(
        len(filtered_df)), unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">💀 Total Fatalities<br><h2 style="color:#e74c3c;">{:,}</h2></div>'.format(
        filtered_df['Fatalities (air)'].sum()), unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card">🌍 Countries Affected<br><h2 style="color:#2ecc71;">{}</h2></div>'.format(
        filtered_df['Country/Region'].nunique()), unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card">✈️ Airlines Involved<br><h2 style="color:#9b59b6;">{}</h2></div>'.format(
        filtered_df['Operator'].nunique()), unsafe_allow_html=True)

# Data Preview
with st.expander("📁 View Filtered Data", expanded=False):
    st.dataframe(filtered_df[['Date', 'Country/Region', 'Operator', 
                             'Aircraft Manufacturer', 'Fatalities (air)']],
                height=300,
                use_container_width=True)

# Visualizations
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🌍 Geography", "📊 Insights"])

with tab1:
    st.subheader("Yearly Crash Trend")
    fig, ax = plt.subplots(figsize=(12,6))
    sns.lineplot(data=df.groupby('Year').size().reset_index(name='Crashes'),
                x='Year', y='Crashes', color='#3498db', linewidth=2.5)
    plt.fill_between(df.groupby('Year').size().index,
                    df.groupby('Year').size().values,
                    color='#3498db', alpha=0.1)
    plt.title("Air Crashes Over Time", fontsize=16, pad=20)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number of Crashes", fontsize=12)
    st.pyplot(fig)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Countries")
        top_countries = df['Country/Region'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10,6))
        sns.barplot(x=top_countries.values, y=top_countries.index, 
                   palette="viridis", alpha=0.9)
        plt.title("Countries with Most Crashes", fontsize=14)
        plt.xlabel("Number of Crashes")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Geographical Distribution")
        # Add a map visualization here if you have coordinates data

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fatalities Correlation")
        fig, ax = plt.subplots(figsize=(8,6))
        sns.regplot(x=df['Fatalities (air)'], y=df['Ground'],
                   scatter_kws={'color':'#e74c3c', 'alpha':0.6},
                   line_kws={'color':'#2c3e50'})
        plt.title("Air vs Ground Fatalities", fontsize=14)
        st.pyplot(fig)
    
    with col2:
        st.subheader("Monthly Pattern")
        monthly = df.groupby('Month').size()
        fig, ax = plt.subplots(figsize=(8,6))
        sns.lineplot(x=monthly.index, y=monthly.values,
                    color='#9b59b6', marker='o')
        plt.title("Crashes by Month", fontsize=14)
        plt.xticks(range(1,13), ['Jan','Feb','Mar','Apr','May','Jun',
                                'Jul','Aug','Sep','Oct','Nov','Dec'])
        st.pyplot(fig)


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p>Developed with ❤️ by Eunice | 🚀 Aviation Safety Initiative</p>
    <p>Last Updated: March 2025</p>
</div>
""", unsafe_allow_html=True)