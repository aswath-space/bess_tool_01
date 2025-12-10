
import os
import pandas as pd
from datetime import datetime, timedelta
from entsoe import EntsoePandasClient
from geopy.geocoders import Nominatim
from app.utils.zone_mapping import get_entsoe_zone

# Ensure cache directory exists
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

class EntsoeService:
    def __init__(self):
        api_key = os.getenv('ENTSOE_API_KEY')
        if not api_key:
            # Fallback or error handling if key is missing
            print("WARNING: ENTSOE_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = EntsoePandasClient(api_key=api_key)
        
        self.geolocator = Nominatim(user_agent="pv_bess_investor_guide_tool")

    def get_zone_from_lat_lon(self, lat: float, lon: float) -> str:
        """
        Reverse geocodes the coordinates to find the country and maps it to an ENTSO-E zone.
        """
        try:
            location = self.geolocator.reverse((lat, lon), language='en')
            if location and 'address' in location.raw:
                country_code = location.raw['address'].get('country_code')
                if country_code:
                    return get_entsoe_zone(country_code)
            return None
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def fetch_day_ahead_prices(self, zone: str, start_date: pd.Timestamp, end_date: pd.Timestamp):
        """
        Fetches Day-Ahead Market prices for the given zone and date range.
        Checks local cache first.
        """
        cache_file = os.path.join(CACHE_DIR, f"dam_prices_{zone}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv")
        
        if os.path.exists(cache_file):
            print(f"Loading data from cache: {cache_file}")
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            # Ensure the index is timezone-aware if needed, or just return as is
            return df

        if not self.client:
            raise ValueError("ENTSO-E API Client not initialized. Check API Key.")

        print(f"Fetching data from ENTSO-E for {zone}...")
        try:
            # query_day_ahead_prices returns a Pandas Series
            prices_series = self.client.query_day_ahead_prices(country_code=zone, start=start_date, end=end_date)
            
            # Convert to DataFrame for consistent handling and saving
            df = prices_series.to_frame(name='price')
            
            # Save to cache
            df.to_csv(cache_file)
            return df
        except Exception as e:
            print(f"Error fetching data from ENTSO-E: {e}")
            raise e

entsoe_service = EntsoeService()
