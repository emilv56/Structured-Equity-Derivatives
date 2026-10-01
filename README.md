# Structured-Equity-Derivatives

In this project I have developed and analysed a protective collar strategy on an equity position in Python. The stock simulation in this project is modelled by a Geometric Brownian Motion, reused from my Stochastic Processes simulations project (see my Stochastic Process Path Simulations repository). The call and put premiums are valued by a Black Scholes model with the following parameters:

* S - the stock price at the given time. I have set the initial stock price valued at 100.
* K - the put / call strike. The put strike has been set to 95 and the call strike 110; I have assumed they remain constant in this project throughout the time period until maturity.
* T - the time remaining until maturity. I have set the maturity to be 1 year containing 252 trading days.
* sigma - the annualised volatility of the stock's returns, which I have assumed to be constant in this project and set to 20%.
* call/put - a design idea I included to reuse the code containing the Black Scholes formula and value error checking.

Running the code will generate 4 plots and an interactive slider controlling the number of trading days until maturity (out of 252 trading days in the maturity of one year). The following information is shown on the figure:

1. The stock price and 
