import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
from scipy.optimize import minimize

__all__ = ['gaussian_ll', 'ewma_var_estimates', 'ewma_objective', 'ewma_fit']

def gaussian_ll(returns: np.ndarray, vars: np.ndarray) -> float:
    """Conditional Gaussian log-likelihood function using NumPy.

    Args:
        returns (np.ndarray): Array of returns.
        vars (np.ndarray): Array of corresponding variances.

    Returns:
        float: Log-likelihood result.
    """
    if len(returns) != len(vars):
        raise ValueError("The lengths of returns and variances must match.")

    if np.any(vars <= 0):
        raise ValueError("All variances must be positive.")

    log_likelihood = -0.5 * np.sum(np.log(2 * np.pi * vars) + (returns ** 2) / vars)
    return log_likelihood

def ewma_var_estimates(lmb: float, returns: pd.Series) -> pd.Series:
    """
    Estimate variances using EWMA with time series support.
    
    Args:
        lmb (float): Lambda parameter (smoothing factor).
        returns (pd.Series): Historical return series with a datetime index.
        
    Returns:
        pd.Series: EWMA variance estimates with the same index as the returns.
    """
    if len(returns) < 1:
        raise ValueError("Returns series must have at least one element.")

    vars = np.zeros_like(returns, dtype=float)
    vars[0] = np.var(returns)

    for i in range(1, len(returns)):
        vars[i] = (1 - lmb) * float(returns.iloc[i - 1] ** 2) + lmb * float(vars[i - 1])

    return pd.Series(vars, index=returns.index)

def ewma_objective(lmb: float, returns: np.ndarray) -> float:
    """EWMA objective function to minimize using NumPy.

    Args:
        lmb (float): Lambda parameter.
        returns (np.ndarray): Input return series.

    Returns:
        float: Objective function result.
    """
    if lmb <= 0 or lmb >= 1:
        return np.inf
    else:
        vars = ewma_var_estimates(lmb, pd.Series(returns))
        return -gaussian_ll(returns, vars.values)

def ewma_fit(returns: pd.Series, guess: float = 0.9) -> float:
    """Fit an EWMA volatility model to a historical return series using NumPy.

    Args:
        returns (pd.Series): Historical returns with a datetime index.
        guess (float, optional): Initial guess for lambda parameter. Defaults to 0.9.

    Returns:
        float: The fitted lambda parameter.
    """
    result = minimize(
        ewma_objective,
        x0=guess,
        args=(returns.values,),
        method="Nelder-Mead",
        tol=1e-15,
    )
    return result.x[0]