"""Widget for showing how APR and payment amount impact payoff time. """
import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.backend_bases import PickEvent
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DebtWidget(tk.Frame):
    """Widget for showing how APR and payment amount impact payoff time. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # graph
        fig, axes = plt.subplots()
        axes.set_title('Debt Payoff Schedule')
        axes.grid()
        self.linegraph.axes.set_xlabel('months')
        self.linegraph.axes.set_ylabel('balance')
        self._canvas = FigureCanvasTkAgg(fig, self)
        self._canvas.mpl_connect('pick_event', self.select)
        canvas_widget = self._canvas.get_tk_widget()
        canvas_widget.grid(row=0, columnspan=3, padx=2, pady=2)
        canvas_widget.bind('<BackSpace>', lambda _: self.delete_selected())

    def select(self, event: PickEvent) -> None:
        """Highlight selected artist on graph and enable live updates.

        Args:
            event (PickEvent): click event and selected artist data
        """
        pass

    def delete_selected(self) -> None:
        """Delete the selected artist. """
        if self._selected is None:
            return
        del self._categories[self._selected.idx]
        del self._amounts[self._selected.idx]
        self._selected = None
        self._enter_add_mode()
        self.plot()
