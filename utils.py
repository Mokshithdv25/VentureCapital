import pandas as pd
import numpy as np

def clean_currency(x):
    """
    Cleans currency strings like '- ' or ' 1,000,000 ' into floats.
    Returns 0.0 if invalid.
    """
    if isinstance(x, str):
        # Remove spaces and commas
        clean_str = x.strip().replace(',', '')
        # Handle '-' or empty strings which often represent 0 or missing in CSVs
        if clean_str == '-' or clean_str == '':
            return 0.0
        try:
            return float(clean_str)
        except ValueError:
            return 0.0
    return x

def clean_money_string(x):
    """
    Cleans strings like '$100B', '$50M', '$180,000' into actual floats (USD).
    """
    if not isinstance(x, str):
        return x
    
    s = x.strip().replace('$', '').replace(',', '')
    multiplier = 1.0
    
    if 'B' in s:
        multiplier = 1e9
        s = s.replace('B', '')
    elif 'M' in s:
        multiplier = 1e6
        s = s.replace('M', '')
    elif 'K' in s:
        multiplier = 1e3
        s = s.replace('K', '')
    elif 'T' in s: # Trillion?
        multiplier = 1e12
        s = s.replace('T', '')
        
    try:
        return float(s) * multiplier
    except ValueError:
        return 0.0

def load_data(filepath='investments_VC.csv'):
    """
    Loads and cleans the VC investment data.
    """
    try:
        df = pd.read_csv(filepath, encoding='ISO-8859-1') # specific encoding often needed for this dataset
    except UnicodeDecodeError:
        df = pd.read_csv(filepath)

    # 1. Clean Column Names (strip whitespace)
    df.columns = df.columns.str.strip()

    # 2. Clean Funding Totals
    if 'funding_total_usd' in df.columns:
        if df['funding_total_usd'].dtype == object:
             df['funding_total_usd'] = df['funding_total_usd'].astype(str).apply(clean_currency)

    # 3. Handle Dates
    date_cols = ['founded_at', 'first_funding_at', 'last_funding_at']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 4. Create 'founded_year'
    if 'founded_year' in df.columns:
        df['founded_year'] = pd.to_numeric(df['founded_year'], errors='coerce')
    elif 'founded_at' in df.columns:
        df['founded_year'] = df['founded_at'].dt.year

    # 5. Normalize Status
    if 'status' in df.columns:
        df['status'] = df['status'].astype(str).str.strip().str.lower()
    
    # 6. Normalize Market
    if 'market' in df.columns:
        df['market'] = df['market'].astype(str).str.strip()
    
    # 7. Calculate "Time to Liquidity" (Years) for Exits
    df['years_to_exit'] = np.nan
    exits = df[df['status'].isin(['acquired', 'ipo'])].copy()
    
    mask = exits['last_funding_at'].notna() & exits['founded_at'].notna()
    exits.loc[mask, 'years_to_exit'] = (exits.loc[mask, 'last_funding_at'] - exits.loc[mask, 'founded_at']).dt.days / 365.0
    
    exits.loc[exits['years_to_exit'] < 0.5, 'years_to_exit'] = np.nan
    df.loc[exits.index, 'years_to_exit'] = exits['years_to_exit']

    return df

def get_sector_metrics(df):
    """
    Calculates aggregate metrics per sector (market).
    """
    metrics = df.groupby('market').agg(
        total_funding_usd=('funding_total_usd', 'sum'),
        deal_count=('name', 'count'),
        exit_count=('status', lambda x: x.isin(['acquired', 'ipo']).sum()),
        avg_years_to_exit=('years_to_exit', 'median')
    )

    metrics = metrics[metrics['deal_count'] > 5]
    metrics['success_rate'] = (metrics['exit_count'] / metrics['deal_count']) * 100
    metrics['avg_deal_size'] = metrics['total_funding_usd'] / metrics['deal_count']

    return metrics.sort_values('total_funding_usd', ascending=False)

def get_yearly_funding_by_sector(df, top_n=5):
    """
    Returns time-series data for top N sectors.
    """
    top_sectors = df.groupby('market')['funding_total_usd'].sum().nlargest(top_n).index.tolist()
    subset = df[df['market'].isin(top_sectors)]
    yearly = subset.groupby(['founded_year', 'market'])['funding_total_usd'].sum().reset_index()
    return yearly.sort_values('founded_year')

