import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, get_sector_metrics, get_yearly_funding_by_sector, load_unicorn_data, load_saas_data, load_investor_data, train_success_model, predict_success

# --- CONFIG ---
st.set_page_config(page_title="Vantage Point", page_icon="📈", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30333d;
        text-align: center;
    }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #f0f2f6;
    }
    .stMetricValue {
        color: #00ff7f !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA ---
@st.cache_data
def get_data():
    return load_data(), load_unicorn_data(), load_saas_data(), load_investor_data()

try:
    df_raw, df_unicorn, df_saas, df_investors = get_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- ML MODEL ---
@st.cache_resource
def get_model():
    return train_success_model()

model, encoders = get_model() # Load ML model once

# --- SIDEBAR ---
st.sidebar.title("Vantage Point 👁")
st.sidebar.markdown("---")

user_mode = st.sidebar.radio("Observation Lens", ["VC Partner (Macro)", "Founder (Micro)"])

# Global Filters
all_countries = sorted(df_raw['country_code'].dropna().unique())
selected_countries = st.sidebar.multiselect("Region / Country", all_countries, default=['USA', 'GBR', 'CAN', 'IND', 'DEU'])

min_year = int(df_raw['founded_year'].min())
max_year = int(df_raw['founded_year'].max())
selected_years = st.sidebar.slider("Vintage (Founded Year)", 2000, 2014, (2005, 2014))

# Filter
df = df_raw.copy()
if selected_countries:
    df = df[df['country_code'].isin(selected_countries)]
df = df[(df['founded_year'] >= selected_years[0]) & (df['founded_year'] <= selected_years[1])]

# --- HEADER ---
st.title("Vantage Point: Investment Intelligence")
if user_mode == "VC Partner (Macro)":
    st.markdown("### 📊 Macro-Thesis Generation: Where is the Alpha?")
else:
    st.markdown("### 🚀 Founder Strategy: Survival & Valuation Benchmarks")

st.markdown("---")

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📈 Market Trends", 
    "💰 Exit Intelligence", 
    "🌍 Geographic Stratigraphy", 
    "🔬 Sector Deep Dive",
    "🦄 Unicorn Hunter",
    "☁️ SaaS 2025",
    "🤝 Investor Matchmaker",
    "🔮 Crystal Ball"
])

# TAB 1: MARKET TRENDS (Time Series)
with tab1:
    st.subheader("Sector Funding Velocity (CAGR Proxy)")
    
    # Get yearly data
    yearly_funding = get_yearly_funding_by_sector(df, top_n=8)
    
    fig_lines = px.line(
        yearly_funding,
        x="founded_year",
        y="funding_total_usd",
        color="market",
        title="Funding Volume Trajectory by Sector (Top 8)",
        markers=True,
        labels={"funding_total_usd": "Total Funding (USD)", "market": "Sector"}
    )
    st.plotly_chart(fig_lines, use_container_width=True)
    
    st.info("💡 **Insight**: Sectors with steep upward slopes in recent years indicate 'Heating Up' markets. Flat lines suggest maturity or saturation.")

