import numpy as np
import pandas as pd


def calculate_portfolio_metrics(portfolio_df):
    """Calculate portfolio metrics including Sharpe ratio"""
    if portfolio_df.empty:
        return None

    total_value = portfolio_df['Value'].sum()

    # Calculate returns (simplified - using random for demo)
    returns = np.random.randn(len(portfolio_df)) * 0.1 + 0.05
    portfolio_df['Returns'] = returns

    avg_return = np.average(returns, weights=portfolio_df['Value'])
    volatility = np.std(returns)

    risk_free_rate = 0.02  # 2%
    sharpe_ratio = (avg_return - risk_free_rate) / volatility if volatility > 0 else 0

    return {
        'total_value': total_value,
        'avg_return': avg_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio
    }