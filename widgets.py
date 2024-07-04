"""Standalone tkinter widgets to insert into dashboard. """
import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class DebtPayoffWidget:
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, dashboard: tk.Tk) -> None:
        self.fig, self.axes = plt.subplots(figsize=(4, 4))
        self.axes.set_title('Debt Payoff Schedule')
        self.axes.grid()
        self.canvas = FigureCanvasTkAgg(self.fig, dashboard)

        balance = 1000
        apr = 25
        payment = 100
        periods = np.log(payment) - np.log(payment - apr * balance / 1200)
        periods /= np.log(1 + apr / 1200)
        periods = np.ceil(periods).astype(int)
        running_balance = np.empty(periods + 1)
        running_balance[0] = balance
        for month in range(periods):
            running_balance[month + 1] = max(
                running_balance[month] * (1 + apr / 1200) - payment,
                0
            )
        self.axes.plot(np.arange(periods + 1), running_balance, '.-')

    def pack(self, *args, **kwargs) -> None:
        """Pack the widget in a parent widget (refer to tkinter docs). """
        self.canvas.get_tk_widget().pack(*args, **kwargs)

    def update(self) -> None:
        """Add another payoff schedule line. """