# TAB 2: EXIT INTELLIGENCE (Returns)
with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Time to Liquidity")
        # Box plot of years_to_exit
        exits = df[df['years_to_exit'].notna()]
        top_exit_markets = exits['market'].value_counts().nlargest(10).index
        exit_df = exits[exits['market'].isin(top_exit_markets)]
        
        fig_box = px.box(
            exit_df,
            x="years_to_exit",
            y="market",
            color="market",
            title="Distribution of Time-to-Exit (Years) by Sector",
            labels={"years_to_exit": "Years from Founding to Last Funding"}
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_b:
        st.subheader("Capital Efficiency Frontier")
        # Scatter: Success Rate vs Total Funding Needed
        metrics = get_sector_metrics(df)
        metrics = metrics[metrics['deal_count'] > 20] # Clean noise
        
        fig_eff = px.scatter(
            metrics.reset_index(),
            x="avg_deal_size",
            y="success_rate",
            size="deal_count",
            color="market",
            hover_name="market",
            log_x=True,
            title="Probability of Exit vs. Capital Intensity",
            labels={"avg_deal_size": "Avg Capital Raised (Log)", "success_rate": "Exit Probability (%)"}
        )
        st.plotly_chart(fig_eff, use_container_width=True)
        
    if user_mode == "Founder (Micro)":
        st.success("🚀 **Founder Note**: Shorter boxes mean faster exits. Low 'Avg Capital Raised' means you can exit with less dilution.")

# TAB 3: GEOGRAPHY
with tab3:
    st.subheader("Global Capital Density")
    
    # Aggregate by country
    country_stats = df.groupby('country_code').agg(
        total_funding=('funding_total_usd', 'sum'),
        deal_count=('name', 'count')
    ).reset_index()
    
    fig_map = px.choropleth(
        country_stats,
        locations="country_code",
        locationmode="ISO-3",
        color="total_funding",
        hover_name="country_code",
        color_continuous_scale="Plasma",
        title="Global Funding Intensity (USD)"
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Top Hubs Table
    st.subheader("Emerging Startup Hubs")
    city_stats = df.groupby(['city', 'country_code'])['funding_total_usd'].sum().reset_index().sort_values('funding_total_usd', ascending=False)
    st.dataframe(city_stats.head(10).style.format({'funding_total_usd': '${:,.0f}'}))

# TAB 4: DEEP DIVE (Interactive)
with tab4:
    st.subheader("Sector X-Ray")
    all_markets = sorted(df['market'].unique())
    target_market = st.selectbox("Select Sector to Analyze:", all_markets, index=all_markets.index('Software') if 'Software' in all_markets else 0)
    
    subset = df[df['market'] == target_market]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Deals", len(subset))
    m2.metric("Median Funding", f"${subset['funding_total_usd'].median():,.0f}")
    
    success_count = subset[subset['status'].isin(['acquired', 'ipo'])].shape[0]
    rate = (success_count / len(subset) * 100) if len(subset) > 0 else 0
    m3.metric("Exit Rate", f"{rate:.1f}%")
    
    st.write(f"**Top Companies in {target_market}**")
    st.dataframe(subset.sort_values('funding_total_usd', ascending=False)[['name', 'funding_total_usd', 'status', 'city', 'founded_year']].head(10))

# TAB 5: UNICORN HUNTER
with tab5:
    st.subheader("Unicorn Breeding Grounds")
    
    if df_unicorn.empty:
        st.warning("Unicorn data not found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top Investors in Unicorns**")
            # Parse 'Select Investors' column which is comma separated strings
            investors_series = df_unicorn['Select Investors'].dropna().str.split(', ').explode()
            top_investors = investors_series.value_counts().head(15).reset_index()
            top_investors.columns = ['Investor', 'Count']
            
            fig_uni_inv = px.bar(
                top_investors, 
                x='Count', 
                y='Investor', 
                orientation='h',
                title="Number of Unicorn Portfolio Companies",
                color='Count',
                color_continuous_scale='Magma'
            )
            fig_uni_inv.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_uni_inv, use_container_width=True)
            
        with c2:
            st.markdown("**Speed to Valuation**")
            # Histogram of years joined vs founded
            clean_uni = df_unicorn[(df_unicorn['Years_to_Unicorn'] > 0) & (df_unicorn['Years_to_Unicorn'] < 20)]
            fig_hist = px.histogram(
                clean_uni, 
                x="Years_to_Unicorn", 
                nbins=20,
                title="Distribution of Years to Reach $1B+ Valuation",
                color_discrete_sequence=['#00CC96']
            )
            st.plotly_chart(fig_hist, use_container_width=True)

# TAB 6: SAAS BENCHMARKS
with tab6:
    st.subheader("SaaS Valuation Multiples (2025)")
    
    if df_saas.empty:
        st.warning("SaaS 2025 data not found.")
    else:
        # Calculate Multiple
        # Filter for valid data
        saas_clean = df_saas[(df_saas['ARR_USD'] > 0) & (df_saas['Valuation_USD'] > 0)].copy()
        saas_clean['Multiple'] = saas_clean['Valuation_USD'] / saas_clean['ARR_USD']
        
        # Remove outliers? (Multiple > 100x)
        saas_clean = saas_clean[saas_clean['Multiple'] < 100]
        
        col_s1, col_s2 = st.columns([3, 1])
        
        with col_s1:
            fig_scat = px.scatter(
                saas_clean,
                x='ARR_USD',
                y='Valuation_USD',
                size='Employees',
                color='Multiple',
                hover_name='Company Name',
                log_x=True,
                log_y=True,
                title="Valuation vs ARR (Size = Employee Count, Color = Multiple)",
                labels={'ARR_USD': 'ARR ($)', 'Valuation_USD': 'Valuation ($)'}
            )
            st.plotly_chart(fig_scat, use_container_width=True)
            
        with col_s2:
            median_mult = saas_clean['Multiple'].median()
            st.metric("Median SaaS Multiple", f"{median_mult:.1f}x")
            
            st.markdown("### Top Efficient Companies")
            # Efficiency = Valuation / Employees?
            saas_clean['Val_Per_Emp'] = saas_clean['Valuation_USD'] / saas_clean['Employees']
            st.dataframe(
                saas_clean.sort_values('Val_Per_Emp', ascending=False)[['Company Name', 'Multiple', 'Val_Per_Emp']].head(10).style.format({'Val_Per_Emp': '${:,.0f}'})
            )

# TAB 7: INVESTOR MATCHMAKER
with tab7:
    st.subheader("Find Your Lead Investor")
    
    if df_investors.empty:
        st.warning("Investor data not found.")
    else:
        # Filters
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            search_sector = st.text_input("Filter by Sector (e.g. Fintech, AI)")
        with i_col2:
            search_name = st.text_input("Search Investor Name")
            
        filtered_inv = df_investors.copy()
        
        if search_sector:
            filtered_inv = filtered_inv[filtered_inv['Sectors'].str.contains(search_sector, case=False, na=False)]
        if search_name:
            filtered_inv = filtered_inv[filtered_inv['Name'].str.contains(search_name, case=False, na=False)]
            
        st.dataframe(
            filtered_inv[['Name', 'Title', 'Size Range', 'Sectors', 'Note Investments', 'Location']],
            use_container_width=True,
            hide_index=True
        )

# TAB 8: CRYSTAL BALL
with tab8:
    st.subheader("Startup Success Predictor (Beta)")
    st.info("🤖 **AI Model**: Trained on 60,000+ historical startup outcomes (operating vs exit) from 2015 dataset.")
    
    if model is None:
        st.error("ML Model could not be trained. Check if data file exists.")
    else:
        col_ml1, col_ml2 = st.columns(2)
        
        with col_ml1:
            st.markdown("#### Input Startup DNA")
            p_cat = st.selectbox("Industry / Sector", sorted(encoders[1].classes_))
            p_country = st.selectbox("HQ Location", sorted(encoders[0].classes_), index=list(encoders[0].classes_).index('USA') if 'USA' in encoders[0].classes_ else 0)
            p_funding = st.number_input("Total Funding Raised ($)", min_value=0, value=1000000, step=500000)
            p_rounds = st.number_input("Number of Funding Rounds", min_value=1, value=2, step=1)
            
            if st.button("🔮 Predit Probability of Exit"):
                prob = predict_success(model, encoders, p_funding, p_rounds, p_country, p_cat)
                
                with col_ml2:
                    st.markdown("### Prediction Result")
                    # Gauge Chart
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = prob * 100,
                        title = {'text': "Exit Probability"},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#00ff7f" if prob > 0.5 else "#ff4b4b"},
                            'steps': [
                                {'range': [0, 30], 'color': "#30333d"},
                                {'range': [30, 70], 'color': "#505461"}
                            ]
                        }
                    ))
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    if prob > 0.7:
                        st.success("High Probability of Success! 🚀")
                    elif prob > 0.4:
                        st.warning("Moderate Probability. Execution is key.")
                    else:
                        st.error("High Risk Profile. Proceed with caution.")

