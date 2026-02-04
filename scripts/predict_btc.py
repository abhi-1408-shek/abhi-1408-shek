"""
Daily Bitcoin Price Predictor
=============================
Fetches live BTC-USD data, trains a RandomForest model,
makes a prediction for tomorrow, and generates a visualization.
"""

import os
import re
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def fetch_data():
    """Fetch 90 days of BTC-USD data."""
    btc = yf.Ticker("BTC-USD")
    df = btc.history(period="90d")
    df = df[['Close']].copy()
    df.columns = ['price']
    return df

def create_features(df):
    """Create lag and moving average features."""
    df = df.copy()
    df['ma_7'] = df['price'].rolling(window=7).mean()
    df['ma_14'] = df['price'].rolling(window=14).mean()
    df['lag_1'] = df['price'].shift(1)
    df['lag_3'] = df['price'].shift(3)
    df['lag_7'] = df['price'].shift(7)
    df = df.dropna()
    return df

def train_model(df):
    """Train RandomForest and return model, predictions, metrics."""
    feature_cols = ['ma_7', 'ma_14', 'lag_1', 'lag_3', 'lag_7']
    X = df[feature_cols]
    y = df['price']
    
    # Train on all but last day, test on last day
    X_train, X_test = X[:-1], X[-1:]
    y_train, y_test = y[:-1], y[-1:]
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Last known prediction (for validation)
    last_pred = model.predict(X_test)[0]
    last_actual = y_test.values[0]
    rmse = np.sqrt(mean_squared_error([last_actual], [last_pred]))
    
    # Predict tomorrow's price using last available features
    tomorrow_features = X.iloc[-1:].copy()
    tomorrow_pred = model.predict(tomorrow_features)[0]
    
    # Get predictions for visualization (last 30 days)
    last_30 = df.tail(30)
    X_viz = last_30[feature_cols]
    y_viz = last_30['price']
    preds_viz = model.predict(X_viz)
    
    return {
        'model': model,
        'predictions': preds_viz,
        'actuals': y_viz.values,
        'dates': y_viz.index,
        'rmse': rmse,
        'tomorrow_pred': tomorrow_pred,
        'last_actual': last_actual
    }

def generate_plot(results):
    """Generate and save the prediction plot."""
    os.makedirs('assets', exist_ok=True)
    
    plt.figure(figsize=(12, 6))
    plt.style.use('dark_background')
    
    plt.plot(results['dates'], results['actuals'], 
             label='Actual Price', color='#00ff88', linewidth=2)
    plt.plot(results['dates'], results['predictions'], 
             label='Model Prediction', color='#ff6b6b', linewidth=2, linestyle='--')
    
    # Add tomorrow's prediction as a point
    tomorrow = results['dates'][-1] + timedelta(days=1)
    plt.scatter([tomorrow], [results['tomorrow_pred']], 
                color='#ffd93d', s=100, zorder=5, label=f"Tomorrow: ${results['tomorrow_pred']:,.0f}")
    
    plt.title(f"🤖 Live ML Experiment: BTC-USD Price Prediction\nRMSE: ${results['rmse']:,.2f}", 
              fontsize=14, fontweight='bold', color='white')
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Price (USD)', fontsize=11)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig('assets/btc_prediction.png', dpi=150, facecolor='#0d1117', edgecolor='none')
    plt.close()
    print(f"✅ Plot saved to assets/btc_prediction.png")

def update_readme(results):
    """Update README.md with latest prediction stats."""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_marker = '<!--START_SECTION:btc-->'
    end_marker = '<!--END_SECTION:btc-->'
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    new_section = f"""{start_marker}
| Metric | Value |
|--------|-------|
| 📈 Tomorrow's Prediction | **${results['tomorrow_pred']:,.2f}** |
| 📉 Last Actual Price | ${results['last_actual']:,.2f} |
| 🎯 Model RMSE | ${results['rmse']:,.2f} |
| 🕐 Last Updated | {now} |

*Model: RandomForestRegressor | Features: MA(7), MA(14), Lag(1,3,7) | Data: Yahoo Finance*
{end_marker}"""
    
    pattern = f'{re.escape(start_marker)}.*?{re.escape(end_marker)}'
    
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, new_section, content, flags=re.DOTALL)
    else:
        # If markers don't exist, this will need to be added manually first
        print("⚠️ BTC section markers not found in README")
        return
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ README updated with prediction: ${results['tomorrow_pred']:,.2f}")

if __name__ == "__main__":
    print("📊 Fetching BTC-USD data...")
    df = fetch_data()
    
    print("🔧 Creating features...")
    df = create_features(df)
    
    print("🤖 Training model...")
    results = train_model(df)
    
    print("🎨 Generating plot...")
    generate_plot(results)
    
    print("📝 Updating README...")
    update_readme(results)
    
    print(f"\n🎉 Done! Tomorrow's BTC prediction: ${results['tomorrow_pred']:,.2f}")
