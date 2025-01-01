"""
Implementation of the Longstaff-Schwartz LSM model
"""

from dataclasses import dataclass
from typing import Any

import numpy as np

from final.random import Paths, PathGenerator


# NOTE: you may decide to populate this information within your lsm_price
# function to help you debug, but you don't have to use it if you don't want to

@dataclass
class LSMTimeStepData:
    """Storage class for LSM debug data"""

    j: int
    """Time index"""
    t_j: float
    """Time t_j"""
    po_plus: float
    """Immediate positive payoffs"""
    b_hat: list[float]
    """Regression coefficients beta hat"""
    x: np.ndarray[float]
    """Stock price paths that are ITM at t_j"""
    y: np.ndarray[float]
    """Discounted continuation values"""
    y_hat: np.ndarray[float]
    """Fitted discounted continuation values"""


def lsm_price(
    strike_price: float,
    risk_free_rate: float,
    is_call: float,
    path_generator: PathGenerator,
    polynomial_degree: int = 2,
    debug: bool = False,
) -> float | tuple[float, list[LSMTimeStepData]]:
    """The Longstaff-Schwartz Least Squares Monte Carlo American option price

    Args:
        strike_price (float): strike price
        risk_free_rate (float): risk free spot rate corresponding to t
        is_call (float): True if is call option else False if put
        path_generator (PathGenerator): an object to generate price paths
        polynomial_degree (int, optional): polynomial degree used for
        regression. Defaults to 2, as is in the reference paper.
        debug (bool, optional): if True will return additional output with debug
        info. Defaults to False.

    Returns:
        float | tuple[float, list[LSMTimeStepData]]: the option price and optionally some debug output
    """

    # Your implementation

    paths = path_generator.generate()
    
    num_steps = paths.shape[1] - 1

    time_step = paths.time_step
    
    # Initializing the cashflow matrix
    cashflows = np.zeros_like(paths[:])
    
    # Terminal payoffs
    if is_call:
        cashflows[:, -1] = np.maximum(paths[:, -1] - strike_price, 0)
    else:
        cashflows[:, -1] = np.maximum(strike_price - paths[:, -1], 0)
    
    debug_data = []
    
    # Backward induction through all exercise dates except the first one
    for j in range(num_steps - 1, 0, -1):

        # Current time
        t_j = j * time_step
        
        # Calculate immediate exercise value
        if is_call:
            exercise_value = np.maximum(paths[:, j] - strike_price, 0)
        else:
            exercise_value = np.maximum(strike_price - paths[:, j], 0)
        
        # Find in-the-money paths
        itm_indices = np.where(exercise_value > 0)[0]
        
        if len(itm_indices) > 0:
            # Get price paths and continuation values for ITM paths
            x = paths[itm_indices, j]
            
            # Future cashflows
            future_cf = cashflows[itm_indices, j+1:]
            discount_factors = np.exp(-risk_free_rate * np.arange(1, num_steps-j+1) * time_step)
            y = np.sum(future_cf * discount_factors, axis=1)
            
            # Setup basis functions (polynomial terms)
            x_mat = np.column_stack([x**i for i in range(polynomial_degree + 1)])
            
            # Regression
            b_hat = np.linalg.lstsq(x_mat, y, rcond=None)[0]
            continuation_value = x_mat @ b_hat
            
            # Exercise decision
            exercise = exercise_value[itm_indices] > continuation_value
            
            # Update cashflows matrix
            cashflows[itm_indices, j] = np.where(exercise, exercise_value[itm_indices],0)
            
            # Zero out future cashflows where we exercise now
            cashflows[itm_indices[exercise], j+1:] = 0
            
            if debug:
                debug_data.append(LSMTimeStepData(j=j, t_j=t_j, po_plus=exercise_value[itm_indices], b_hat=b_hat.tolist(), x=x, y=y, y_hat=continuation_value))
    
    # Price is the average of discounted cashflows
    discount_factors = np.exp(-risk_free_rate * np.arange(num_steps + 1) * time_step)
    option_price = np.mean(np.sum(cashflows * discount_factors, axis=1))
    
    if debug:
        return option_price, debug_data
    return option_price
