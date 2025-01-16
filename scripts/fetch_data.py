from json import dump
from pathlib import Path

import pandas as pd
from requests import get

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": 38.5816,
	"longitude": -121.4944,
	"start_date": "1940-01-01",
	# "start_date": "2024-12-28",
	"end_date": "2024-12-31",
	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean"],
	"temperature_unit": "fahrenheit",
	"timezone": "America/Los_Angeles"
}

here = Path(__file__).parent
data_dir = here / '..' / 'data'
data_dir.mkdir(exist_ok=True)

resp = get(url, params=params)
data = resp.json()

# dump json data to disk
with open(data_dir / 'weather.json', 'w') as f:
    dump(data, f)

df = pd.DataFrame({
    'min_temp': data['daily']['temperature_2m_min'],
    'max_temp': data['daily']['temperature_2m_max'],
    'avg_temp': data['daily']['temperature_2m_mean'],
    'date': pd.to_datetime(resp.json()['daily']['time'], format='%Y-%m-%d')
})


# dump into .csv
df.to_csv(data_dir / 'weather.csv', index=False)

# dump into .parquet
df.to_parquet(data_dir / 'weather.parquet', index=False)

