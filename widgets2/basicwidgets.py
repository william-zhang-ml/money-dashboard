"""Basic widgets that the more application-specific widgets can use. """
from functools import partial
from tkinter import filedialog, ttk
from matplotlib import pyplot as plt


class StringToNumberEntry(ttk.Frame):
    """String key to natural number value entry. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # entry box and backend entry data variable
        self.key_var = tk.StringVar()
        tk.Entry(
            self,
            textvariable=self.key_var,
        ).pack(padx=2, pady=2, side=tk.LEFT)

        # entry box and backend entry data variable
        self.value_var = tk.StringVar()
        tk.Entry(
            self,
            textvariable=self.value_var,
            validate='key',
            validatecommand=(
                self.register(self.is_valid),
                '%P'
            )
        ).pack(padx=2, pady=2, side=tk.LEFT)

        # setup mechanism to update observers/subscribers
        self.disabled = False
        self.key_var.trace_add('write', self.run_traces)
        self.value_var.trace_add('write', self.run_traces)
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

    def set_value(self, text: str) -> bool:
        """Set value text.

        Args:
            text (str): what the value box should say

        Returns:
            bool: whether text is valid and set as the value text
        """
        if not self.is_valid(text):
            return False
        self.value_var.set(text)
        return True

    def add_trace(self, callback: Callable) -> None:
        """Add a new observer trace to notify when entry changes.

        Args:
            callback (Callable): function that accepts a Dict[str, int]
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
            callback({self.key: val_to_send})

    def enable_traces(self) -> None:
        """Turn on pub-sub traces. """
        self.disabled = False

    def disable_traces(self) -> None:
        """Turn off pub-sub traces. """
        self.disabled = True

    @property
    def key(self) -> str:
        """str: current key-entry value """
        return self.key_var.get()

    @property
    def value(self) -> int:
        """int: current value-entry value (None if '') """
        value = self.value_var.get()
        value = None if value == '' else int(value)
        return value


class SaveFigureButton(ttk.Button):
    """Button specifically for downloading embedded Matplotlib figures. """
    def __init__(self, *args, **kwargs) -> None:
        if 'command' in kwargs:
            del kwargs['command']
        super().__init__(*args, **kwargs)

    def link_fig(self, fig: plt.Figure) -> None:
        """Set button callback to download provided figure.

        Args:
            fig (plt.Figure): figure to track
        """
        self.config(command=partial(self.save_figure, fig=fig))

    @staticmethod
    def save_figure(fig: plt.Figure) -> None:
        """Save a figure to disk.

        Args:
            fig (plt.Figure): figure to save
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension='.jpg',
            filetypes=[('JPEG files', '*.jpg;*.jpeg'), ('PNG files', '*.png')],
            initialfile='debtpayoff'
        )  # ask the user where to save the file
        if filepath:
            fig.savefig(filepath)  # Save the plot to the file
