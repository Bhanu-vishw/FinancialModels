"""
Implementation of Black-Scholes formulae
"""

import numpy as np
from scipy.stats import norm

N = norm(0, 1)


def d1(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes d1

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes d1
    """
    # Your implementation

    if t == 0:
        raise ValueError("Time to expiry (t) must be greater than 0.")

    a = (np.log(s / k) + (r - q + 0.5 * v**2) * t) / (v * np.sqrt(t))

    return a


def d2(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes d2

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes d2
    """
    # Your implementation

    b = d1(s, k, r, q, v, t) - v * np.sqrt(t)

    return b


def itm(s: float, k: float, is_call: bool) -> bool:
    """Moneyness indicator

    Args:
        s (float): underlying price
        k (float): strike price
        is_call (bool): True if is call option else False if put

    Returns:
        bool: True if ITM else False
    """
    # Your implementation

    if is_call:
        i = s>k
    else:
        i = s<k

    return i


def payoff(s: float, k: float, is_call: bool) -> float:
    """Payoff function

    Args:
        s (float): underlying price
        k (float): strike price
        is_call (bool): True if is call option else False if put

    Returns:
        float: the payoff
    """
    # Your implementation

    if is_call:
        poff = max(s - k, 0)
    else:
        poff = max(k - s, 0)

    return poff 


def price(
    s: float, k: float, r: float, q: float, v: float, t: float, is_call: bool
) -> float:
    """Black-Scholes price

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry
        is_call (bool): True if is call option else False if put

    Returns:
        float: Black-Scholes price
    """
    # Your implementation

    D1 = d1(s, k, r, q, v, t)
    D2 = d2(s, k, r, q, v, t)

    if is_call:
        p = s * np.exp(-q * t) * N.cdf(D1) - k * np.exp(-r * t) * N.cdf(D2)
    else:
        p = k * np.exp(-r * t) * N.cdf(-D2) - s * np.exp(-q * t) * N.cdf(-D1)

    return p


def delta(
    s: float, k: float, r: float, q: float, v: float, t: float, is_call: bool
) -> float:
    """Black-Scholes delta

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry
        is_call (bool): True if is call option else False if put

    Returns:
        float: Black-Scholes delta
    """
    # Your implementation

    D1 = d1(s, k, r, q, v, t)

    if is_call:
        d =  np.exp(-q * t) * N.cdf(D1)
    else:
        d =  -np.exp(-q * t) * N.cdf(-D1)
    
    return d


def theta(
    s: float, k: float, r: float, q: float, v: float, t: float, is_call: bool
) -> float:
    """Black-Scholes theta

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry
        is_call (bool): True if is call option else False if put

    Returns:
        float: Black-Scholes theta
    """
    # Your implementation

    D1 = d1(s, k, r, q, v, t)
    D2 = d2(s, k, r, q, v, t)

    if t == 0:
        raise ValueError("Time to expiry (t) must be greater than 0.")

    term1 = -(s * v * np.exp(-q * t) * N.pdf(D1)) / (2 * np.sqrt(t))

    # Implementing separate formulas for Call and Put
    if is_call:
        t = (term1 + q * s * np.exp(-q * t) * N.cdf(D1) - r * k * np.exp(-r * t) * N.cdf(D2))
    else:
        t =  (term1 - q * s * np.exp(-q * t) * N.cdf(-D1) + r * k * np.exp(-r * t) * N.cdf(-D2))

    return t


def call_price(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes call price

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes call price
    """
    # Your implementation

    c = price(s, k, r, q, v, t, is_call=True)

    return c 



def put_price(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes put price

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes put price
    """
    # Your implementation

    p = price(s, k, r, q, v, t, is_call=False)

    return p


def call_delta(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes call delta

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes call delta
    """
    # Your implementation

    cd = delta(s, k, r, q, v, t, is_call=True)

    return cd


def put_delta(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes put delta

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes put delta
    """
    # Your implementation

    pd = delta(s, k, r, q, v, t, is_call=False)

    return pd


def call_theta(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes call theta

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes call theta
    """
    # Your implementation

    ct = theta(s, k, r, q, v, t, is_call=True)

    return ct


def put_theta(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes put theta

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes put theta
    """
    # Your implementation

    pt = theta(s, k, r, q, v, t, is_call=False)

    return pt


def gamma(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes gamma

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes gamma
    """
    # Your implementation

    if t == 0:
        raise ValueError("Time to expiry (t) must be greater than 0.")

    D1 = d1(s, k, r, q, v, t)

    g = (np.exp(-q * t) * N.pdf(D1)) / (s * v * np.sqrt(t))

    return g


def vega(s: float, k: float, r: float, q: float, v: float, t: float) -> float:
    """Black-Scholes vega

    Args:
        s (float): underlying spot price
        k (float): strike price
        r (float): continuous risk free rate
        q (float): continuous dividend yield
        v (float): return volatility
        t (float): time to expiry

    Returns:
        float: Black-Scholes vega
    """
    # Your implementation

    D1 = d1(s, k, r, q, v, t)

    v = s * np.exp(-q * t) * N.pdf(D1) * np.sqrt(t)

    return v
