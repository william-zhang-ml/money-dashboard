"""Standalone tkinter widgets to insert into dashboard. """
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils


class DebtPayoffWidget:
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, dashboard: tk.Tk) -> None:
        self.linegraph = utils.LineGraph()
        self.canvas = FigureCanvasTkAgg(self.linegraph.fig, dashboard)

        # scenario 1
        _, running_balance = utils.calc_balance_over_time(
            balance=1000,
            payment=50,
            apr=25
        )
        self.linegraph.plot(running_balance, '.-', picker=5)

        # scenario 2
        _, running_balance = utils.calc_balance_over_time(
            balance=1000,
            payment=100,
            apr=25
        )
        self.linegraph.plot(running_balance, '.-', picker=5)

        self.linegraph.axes.set_title('Debt Payoff Schedule')
        self.linegraph.axes.grid()
        self.linegraph.axes.set_xlabel('months')
        self.linegraph.axes.set_ylabel('balance')

        # register a callback to swap selected line
        def swap_selected(event) -> None:
            for i_line, line in self.linegraph:
                if event.artist == line:
                    self.linegraph.select(i_line)
                    self.canvas.draw()
        self.canvas.mpl_connect('pick_event', swap_selected)

    def pack(self, *args, **kwargs) -> None:
        """Pack the widget in a parent widget (refer to tkinter docs). """
        self.canvas.get_tk_widget().pack(*args, **kwargs)

    def update(self) -> None:
        """Add another payoff schedule line. """
