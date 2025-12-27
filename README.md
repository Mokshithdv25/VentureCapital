# Vantage Point: Investment Intelligence Dashboard

## 🚀 Live Demo

**[👉 Try the Live App Here](https://venturecapital-ujqvnjxgynh5y9ckpesqzi.streamlit.app/)**

Deployed on Streamlit Cloud | Status: ✅ Live

---

## Project Overview
**Vantage Point** is a Streamlit-based investment intelligence dashboard designed to identify high-potential sectors and geographies using historical VC data. It focuses on "Investment Thesis" generation rather than simple data exploration.

## Key Features

### 1. The "Sector Alpha" Matrix
Located in the **Sector Alpha** tab, this is the core analytical tool.
- **X-Axis**: Average Deal Size (Low = Cheap entry).
- **Y-Axis**: Success/Exit Rate (High = Proven liquidity).
- **Bubble Size**: Deal Volume.
- **Insight**: Look for bubbles in the **Top-Left** (High Success, Low Cost) for the best ROI.

### 2. Exit Intelligence Engine
Located in the **Exit Intelligence** tab.
- **Time to Liquidity**: Box plots showing how long it takes to exit in each sector.
- **Capital Efficiency Frontier**: Scatter plot identifying sectors that generate exits with minimal capital injection.

### 3. Geographic Stratigraphy
Located in the **Geographic Stratigraphy** tab.
- **Choropleth Map**: Visualizes global capital density.
- **Emerging Hubs**: Identifies cities with high funding velocity.

### 4. Interactive Deep Dive
Located in the **Sector Deep Dive** tab.
- Select any sector to get a "One-Pager" analysis: Median Funding, Exit Rate, and Top Companies.

### 5. 🦄 Unicorn Hunter
Located in the **Unicorn Hunter** tab.
- **Top Investors**: Who creates the most unicorns? (e.g., Sequoia, Accel).
- **Speed to Value**: Histogram of how many years it takes to reach $1B valuation.

### 6. ☁️ SaaS Benchmarks (2025)
Located in the **SaaS 2025** tab.
- **Valuation Multiples**: Live 2025 data showing the relationship between ARR and Valuation.
- **Rule of 40**: Identifies efficient growth leaders.

### 7. 🤝 Investor Matchmaker
Located in the **Investor Matchmaker** tab.
- **Searchable Database**: Filter investors by sector, check size, and recent investments.

### 8. 🔮 Crystal Ball (Predictive AI)
Located in the **Crystal Ball** tab.
- **Machine Learning**: Uses a Random Forest model trained on 60,000+ historical startup outcomes (Operating vs Acquired/IPO).
- **Interactive Prediction**: Input potential deal stats (Funding, Sector, Location) to get an "Exit Probability" score.

## 📸 Screenshots

### Dashboard Overview
<!-- Add your main dashboard screenshot here -->
![Dashboard Overview](screenshots/dashboard-overview.png)
*Main dashboard view showing all analytical tabs*

### Market Trends Analysis
<!-- Add screenshot of Market Trends tab -->
![Market Trends](screenshots/market-trends.png)
*Time-series analysis of funding velocity by sector*

### Exit Intelligence
<!-- Add screenshot of Exit Intelligence tab -->
![Exit Intelligence](screenshots/exit-intelligence.png)
*Capital efficiency frontier and time-to-liquidity analysis*

### Geographic Stratigraphy
<!-- Add screenshot of Geographic tab -->
![Geographic Stratigraphy](screenshots/geographic-stratigraphy.png)
*Global capital density visualization*

### Crystal Ball (ML Predictions)
<!-- Add screenshot of Crystal Ball tab -->
![Crystal Ball](screenshots/crystal-ball.png)
*Machine learning-powered startup success predictor*

### Unicorn Hunter
<!-- Add screenshot of Unicorn Hunter tab -->
![Unicorn Hunter](screenshots/unicorn-hunter.png)
*Top investors and speed-to-valuation metrics*

**Note**: To add screenshots, create a `screenshots/` folder in your repository and add your images there. Update the paths above accordingly.

## How to Run

### Local Deployment

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```
   *Or use the helper script:*
   ```bash
   ./run_project.sh
   ```

### Streamlit Cloud Deployment

Deploy your app to Streamlit Cloud in minutes:

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**:
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository: `Mokshithdv25/VentureCapital`
   - Set the **Main file path** to: `app.py`
   - Click "Deploy"

3. **Your app will be live** at: `https://venturecapital-ujqvnjxgynh5y9ckpesqzi.streamlit.app`

**Note**: Streamlit Cloud automatically:
- Installs dependencies from `requirements.txt`
- Uses the configuration from `.streamlit/config.toml`
- Deploys from the `main` branch (or your default branch)

## Files
- `app.py`: Main dashboard logic and UI.
- `utils.py`: Data cleaning and financial metric calculations.
- `run_project.sh`: One-click launcher.
- `.streamlit/config.toml`: Streamlit configuration for cloud deployment.
