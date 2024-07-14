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

    def set_entry(self, text: str) -> bool:
        """Set entry text.

        Args:
            text (str): what the entry box should say

        Returns:
            bool: whether text is valid and set as the entry text
        """
        if not self.is_valid(text):
            return False
        self.entry_var.set(text)
        return True

    def add_trace(self, callback: Callable) -> None:
        """Add a new observer trace to notify when entry changes.

        Args:
            callback (Callable): function that accepts an int
        """
        self._traces.append(callback)

    def run_traces(self, *_) -> None:
        """Send entry value (or repeat previous value if '') to observers. """
        val_to_send = self.value
        if val_to_send is None:
            val_to_send = self._backup_value
        else:
            self._backup_value = val_to_send
        for callback in self._traces:
            callback(val_to_send)

    @property
    def value(self) -> int:
        """int: current entry value (None if '') """
        value = self.entry_var.get()
        value = None if value == '' else int(value)
        return value


class DebtPayoffWidget(ttk.Frame):
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.linegraph = utils.LineGraph()

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
                    self.balance.set_entry(str(line.metadata['balance']))
                    self.payment.set_entry(str(line.metadata['payment']))
                    self.apr.set_entry(str(line.metadata['apr']))

        canvas.mpl_connect('pick_event', swap_selected)
        canvas.get_tk_widget().pack(padx=2, pady=2, fill=tk.X)

        # debt starting balance
        self.balance = NaturalNumberEntry(self)
        self.balance.set_text('Balance')
        self.balance.pack(padx=2, pady=2, fill=tk.X)
        # self.balance.add_trace(self.entry_change_callback)

        # monthly payment
        self.payment = NaturalNumberEntry(self)
        self.payment.set_text('Monthly Payment')
        self.payment.pack(padx=2, pady=2, fill=tk.X)
        self.payment.add_trace(self.entry_change_callback)

        # annual percentage rate (APR)
        self.apr = NaturalNumberEntry(self)
        self.apr.set_text('APR')
        self.apr.pack(padx=2, pady=2, fill=tk.X)
        # self.apr.add_trace(self.entry_change_callback)

        # add button
        self.add_button = ttk.Button(
            self,
            text='New line',
            command=self.add_candidate_line
        )
        self.add_button.pack(padx=2, pady=2, fill=tk.X)

    def add_candidate_line(self) -> None:
        """Add a new candiate line to the graph. """
        _, running_balance = utils.calc_balance_over_time(
            balance=1000,
            payment=25,
            apr=25
        )
        self.linegraph.plot(
            running_balance, '.-', picker=5,
            metadata={'balance': 1000, 'payment': 25, 'apr': 25}
        )

    def entry_change_callback(self, _) -> None:
        """Update currently-selected line. """
        try:
            meta = {
                'balance': self.balance.value,
                'payment': self.payment.value,
                'apr': self.apr.value
            }
            _, running_bal = utils.calc_balance_over_time(**meta)
            self.linegraph.update(
                range(len(running_bal)),
                running_bal,
                metadata=meta
            )
        except RuntimeError:
            pass  # intermediate entry values where interest > payment
        except TypeError:
            pass  # balance, payment, or APR have None values
