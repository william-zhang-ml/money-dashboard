"""Basic widgets that the more application-specific widgets can use. """
from functools import partial
from tkinter import filedialog, ttk
from matplotlib import pyplot as plt


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
