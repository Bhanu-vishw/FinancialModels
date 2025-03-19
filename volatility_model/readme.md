# Volatility Models Calibration

This repository contains the implementation of various volatility models, including EWMA and GARCH(1,1), to estimate and analyze financial market variances. The assignment walks through creating key components such as log-likelihood functions, variance estimators, and optimization routines for parameter calibration.

---

## **Overview**

### **Key Features**
- **Daily Log Returns Function**: Helper function to calculate and fetch daily log returns using Yahoo! Finance data.
- **Volatility Models**: Implementation of EWMA and GARCH(1,1) models.
- **Parameter Calibration**: Optimize model parameters using `scipy.optimize.minimize` for maximum conditional log-likelihood.
- **Model Diagnostics**: Plot residual correlograms and create visualizations of objective functions and parameter insights.

---
