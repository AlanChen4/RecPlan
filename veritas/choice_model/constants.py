import pandas as pd
import json

from pathlib import Path


CURRENT_PATH = Path(__file__).parent.resolve() / 'data'

# SITE_DATA
# 322 x 10: each row is site name, column is attribute
"""
name    acres    trails    ...
------------------------------
jordan| 911.60   ...
twin  | ...
...
"""
SITE_DATA = pd.read_parquet(CURRENT_PATH / 'site_data.parquet')

# SITE_COEFFICIENTS 
# 1 x 10: each column is attribute with the coefficient as value
SITE_COEFFICIENTS = pd.read_parquet(CURRENT_PATH / 'site_coefficients.parquet')

# DISTANCES
# 920 x 596: distance matrix containing (sites + block groups) on row index and (block groups only) on column index
DISTANCES = pd.read_parquet(CURRENT_PATH / 'distances.parquet')

# MODEL_POPULATION
# 596 x 2
"""
        black    other
------------------------------
bg 1  | 215   ...
bg 2  | ...
...
"""
POPULATION = pd.read_parquet(CURRENT_PATH / 'model_population.parquet')

# WAKE_BG_GEOJSON
# .geojson file containing shapes of all the block groups in NC (according to 2020 census)
with open(CURRENT_PATH / 'wake_bg.json') as f:
    WAKE_BG_GEOJSON = json.load(f)

# SITE_LOCATIONS
# rows are site name, columns are respective latitude & longitude
SITE_LOCATIONS = pd.read_parquet(CURRENT_PATH / 'site_locations.parquet')

# BASELINE_VISITS
# index is site name, column is visits
BASELINE_VISITS = pd.read_parquet(CURRENT_PATH / 'baseline_visits.parquet').set_index('site_name')