def load_unicorn_data(filepath='unicorns2022.csv'):
    # Updated to combine 2022 freshness with 2021 metadata (Year Founded)
    # Filepath argument is primarily for the 2022 file
    try:
        df_2022 = pd.read_csv(filepath)
    except Exception:
        return pd.DataFrame()

    # Try to load 2021 data for 'Year Founded'
    try:
        df_2021 = pd.read_csv('Unicorn_Companies2021.csv')
    except Exception:
        df_2021 = pd.DataFrame()
    
    # Clean Valuation 2022
    if 'Last Valuation (Billion $)' in df_2022.columns:
        df_2022['Valuation_USD'] = pd.to_numeric(df_2022['Last Valuation (Billion $)'], errors='coerce') * 1e9
        
    # Dates 2022
    if 'Date Joined' in df_2022.columns:
        df_2022['Date Joined'] = pd.to_datetime(df_2022['Date Joined'], errors='coerce')
        df_2022['Year Joined'] = df_2022['Date Joined'].dt.year
    
    # Merge Year Founded from 2021 if possible
    if not df_2021.empty and 'Company' in df_2021.columns and 'Year Founded' in df_2021.columns:
        # Create a mapping dictionary
        # Clean company names?
        founded_map = df_2021.set_index('Company')['Year Founded'].to_dict()
        df_2022['Year Founded'] = df_2022['Company'].map(founded_map)
        # Create Years to Unicorn
        df_2022['Years_to_Unicorn'] = df_2022['Year Joined'] - df_2022['Year Founded']
    else:
        df_2022['Years_to_Unicorn'] = np.nan

    # Standardize 'Investors' column
    if 'Investors' in df_2022.columns:
        df_2022['Select Investors'] = df_2022['Investors'] 
        
    return df_2022

def load_saas_data(filepath='top_100_saas_companies_2025.csv'):
    try:
        df = pd.read_csv(filepath)
    except Exception:
        return pd.DataFrame()
        
    cols_to_clean = ['Total Funding', 'ARR', 'Valuation']
    for col in cols_to_clean:
        if col in df.columns:
            df[f'{col}_USD'] = df[col].apply(clean_money_string)
            
    if 'Employees' in df.columns:
        df['Employees'] = df['Employees'].astype(str).str.replace(',', '').apply(lambda x: float(str(x).replace('.','',1)) if str(x).replace('.','',1).isdigit() else 0)
        
    return df

def load_investor_data(filepath='VCSheets_Investors.csv'):
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except Exception:
        try:
            df = pd.read_csv(filepath, encoding='ISO-8859-1')
        except:
            return pd.DataFrame()
    return df

# --- ML SECTION ---
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_success_model(filepath='big_startup_secsees_dataset2015.csv'):
    """
    Trains a Random Forest Prediction Model
    """
    try:
        df = pd.read_csv(filepath)
    except Exception:
        return None, None
        
    # Target: Success
    valid_status = ['operating', 'acquired', 'closed', 'ipo']
    df = df[df['status'].isin(valid_status)]
    
    # We define success as Acquisition or IPO
    df['is_success'] = df['status'].apply(lambda x: 1 if x in ['acquired', 'ipo'] else 0)
    
    # CLEANING (Fix for crash)
    # Ensure funding is numeric
    if 'funding_total_usd' in df.columns:
        if df['funding_total_usd'].dtype == object:
             df['funding_total_usd'] = df['funding_total_usd'].astype(str).apply(clean_currency)
    
    # Ensure rounds is numeric
    if 'funding_rounds' in df.columns:
        df['funding_rounds'] = pd.to_numeric(df['funding_rounds'], errors='coerce').fillna(1)
    
    # Feature 1: Primary Category
    df['primary_category'] = df['category_list'].astype(str).apply(lambda x: x.split('|')[0] if isinstance(x, str) else 'Other')
    
    # Feature Selection
    feature_cols = ['funding_total_usd', 'funding_rounds', 'country_code', 'primary_category']
    df_clean = df[feature_cols + ['is_success']].dropna()
    
    # Encoders
    le_country = LabelEncoder()
    le_category = LabelEncoder()
    
    df_clean['country_code_enc'] = le_country.fit_transform(df_clean['country_code'].astype(str))
    
    # Reduce cardinality for categories
    top_cats = df_clean['primary_category'].value_counts().nlargest(50).index
    df_clean['primary_category'] = df_clean['primary_category'].apply(lambda x: x if x in top_cats else 'Other')
    df_clean['category_enc'] = le_category.fit_transform(df_clean['primary_category'])
    
    # Training
    X = df_clean[['funding_total_usd', 'funding_rounds', 'country_code_enc', 'category_enc']]
    y = df_clean['is_success']
    
    model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    model.fit(X, y)
    
    return model, (le_country, le_category)

def predict_success(model, encoders, funding, rounds, country, category):
    le_country, le_category = encoders
    
    # Safe Encoding
    try:
        c_enc = le_country.transform([country])[0]
    except:
        c_enc = 0 
        
    try:
        cat_enc = le_category.transform([category])[0]
    except:
        try:
            cat_enc = le_category.transform(['Other'])[0]
        except:
            cat_enc = 0
            
    X_input = pd.DataFrame({
        'funding_total_usd': [funding],
        'funding_rounds': [rounds],
        'country_code_enc': [c_enc],
        'category_enc': [cat_enc]
    })
    
    return model.predict_proba(X_input)[0][1]
