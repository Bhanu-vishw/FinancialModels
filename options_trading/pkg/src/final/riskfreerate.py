import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def risk_free_rate(data, maturity_in_years):

    # Converting column headers to tenors in fraction years
    tenors = { "1 Mo": 1 / 12, "2 Mo": 2 / 12, "3 Mo": 3 / 12, "4 Mo": 4 / 12, "6 Mo": 6 / 12, "1 Yr": 1, "2 Yr": 2, "3 Yr": 3, "5 Yr": 5, "7 Yr": 7, "10 Yr": 10, "20 Yr": 20, "30 Yr": 30}

    # Extracting the latest treasury data
    latest_rates = data.iloc[-1]
    
    # Preparing tenor and rate data for interpolation
    tenors_years = []
    rates = []

    for col, years in tenors.items():
        if col in latest_rates and not pd.isnull(latest_rates[col]):
            tenors_years.append(years)
            rates.append(latest_rates[col])

    # linear interpolation
    interpolation_func = interp1d(tenors_years, rates, kind='linear', fill_value='extrapolate')
    return float(interpolation_func(maturity_in_years))