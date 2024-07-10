"""Standalone tkinter widgets to insert into dashboard. """
import tkinter as tk
from tkinter import ttk
from typing import Callable, List
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils


class NaturalNumberEntry(ttk.Frame):
    """Label + Entry widget for entering natural numbers. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # label prompt for entry
        self.prompt = ttk.Label(self)
        self.prompt.pack(padx=2, pady=2, side=tk.LEFT)

        # entry box and backend entry data variable
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(
            self,
            textvariable=self.entry_var,
            validate='key',
            validatecommand=(
                self.register(self.is_valid),
                '%P'
            )
        )
        self.entry.pack(padx=2, pady=2, side=tk.LEFT)

        # setup mechanism to update observers/subscribers
        self.entry_var.trace_add('write', self.run_traces)
        self._traces: List[Callable] = []
        self._backup_value = 0

    @staticmethod
    def is_valid(proposed: str) -> bool:
        """Check whether text is a natural number (no leading zero).
           Empty string is also okay.

        Args:
            proposed (str): text to check

        Returns:
            bool: whether text is a natural number (no leading zero)
        """
        if proposed == '':
            return True
        return proposed[0] != '0' and proposed.isdigit()

    def set_text(self, text: str) -> None:
        """Set label text.

        Args:
            text (str): what the label should say
        """
        self.prompt.config(text=text)

    def add_trace(self, callback: Callable) -> None:
        """Add a new observer trace to notify when entry changes.

        Args:
            callback (Callable): function that accepts an int
        """
        self._traces.append(callback)

    def run_traces(self, *_) -> None:
        """Send entry value (or repeat previous value if '') to observers. """
        val_to_send = self.entry_var.get()
        if val_to_send == '':
            val_to_send = self._backup_value
        else:
            val_to_send = int(val_to_send)
            self._backup_value = val_to_send
        for callback in self._traces:
            callback(val_to_send)


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
