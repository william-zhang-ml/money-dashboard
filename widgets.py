"""Standalone tkinter widgets to insert into dashboard. """
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable, Dict, List
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
        self.disabled = False
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
        if self.disabled:
            return
        val_to_send = self.value
        if val_to_send is None:
            val_to_send = self._backup_value
        else:
            self._backup_value = val_to_send
        for callback in self._traces:
            callback(val_to_send)

    def enable_traces(self) -> None:
        """Turn on pub-sub traces. """
        self.disabled = False

    def disable_traces(self) -> None:
        """Turn off pub-sub traces. """
        self.disabled = True

    @property
    def value(self) -> int:
        """int: current entry value (None if '') """
        value = self.entry_var.get()
        value = None if value == '' else int(value)
        return value


class NaturalNumberEntries(ttk.Frame):
    """Multiple NaturalNumberEntry instances in one widget. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._entries: Dict[str, NaturalNumberEntry] = {}

    def add_entry(self, label: str, entry: str = None):
        """Add a new labelled-entry widget to this one.

        Args:
            label (str): label text
            entry (str): initial entry value
        """
        self._entries[label] = NaturalNumberEntry(self)
        self._entries[label].set_text(label)
        if entry is not None:
            self._entries[label].set_entry(entry)
        self._entries[label].pack(expand=True, fill=tk.BOTH, padx=2, pady=2)

    def get(self) -> Dict[str, int]:
        """Get current entry values.

        Returns:
            Dict[str, int]: map from entry label to entry value
        """
        return {label: entry.value for label, entry in self._entries.items()}

    def load(self, data: Dict[str, str]) -> None:
        """Load entry text into entry widgets.

        Args:
            data (Dict[str, str]): map from entry label to new entry text
        """
        for label, value in data.items():
            self._entries[label].set_entry(str(value))

    def clear(self) -> None:
        """Clear entry text in every entry widget. """
        for entry in self._entries.values():
            entry.entry.delete(0, tk.END)

    def enable(self) -> None:
        """Enable user input. """
        for entry in self._entries.values():
            entry.entry.config(state='normal')

    def disable(self) -> None:
        """Disable user input. """
        for entry in self._entries.values():
            entry.entry.config(state='disabled')

    def add_trace(self, callback: Callable) -> None:
        """Add a new observer trace to notify when entry changes.

        Args:
            callback (Callable): function that accepts an int
        """
        for entry in self._entries.values():
            entry.add_trace(callback)

    def enable_traces(self) -> None:
        """Turn on pub-sub traces. """
        for entry in self._entries.values():
            entry.enable_traces()

    def disable_traces(self) -> None:
        """Turn off pub-sub traces. """
        for entry in self._entries.values():
            entry.disable_traces()


class DebtPayoffWidget(tk.Frame):
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.linegraph = utils.LineGraph()
        self.selected = None  # index of selected line

        # graph annotations
        self.linegraph.axes.set_title('Debt Payoff Schedule')
        self.linegraph.axes.grid()
        self.linegraph.axes.set_xlabel('months')
        self.linegraph.axes.set_ylabel('balance')

        # register a callback to swap selected line
        canvas = FigureCanvasTkAgg(self.linegraph.fig, self)

        def swap_selected(event) -> None:
            # identify which line user clicked on
            for i_line, line in self.linegraph:
                if event.artist == line:
                    break

            # pylint: disable=undefined-loop-variable
            self.entries.disable_traces()
            self.entries.clear()
            self.entries.disable()
            if self.selected is None:
                # select line
                self.linegraph.select(i_line)
                self.entries.enable()
                self.entries.load({
                    'Balance': str(line.metadata['balance']),
                    'Monthly Payment': str(line.metadata['payment']),
                    'APR': str(line.metadata['apr'])
                })
                self.entries.enable_traces()
                self.selected = i_line
            elif self.selected == i_line:
                # unselect previously-selected line
                self.linegraph.unselect(self.selected)
                self.selected = None
            else:
                # unselect previously-selected line
                self.linegraph.unselect(self.selected)

                # select line
                self.linegraph.select(i_line)
                self.entries.enable()
                self.entries.load({
                    'Balance': str(line.metadata['balance']),
                    'Monthly Payment': str(line.metadata['payment']),
                    'APR': str(line.metadata['apr'])
                })
                self.entries.enable_traces()
                self.selected = i_line
            # pylint: enable=undefined-loop-variable

        canvas.mpl_connect('pick_event', swap_selected)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)

        # user inputs
        self.entries = NaturalNumberEntries(self)
        self.entries.add_entry('Balance')          # debt starting balance
        self.entries.add_entry('Monthly Payment')  # monthly payment
        self.entries.add_entry('APR')              # annual % rate (APR)
        self.entries.disable()                     # b/c obv no lines to edit
        self.entries.add_trace(self.entry_change_callback)
        self.entries.pack(padx=2, pady=2, fill=tk.X)

        # add button
        self.add_button = ttk.Button(
            self,
            text='New line',
            command=self.add_line
        )
        self.add_button.pack(padx=2, pady=2, fill=tk.X)

        # delete button
        self.del_button = ttk.Button(
            self,
            text='Delete',
            command=self.delete_line
        )
        self.del_button.pack(padx=2, pady=2, fill=tk.X)

        # save button
        self.save_button = ttk.Button(
            self,
            text='Download image',
            command=self.download_image
        )
        self.save_button.pack(padx=2, pady=2, fill=tk.X)

        # hotkeys (assume master == root)
        self.master.bind('<Control-s>', lambda _: self.download_image())
        canvas_widget.bind('<BackSpace>', lambda _: self.delete_line())

    def add_line(self) -> None:
        """Add a new line to the graph. """
        _, running_balance = utils.calc_time_until_cleared(
            balance=1000,
            payment=25,
            apr=25
        )
        self.linegraph.plot(
            running_balance, '-', picker=5,
            metadata={'balance': 1000, 'payment': 25, 'apr': 25}
        )

    def delete_line(self) -> None:
        """Delete the selected line. """
        if self.selected is None:
            return
        self.linegraph.remove(self.selected)
        self.selected = None
        self.entries.clear()
        self.entries.disable()

    def download_image(self) -> None:
        """Save the current figure to disk. """
        filepath = filedialog.asksaveasfilename(
            defaultextension='.jpg',
            filetypes=[('JPEG files', '*.jpg;*.jpeg'), ('PNG files', '*.png')],
            initialfile='debtpayoff'
        )  # ask the user where to save the file
        if filepath:
            self.linegraph.fig.savefig(filepath)  # Save the plot to the file

    def entry_change_callback(self, _) -> None:
        """Update currently-selected line. """
        meta = self.entries.get()
        meta = {
            'balance': meta['Balance'],
            'payment': meta['Monthly Payment'],
            'apr': meta['APR']
        }

        try:
            _, running_bal = utils.calc_time_until_cleared(**meta)
        except RuntimeError:
            pass  # intermediate entry values where interest > payment
        except TypeError:
            pass  # balance, payment, or APR have None values
        else:
            self.linegraph.update(
                self.selected,
                range(len(running_bal)),
                running_bal,
                metadata=meta
            )


class FireWidget(tk.Frame):
    """Widget that shows time until a portfolio generates a goal income. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.linegraph = utils.LineGraph()
        self.selected = None  # index of selected line

        # graph annotations
        self.linegraph.axes.set_title('How Long Until Money Printer Go Brr')
        self.linegraph.axes.grid()
        self.linegraph.axes.set_xlabel('year')
        self.linegraph.axes.set_ylabel('balance')

        # register a callback to swap selected line
        canvas = FigureCanvasTkAgg(self.linegraph.fig, self)

        def swap_selected(event) -> None:
            # identify which line user clicked on
            for i_line, line in self.linegraph:
                if event.artist == line:
                    break

            # pylint: disable=undefined-loop-variable
            self.entries.disable_traces()
            self.entries.clear()
            self.entries.disable()
            if self.selected is None:
                # select line
                self.linegraph.select(i_line)
                self.entries.enable()
                self.entries.load({
                    'Target Income': str(line.metadata['income']),
                    'Starting Portfolio Value': str(line.metadata['balance']),
                    'Monthly Deposit': str(line.metadata['deposit']),
                    'Growth Rate': str(line.metadata['rate']),
                    'Safe Rate': str(line.metadata['safe_rate'])
                })
                self.entries.enable_traces()
                self.selected = i_line
            elif self.selected == i_line:
                # unselect previously-selected line
                self.linegraph.unselect(self.selected)
                self.selected = None
            else:
                # unselect previously-selected line
                self.linegraph.unselect(self.selected)

                # select line
                self.linegraph.select(i_line)
                self.entries.enable()
                self.entries.load({
                    'Target Income': str(line.metadata['income']),
                    'Starting Portfolio Value': str(line.metadata['balance']),
                    'Monthly Deposit': str(line.metadata['deposit']),
                    'Growth Rate': str(line.metadata['rate']),
                    'Safe Rate': str(line.metadata['safe_rate'])
                })
                self.entries.enable_traces()
                self.selected = i_line
            # pylint: enable=undefined-loop-variable

        canvas.mpl_connect('pick_event', swap_selected)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)

        # user inputs
        self.entries = NaturalNumberEntries(self)
        self.entries.add_entry('Target Income')
        self.entries.add_entry('Starting Portfolio Value')
        self.entries.add_entry('Monthly Deposit')
        self.entries.add_entry('Growth Rate')
        self.entries.add_entry('Safe Rate')
        self.entries.disable()  # b/c obv no lines to edit
        self.entries.add_trace(self.entry_change_callback)
        self.entries.pack(padx=2, pady=2, fill=tk.X)

        # add button
        self.add_button = ttk.Button(
            self,
            text='New line',
            command=self.add_line
        )
        self.add_button.pack(padx=2, pady=2, fill=tk.X)

        # delete button
        self.del_button = ttk.Button(
            self,
            text='Delete',
            command=self.delete_line
        )
        self.del_button.pack(padx=2, pady=2, fill=tk.X)

        # save button
        self.save_button = ttk.Button(
            self,
            text='Download image',
            command=self.download_image
        )
        self.save_button.pack(padx=2, pady=2, fill=tk.X)

        # hotkeys (assume master == root)
        self.master.bind('<Control-s>', lambda _: self.download_image())
        canvas_widget.bind('<BackSpace>', lambda _: self.delete_line())

    def add_line(self) -> None:
        """Add a new line to the graph. """
        _, running_balance = utils.calc_time_until_fire(
            income=3000,
            balance=1000,
            deposit=100,
            rate=7,
            safe_rate=5
        )
        self.linegraph.plot(
            running_balance, '-', picker=5,
            metadata={
                'income': 3000,
                'balance': 1000,
                'deposit': 100,
                'rate': 7,
                'safe_rate': 5
            }
        )

    def delete_line(self) -> None:
        """Delete the selected line. """
        if self.selected is None:
            return
        self.linegraph.remove(self.selected)
        self.selected = None
        self.entries.clear()
        self.entries.disable()

    def download_image(self) -> None:
        """Save the current figure to disk. """
        filepath = filedialog.asksaveasfilename(
            defaultextension='.jpg',
            filetypes=[('JPEG files', '*.jpg;*.jpeg'), ('PNG files', '*.png')],
            initialfile='debtpayoff'
        )  # ask the user where to save the file
        if filepath:
            self.linegraph.fig.savefig(filepath)  # Save the plot to the file

    def entry_change_callback(self, _) -> None:
        """Update currently-selected line. """
        meta = self.entries.get()
        meta = {
            'income': meta['Target Income'],
            'balance': meta['Starting Portfolio Value'],
            'deposit': meta['Monthly Deposit'],
            'rate': meta['Growth Rate'],
            'safe_rate': meta['Safe Rate']
        }

        try:
            _, running_bal = utils.calc_time_until_fire(**meta)
        except RuntimeError:
            pass  # intermediate entry values where interest > payment
        except TypeError:
            pass  # balance, payment, or APR have None values
        else:
            self.linegraph.update(
                self.selected,
                range(len(running_bal)),
                running_bal,
                metadata=meta
            )
