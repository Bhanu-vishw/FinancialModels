import pytest
import numpy as np
import pandas as pd
from final import riskfreerate as rf

def test():
    # Sample Treasury data for testing
    test_data = pd.DataFrame({
        "Date": ["12/29/2023"],
        "1 Mo": [5.60], "2 Mo": [5.59], "3 Mo": [5.40], "4 Mo": [5.41], 
        "6 Mo": [5.26], "1 Yr": [4.79], "2 Yr": [4.23], "3 Yr": [4.01],
        "5 Yr": [3.84], "7 Yr": [3.88], "10 Yr": [3.88], "20 Yr": [4.20], "30 Yr": [4.03]
    })
    assert abs(rf.risk_free_rate(test_data, 1 / 12) - 5.60) < 1e-6
    assert abs(rf.risk_free_rate(test_data, 1) - 4.79) < 1e-6
    assert abs(rf.risk_free_rate(test_data, 10) - 3.88) < 1e-6