# Options Pricing and Analysis: Final Project

## Overview

This project is designed to implement and analyze various financial modeling techniques related to options pricing and risk management. It includes the Black-Scholes model, Monte Carlo simulations, and the Longstaff-Schwartz methodology. The project also covers delta and gamma hedging strategies and explores volatility arbitrage using real-world financial data. By completing this project, you will gain hands-on experience with theoretical concepts and their practical applications.

---

- **`pkg/src/blackscholes.py`**: Implement the Black-Scholes model formulas.
- **`pkg/src/random.py`**: Implement random number generation logic.
- **`pkg/src/longstaffschwartz.py`**: Implement the Longstaff-Schwartz algorithm for American options.

### Resources

- John Hull’s *Options, Futures, and Other Derivatives*.
- Week 12 content for guidance on `random.py` and `longstaffschwartz.py`.

### Testing

Run the unit tests provided with the starter code to verify your implementations:
```bash
pytest -v


Project instructions
Part 0: Set up
First, download the starter code from the links and downloads page.

For this project you should create a new conda environment (you can call it final) that uses Python 3.11.

$ conda create -n final python=3.11 -y
Next, activate the environment

$ conda activate final
and install the starter code in development mode (-e flag) so updates are automatically picked up without you needing to reinstall.

(final) $ pip install -e ./pkg
If done correctly you should get some output when running

(final) $ pip show final
Part 1: Implementation
In this part of the project you’ll fill in missing implementations in the following files:

pkg/src/blackscholes.py

pkg/src/random.py

pkg/src/longstaffschwartz.py

If you don’t have a resource for the Black-Scholes formulas, you can find them in John Hull’s Options Futures and Other derivatives (you can some edition of this for free online).

Review the week 12 content to fill in the implementation details for random.py and longstaffschwartz.py.

You can utilize the unit tests provided with the starter code to test your implementations.

$ pytest -v
Part 2: Profit calculation and analysis
In this part of the exercise, you’ll get your hands dirty verifying some of the theoretical results from week 14. Add a notebook file to the analysis subfolder to store your results.

(a) Delta hedging efficiency
Assume we’re in the Black Scholes world and their assumptions hold. Using a put option with parameters:

: 100

: 105

: 0.04

: 0.085

: 0

: 0.3

: 2

(i): Plot

Simulate the hedging P&L of a delta hedged short put option position, using 2,000 scenarios under the following rebalance frequencies.

monthly

bi-monthly

weekly

bi-weekly

daily

2x day

4x day

8x day

Display your results graphically by plotting the mean and standard deviation of the P&L as a function of the rebalancing frequency, clearly labeling your graph.

(ii): Answer the following:

Explain what you’re seeing in the graph

What position do you need to take in the underlying to delta hedge a put option you’ve sold

Under which scenarios, in general, would the P&L have a positive expected profit vs. a negative expected profit?

(b) Gamma hedging
Now assume you can also trade a call option on the same underlying with the following parameters

: 100

: 115

: 0.04

: 0.085

: 0

: 0.3

: 2

(i): Plot

Reproduce the (a)(i) above, now incorporating this new option in your portfolio.

(ii): Answer the following:

What position do you need to take in the call option to hedge your portfolio’s gamma?

What effect does the gamma hedge have on the overall variance of the hedged portfolio P&L? Why do you think that is?

Part 3: Volatility arbitrage analysis
In this part of the project you’ll use some real options data to try to figure out if there’s a potential to make money from mispriced options.

The data you’ll use for the analysis is in the data subfolder:

options.csv: closing call and put option price data from 2023

stock.csv: historical stock prices

treasury.csv: historical Treasury par rates

The subparts will guide you through the steps.

(a) Estimate dividend yield for AAPL
Use stock price data from 2022 to estimate the continuous dividend yield. You’re free to research a coherent way for doing this. Report the number you get along with your methodology for doing so. You’ll use this as an input for your option pricing calculations.

Note

AAPL pays relatively predictable dividends. There are extensions to these models to incorporate discrete dividends with specific dates, which would be more realistic here, but we haven’t discussed so we’ll just use a continuous dividend yield.

(b) Risk free rate function and testing
Create a function that, provided one of the interest rate curves in the treasury.csv file, can compute the risk free rate to plug into the Black-Scholes formula. The risk free rate can simply be the rate corresponding to the remaining time to maturity. You can calculate this by performing linear or spline interpolation between the tenors.

Put your function for doing this within the Python package source folder and add a unit test to the unit test suite.

Note

In practice, rates used as the risk free rate in Option pricing calculations (Treasury rates or SOFR Swap rates) are generally provided as par yields. These rates would then need to be bootstrapped to get a spot rate. We didn’t talk about that this semester, but you’ll learn about this in your fixed income class.

(c) Calculate implied and realized volatilities
In this step you’ll compute implied and realized volatility, generating a new options.csv file titled options_with_vols.csv.

(i): Implied vols

In the options.csv file, you have quoted option prices for corresponding strikes and time to expiries. You also have underlying prices and risk free rates in stock.csv and treasury.csv, and your estimated dividend yield from above. Use your lsm_price implementation to back into what the volatility parameter must have been to produce the quoted price. This value is called the implied volatility of the option. You can call these columns call_iv and put_iv.

Before you do this on all of the options, perform a rough analysis to determine a reasonable number of scenarios to use. Comment on why you chose the number you did, saving this analysis in the analysis subfolder.

Note

If you struggled getting your lsm_price function to work, you may use the Black-Scholes model for this part for some point reduction.

You may decide to implement a variance reduction technique. If you do I’ll provide 5pts of extra credit if you:

also illustrate the effect of the variance reduction technique in your analysis folder

avoid breaking any of the interfaces

(ii): Realized vols

Using a volatility model of your choice, also add a column to the new file for realized volatility.

(d) Investigate volatility arbitrage
Consider the four cases

realized vol > implied vol for call options

realized vol > implied vol for put options

realized vol < implied vol for call options

realized vol < implied vol for put options

and propose trading strategies you could take for each one to capture potential mispricing.

Next, using the options_with_vols.csv file test the strategies above by entering into portfolios to exploit potential mispricing starting with 1/1/2023. Keep progressing forward through each date in the file trading your portfolios to expiry while keeping track of P&L associated with each option. As options expire and new options get introduced during 2023, enter into new portfolios. Once you get to the end of 2023, close out all your positions.

Note

In this analysis, since we want to be able to drill into P&L under each option your hedging should be done at the individual option level. That is, pretend all these portfolios are independent of each other.

Investigate your results

In this part you’ll dig into your results and try to make sense of them. Are your trading strategies viable? This is open ended but here are some questions to get you thinking:

Overall did you make money or lose money?

What proportion of strategies made money vs. lost money?

Did 1, 2, 3, or 4 above tend to perform the best?

Did the initial moneyness of the position seem to impact your results?

Were your results what you expected them to be?

Is there anything significant you think we might be missing in this model that is impacting the results?
