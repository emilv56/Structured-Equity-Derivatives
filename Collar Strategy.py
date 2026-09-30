import numpy as np
from statistics import NormalDist
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

S_zero = 100 #intial stock price
K_put = 95
K_call = 110
drift = 0.05 #expected stock growth rate
r = 0.05 #risk-free interest rate
sigma = 0.2 #volatility

trading_days = 252 #252 trading days in one year
maturity = 1 #maturity in years
steps = int(maturity * trading_days)


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





stock = geometricBrownianMotion(drift, sigma, 1/252, S_zero) #create a GBM object
stock.step(steps)

stock_values = np.array(stock.path)
call_values = np.zeros(steps + 1)
put_values = np.zeros(steps + 1)

time_to_maturity = np.linspace(1, 0, 252*maturity + 1) #T=0 is the intial time and T=1 is time at maturity
elapsed_time = time_to_maturity[::-1]

for t in range(steps + 1):
    call_values[t] = black_scholes(stock.path[t], K_call, time_to_maturity[t], r, sigma, call=True)
    put_values[t] = black_scholes(stock.path[t], K_put, time_to_maturity[t], r, sigma, call=False)


initial_collar_value = stock_values[0] + put_values[0] - call_values[0]
collar_values = stock_values + put_values - call_values
collar_profit = collar_values - initial_collar_value


#maturity payoff
stock_range = np.linspace(50, 150, 200)
maturity_profit = stock_range + np.maximum(K_put - stock_range, 0) - np.maximum(stock_range - K_call, 0) - initial_collar_value


#build a figure to show the four plots
fig = plt.figure(figsize=(12, 9))
gridspec = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.2)
axes_stock = fig.add_subplot(gridspec[0, 0])
axes_options = fig.add_subplot(gridspec[0, 1])
axes_maturity = fig.add_subplot(gridspec[1, 0])
axes_profit = fig.add_subplot(gridspec[1, 1])


#stock and collar value against time to maturity
stock_line, = axes_stock.plot([], [], label="Stock")
collar_line, = axes_stock.plot([], [], label="Collar")

axes_stock.set_xlim(0, maturity)
axes_stock.set_ylim(min(np.concatenate([stock_values, collar_values])), max(np.concatenate([stock_values, collar_values])))
axes_stock.set_title("Collar Value")
axes_stock.set_xlabel("Time to Maturity")
axes_stock.set_ylabel("Value")
axes_stock.legend()
axes_stock.grid()

#options against time to maturity
call_line, = axes_options.plot([], [], label="Call")
put_line, = axes_options.plot([], [], label="Put")

axes_options.set_xlim(0, maturity)
axes_options.set_ylim(min(np.concatenate([put_values, call_values])), max(np.concatenate([put_values, call_values])))
axes_options.set_title("Option Values")
axes_options.set_xlabel("Time to Maturity")
axes_options.set_ylabel("Value")
axes_options.legend()
axes_options.grid()

#collar payout diagram at maturity
current_stock_line = axes_maturity.axvline(stock_values[0], linewidth=2)

axes_maturity.plot(stock_range, maturity_profit, label="Collar Profit at Maturity")
axes_maturity.axhline(0, linestyle="--", linewidth="0.7")
axes_maturity.axvline(K_put, linestyle="--", linewidth="0.7")
axes_maturity.axvline(K_call, linestyle="--", linewidth="0.7")
axes_maturity.set_xlabel("Terminal Stock Price")
axes_maturity.set_ylabel("Profit")
axes_maturity.grid()


#collar profit against time to maturity
profit_line, = axes_profit.plot([], [], label="Collar Profit")

axes_profit.set_xlim(0, maturity)
axes_profit.set_ylim(min(collar_profit), max(collar_profit))
axes_profit.set_title("Collar Profit")
axes_profit.set_xlabel("Time to Maturity")
axes_profit.set_ylabel("Profit")
axes_profit.grid()


#slider
axes_slider = fig.add_axes([0.25, 0.94, 0.5, 0.03])
time_slider = Slider(axes_slider, "Time to Maturity in Trading Days", 0, int(maturity*trading_days), valinit=0, valstep=1)


def update_time_slider(value):

    end = int(value) + 1

    current_time = elapsed_time[:end]
    current_stock = stock_values[:end]
    current_call = call_values[:end]
    current_put = put_values[:end]
    current_collar = collar_values[:end]
    current_profit = collar_profit[:end]

    stock_line.set_data(current_time, current_stock)
    collar_line.set_data(current_time, current_collar)
    call_line.set_data(current_time, current_call)
    put_line.set_data(current_time, current_put)
    profit_line.set_data(current_time, current_profit)
    current_stock_line.set_xdata([current_stock[-1], current_stock[-1]])

    fig.canvas.draw_idle()

time_slider.on_changed(update_time_slider)

update_time_slider(0)

plt.show()
