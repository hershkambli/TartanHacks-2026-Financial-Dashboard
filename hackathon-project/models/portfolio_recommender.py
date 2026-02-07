import pickle
import numpy as np
import pandas as pd


class PortfolioRecommender:
    def __init__(self):
        # Load the trained models
        with open('models/risk_classifier.pkl', 'rb') as f:
            self.risk_classifier = pickle.load(f)

        with open('models/allocation_regressor.pkl', 'rb') as f:
            self.allocation_regressor = pickle.load(f)

        with open('models/feature_columns.pkl', 'rb') as f:
            self.feature_columns = pickle.load(f)

    def get_recommendations(self, user_profile):
        """
        Get personalized investment recommendations

        user_profile should contain:
        - age
        - years_to_retirement
        - risk_tolerance (1-10)
        - income
        - expenses
        - net_worth
        - portfolio_value
        - monthly_savings
        - savings_rate
        """
        # Prepare features
        features = pd.DataFrame([user_profile])[self.feature_columns]

        # Predict risk category
        risk_category = self.risk_classifier.predict(features)[0]

        # Predict optimal stock allocation
        stock_allocation = self.allocation_regressor.predict(features)[0]
        stock_allocation = max(10, min(95, stock_allocation))  # Bounds check
        bond_allocation = 100 - stock_allocation

        # Get stock recommendations based on allocation and risk
        stock_recommendations = self._get_stock_recommendations(risk_category, stock_allocation)
        bond_recommendations = self._get_bond_recommendations(bond_allocation)

        return {
            'risk_category': risk_category,
            'stock_allocation': round(stock_allocation, 1),
            'bond_allocation': round(bond_allocation, 1),
            'recommended_stocks': stock_recommendations,
            'recommended_bonds': bond_recommendations
        }

    def _get_stock_recommendations(self, risk_category, stock_allocation):
        """Recommend specific stocks based on risk profile"""

        stock_universe = {
            'Conservative': [
                {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'weight': 20},
                {'ticker': 'PG', 'name': 'Procter & Gamble', 'weight': 20},
                {'ticker': 'KO', 'name': 'Coca-Cola', 'weight': 15},
                {'ticker': 'VZ', 'name': 'Verizon', 'weight': 15},
                {'ticker': 'PEP', 'name': 'PepsiCo', 'weight': 15},
                {'ticker': 'WMT', 'name': 'Walmart', 'weight': 15},
            ],
            'Moderate': [
                {'ticker': 'AAPL', 'name': 'Apple', 'weight': 20},
                {'ticker': 'MSFT', 'name': 'Microsoft', 'weight': 20},
                {'ticker': 'V', 'name': 'Visa', 'weight': 15},
                {'ticker': 'JPM', 'name': 'JPMorgan Chase', 'weight': 15},
                {'ticker': 'UNH', 'name': 'UnitedHealth', 'weight': 15},
                {'ticker': 'HD', 'name': 'Home Depot', 'weight': 15},
            ],
            'Moderate-Aggressive': [
                {'ticker': 'GOOGL', 'name': 'Google', 'weight': 20},
                {'ticker': 'NVDA', 'name': 'NVIDIA', 'weight': 20},
                {'ticker': 'AMZN', 'name': 'Amazon', 'weight': 15},
                {'ticker': 'META', 'name': 'Meta', 'weight': 15},
                {'ticker': 'NFLX', 'name': 'Netflix', 'weight': 15},
                {'ticker': 'CRM', 'name': 'Salesforce', 'weight': 15},
            ],
            'Aggressive': [
                {'ticker': 'TSLA', 'name': 'Tesla', 'weight': 20},
                {'ticker': 'COIN', 'name': 'Coinbase', 'weight': 15},
                {'ticker': 'PLTR', 'name': 'Palantir', 'weight': 15},
                {'ticker': 'ARKK', 'name': 'ARK Innovation ETF', 'weight': 15},
                {'ticker': 'MSTR', 'name': 'MicroStrategy', 'weight': 15},
                {'ticker': 'RIOT', 'name': 'Riot Platforms', 'weight': 10},
                {'ticker': 'MARA', 'name': 'Marathon Digital', 'weight': 10},
            ],
        }

        return stock_universe.get(risk_category, stock_universe['Moderate'])

    def _get_bond_recommendations(self, bond_allocation):
        """Recommend bond types and allocation"""

        if bond_allocation < 20:
            return [
                {'type': 'Short-term Treasury Bonds', 'ticker': 'SHY', 'weight': 100}
            ]
        elif bond_allocation < 40:
            return [
                {'type': 'Intermediate Treasury Bonds', 'ticker': 'IEF', 'weight': 60},
                {'type': 'Corporate Bonds (Investment Grade)', 'ticker': 'LQD', 'weight': 40}
            ]
        else:
            return [
                {'type': 'Intermediate Treasury Bonds', 'ticker': 'IEF', 'weight': 50},
                {'type': 'Corporate Bonds (Investment Grade)', 'ticker': 'LQD', 'weight': 30},
                {'type': 'Municipal Bonds', 'ticker': 'MUB', 'weight': 20}
            ]