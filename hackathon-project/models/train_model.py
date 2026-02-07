import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import yfinance as yf
from datetime import datetime, timedelta

print("📊 Downloading real market data...")

# Download historical data for stocks and bonds
stocks = yf.download('SPY', start='2010-01-01', end='2024-01-01', progress=False)  # S&P 500
bonds = yf.download('AGG', start='2010-01-01', end='2024-01-01', progress=False)  # US Bonds

# Calculate monthly returns
stocks_monthly = stocks['Close'].resample('ME').last().pct_change().dropna()
bonds_monthly = bonds['Close'].resample('ME').last().pct_change().dropna()

print(f"✅ Downloaded {len(stocks_monthly)} months of market data")


# Calculate performance for different allocations
def calculate_portfolio_metrics(stock_pct, period_months=12):
    """Calculate returns and volatility for a given stock/bond allocation"""
    stock_weight = stock_pct / 100
    bond_weight = 1 - stock_weight

    # Portfolio returns
    portfolio_returns = (stocks_monthly * stock_weight) + (bonds_monthly * bond_weight)

    # Get last N months (cap at available data)
    period_months = min(period_months, len(portfolio_returns))
    recent_returns = portfolio_returns.tail(period_months)

    # Calculate metrics - use .iloc[0] to get scalar values
    avg_return = float(recent_returns.mean() * 12 * 100)  # Annualized %
    volatility = float(recent_returns.std() * np.sqrt(12) * 100)  # Annualized volatility

    return avg_return, volatility


print("🧮 Calculating portfolio performance metrics...")


# Generate training data based on real market performance
def generate_training_data_with_real_returns(n_samples=5000):
    """Generate user profiles matched with real historical performance"""
    data = []

    for i in range(n_samples):
        if i % 1000 == 0:
            print(f"   Generating sample {i}/{n_samples}...")

        # User profile
        age = np.random.randint(22, 70)
        years_to_retirement = max(1, 65 - age + np.random.randint(-5, 5))
        risk_tolerance = np.random.randint(1, 11)
        income = np.random.uniform(30000, 200000)
        expenses = income * np.random.uniform(0.4, 0.9)
        net_worth = np.random.uniform(10000, 2000000)
        portfolio_value = np.random.uniform(5000, net_worth * 0.8)
        monthly_savings = (income - expenses) / 12
        savings_rate = (income - expenses) / income

        # Calculate optimal stock allocation
        base_stock_pct = max(20, min(90, 110 - age))
        risk_adjustment = (risk_tolerance - 5) * 5
        time_adjustment = min(10, years_to_retirement / 2)
        stability_adjustment = (savings_rate - 0.3) * 20

        optimal_stock_pct = base_stock_pct + risk_adjustment + time_adjustment + stability_adjustment
        optimal_stock_pct = max(10, min(95, optimal_stock_pct))

        # Get real historical performance for this allocation
        period = min(years_to_retirement * 12, len(stocks_monthly) - 1)
        period = max(12, period)  # At least 12 months

        try:
            avg_return, volatility = calculate_portfolio_metrics(optimal_stock_pct, period)
        except:
            avg_return, volatility = 8.0, 15.0  # Default if calculation fails

        # Risk category
        if optimal_stock_pct >= 80:
            risk_category = 'Aggressive'
        elif optimal_stock_pct >= 60:
            risk_category = 'Moderate-Aggressive'
        elif optimal_stock_pct >= 40:
            risk_category = 'Moderate'
        else:
            risk_category = 'Conservative'

        data.append({
            'age': age,
            'years_to_retirement': years_to_retirement,
            'risk_tolerance': risk_tolerance,
            'income': income,
            'expenses': expenses,
            'net_worth': net_worth,
            'portfolio_value': portfolio_value,
            'monthly_savings': monthly_savings,
            'savings_rate': savings_rate,
            'stock_allocation': optimal_stock_pct,
            'expected_return': avg_return,
            'expected_volatility': volatility,
            'risk_category': risk_category
        })

    return pd.DataFrame(data)


# Generate training data
df = generate_training_data_with_real_returns(5000)

print(f"\n✅ Generated {len(df)} training samples")
print(f"   Average stock allocation: {df['stock_allocation'].mean():.1f}%")
print(f"   Average expected return: {df['expected_return'].mean():.2f}%")

# Features for prediction
feature_cols = ['age', 'years_to_retirement', 'risk_tolerance', 'income',
                'expenses', 'net_worth', 'portfolio_value', 'monthly_savings', 'savings_rate']

X = df[feature_cols]
y_category = df['risk_category']
y_allocation = df['stock_allocation']

# Train classification model (risk category)
print("\n🤖 Training risk classification model...")
X_train, X_test, y_train, y_test = train_test_split(X, y_category, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print(f"✅ Classification accuracy: {accuracy:.2%}")

# Train regression model (stock allocation %)
print("\n📈 Training allocation regression model...")
X_train, X_test, y_train, y_test = train_test_split(X, y_allocation, test_size=0.2, random_state=42)

reg = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
reg.fit(X_train, y_train)

r2_score = reg.score(X_test, y_test)
print(f"✅ Regression R² score: {r2_score:.3f}")

# Get feature importances
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': reg.feature_importances_
}).sort_values('importance', ascending=False)

print("\n📊 Top 3 most important features:")
for idx, row in feature_importance.head(3).iterrows():
    print(f"   {row['feature']}: {row['importance']:.3f}")

# Save models
print("\n💾 Saving models...")
with open('models/risk_classifier.pkl', 'wb') as f:
    pickle.dump(clf, f)

with open('models/allocation_regressor.pkl', 'wb') as f:
    pickle.dump(reg, f)

with open('models/feature_columns.pkl', 'wb') as f:
    pickle.dump(feature_cols, f)

print("\n✅ Training complete! Models saved:")
print("   - models/risk_classifier.pkl")
print("   - models/allocation_regressor.pkl")
print("   - models/feature_columns.pkl")