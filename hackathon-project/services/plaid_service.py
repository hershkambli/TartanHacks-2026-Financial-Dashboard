import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest


class PlaidService:
    def __init__(self, client_id, secret):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,  # Use Sandbox for testing
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def create_link_token(self, user_id):
        """Create a link token for Plaid Link"""
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name="FinDash Budget Tracker",
                products=[Products("investments")],
                country_codes=[CountryCode("US")],
                language='en'
            )
            response = self.client.link_token_create(request)
            return response['link_token']
        except Exception as e:
            print(f"Error creating link token: {e}")
            return None

    def exchange_public_token(self, public_token):
        """Exchange public token for access token"""
        try:
            exchange_response = self.client.item_public_token_exchange({'public_token': public_token})
            return exchange_response['access_token']
        except Exception as e:
            print(f"Error exchanging token: {e}")
            return None

    def get_holdings(self, access_token):
        """Get investment holdings"""
        try:
            request = InvestmentsHoldingsGetRequest(access_token=access_token)
            response = self.client.investments_holdings_get(request)

            holdings = []
            for holding in response['holdings']:
                security = next((s for s in response['securities'] if s['security_id'] == holding['security_id']), None)

                holdings.append({
                    'name': security['name'] if security else 'Unknown',
                    'ticker': security['ticker_symbol'] if security else 'N/A',
                    'quantity': holding['quantity'],
                    'institution_price': holding['institution_price'],
                    'value': holding['institution_value']
                })

            return holdings
        except Exception as e:
            print(f"Error getting holdings: {e}")
            return []