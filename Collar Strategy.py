import numpy as np
from statistics import NormalDist
import matplotlib.pyplot as plt

S_zero = 100 #intial stock price
K_put = 95
K_call = 110
drift = 0.05 #expected stock growth rate
r = 0.05 #risk-free interest rate
sigma = 0.2 #volatility


#A base stochastic process and GBM class I built in a Brownian Motions simulations project
class stochasticProcess:
    def step(self, steps):
        if not isinstance(steps, int):
            raise TypeError("the number of steps must be an integer")
        if steps < 0:
            raise ValueError("the number of steps must be positive")
        for i in range(steps):
            self.path.append(self.next_value())

    def plot(self, **kwargs):
        plt.plot(self.path, **kwargs)
        plt.show()


class geometricBrownianMotion(stochasticProcess):
    def __init__(self, drift, volatility, dt=0.01, initial_value=1):

        if not isinstance(drift, (float, int)):
            raise TypeError("average growth rate must be a number")
        if not isinstance(volatility, (float, int)):
            raise TypeError("volatility must be a number")
        if volatility < 0:
            raise ValueError("volatility must be non-negative")
        if initial_value <= 0:
            raise ValueError("initial value must be greater than 0")

        self.drift = drift
        self.volatility = volatility
        self.dt = dt
        self.path = [initial_value]

    def next_value(self):
        return self.path[-1] * np.exp((self.drift - 0.5*self.volatility**2)*self.dt + self.volatility*np.sqrt(self.dt)*np.random.normal())



def black_scholes(S, K, T, r, sigma, call=True):

    if T < 0 or T > 1:
        raise ValueError("The maturity must be in the interval [0,1]")
    if T == 0:
        return np.maximum(S-K if call else K-S, 0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    normal = NormalDist(0, 1)

    if call:
        call_put = S * normal.cdf(d1) - K * np.exp(-r * T) * normal.cdf(d2)
    else:
        call_put = K * np.exp(-r * T) * normal.cdf(-d2) - S * normal.cdf(-d1)

    return call_put




trading_days = 252 #252 trading days in one year
maturity = 1 #maturity in years
steps = maturity * trading_days
stock = geometricBrownianMotion(drift, sigma, 1/252, S_zero) #create a GBM object
stock.step(steps)

stock_values = np.array(stock.path)
call_values = np.zeros(steps + 1)
put_values = np.zeros(steps + 1)

time_to_maturity = np.linspace(1, 0, 252*maturity + 1) #T=1 is the intial time and T=0 is time at maturity

for t in range(steps + 1):
    call_values[t] = black_scholes(stock.path[t], K_call, time_to_maturity[t], r, sigma, call=True)
    put_values[t] = black_scholes(stock.path[t], K_put, time_to_maturity[t], r, sigma, call=False)


net_initial_premium = put_values[0] - call_values[0]
initial_collar_value = stock_values[0] + net_initial_premium
collar_values = stock_values + put_values - call_values
collar_profit = collar_values - initial_collar_value



fig, axes = plt.subplots(2, 2, figsize=(10, 7))

#stock against time to maturity
axes[0, 0].plot(time_to_maturity, stock_values)
axes[0, 0].set_title("Stock Price")
axes[0, 0].set_xlabel("Time to Maturity")
axes[0, 0].set_ylabel("Price")
axes[0, 0].grid()

#options against time to maturity
axes[0, 1].plot(time_to_maturity, call_values, color="green", label="Call")
axes[0, 1].plot(time_to_maturity, put_values, color="red", label="Put")
axes[0, 1].set_title("Option Values")
axes[0, 1].set_xlabel("Time to Maturity")
axes[0, 1].set_ylabel("Value")
axes[0, 1].legend()
axes[0, 1].grid()

#collar value against time to maturity
axes[1, 0].plot(time_to_maturity, stock_values)
axes[1, 0].plot(time_to_maturity, collar_values, color="orange")
axes[1, 0].set_title("Collar Value")
axes[1, 0].set_xlabel("Time to Maturity")
axes[1, 0].set_ylabel("Value")
axes[1, 0].legend()
axes[1, 0].grid()

#collar profit against time to maturity
axes[1, 1].plot(time_to_maturity, collar_profit)
axes[1, 1].set_title("Collar Profit")
axes[1, 1].set_xlabel("Time to Maturity")
axes[1, 1].set_ylabel("Profit")
axes[1, 1].grid()

plt.tight_layout()
plt.show()
