"""Standalone tkinter widgets to insert into dashboard. """
import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils


class DebtPayoffWidget:
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, dashboard: tk.Tk) -> None:
        self.fig, self.axes = plt.subplots(figsize=(4, 4))
        self.axes.set_title('Debt Payoff Schedule')
        self.axes.grid()
        self.canvas = FigureCanvasTkAgg(self.fig, dashboard)

        _, running_balance = utils.calc_balance_over_time()
        self.axes.plot(running_balance, '.-')

    def pack(self, *args, **kwargs) -> None:
        """Pack the widget in a parent widget (refer to tkinter docs). """
        self.canvas.get_tk_widget().pack(*args, **kwargs)

    def update(self) -> None:
        """Add another payoff schedule line. """
