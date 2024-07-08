"""Standalone tkinter widgets to insert into dashboard. """
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils


class DebtPayoffWidget(ttk.Frame):
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.linegraph = utils.LineGraph()

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

        # scenario 3
        _, running_balance = utils.calc_balance_over_time(
            balance=1000,
            payment=50,
            apr=20
        )
        self.linegraph.plot(running_balance, '.-', picker=5)

        # graph annotations
        self.linegraph.axes.set_title('Debt Payoff Schedule')
        self.linegraph.axes.grid()
        self.linegraph.axes.set_xlabel('months')
        self.linegraph.axes.set_ylabel('balance')

        # register a callback to swap selected line
        canvas = FigureCanvasTkAgg(self.linegraph.fig, self)

        def swap_selected(event) -> None:
            for i_line, line in self.linegraph:
                if event.artist == line:
                    self.linegraph.select(i_line)
                    canvas.draw()

        canvas.mpl_connect('pick_event', swap_selected)
        canvas.get_tk_widget().pack(padx=2, pady=2)
