"""Widget for adjusting and visualizing a budget. """
import tkinter as tk
from tkinter import ttk
from typing import List
from matplotlib import pyplot as plt
from matplotlib.backend_bases import PickEvent
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from basicwidgets import StringToNumberEntry


COLORS = ['#f99', '#6cf', '#ff9', '#9f9', '#fc9',  '#ccf']


class BudgetWidget(tk.Frame):
    """Widget for adjusting and visualizing a budget. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # user input - add category form
        self._category_inp = StringToNumberEntry(self)
        self._category_inp.grid(row=1, column=0, padx=2, pady=2, sticky='e')
        self._add_button = ttk.Button(self, text='Add', command=self.create)
        self._add_button.grid(row=1, column=1, padx=2, pady=2)

        # user input - toggle color button
        (
            ttk.Button(self, text='Toggle Colors', command=self.toggle_colors)
            .grid(row=1, column=2, padx=2, pady=2, sticky='w')
        )

        # backend vars
        self._categories = []
        self._amounts = []
        self._wedges = []
        self._selected = None  # whether in add or update/delete state
        self._grayscale = False

        # graph
        fig, _ = plt.subplots()
        self._canvas = FigureCanvasTkAgg(fig, self)
        self._canvas.mpl_connect('pick_event', self.select)
        canvas_widget = self._canvas.get_tk_widget()
        canvas_widget.grid(row=0, columnspan=3, padx=2, pady=2)
        canvas_widget.bind('<BackSpace>', lambda _: self.delete_selected())

    def create(self) -> None:
        """Add a new budget category. """
        if self._category_inp.key is None:
            return
        if self._category_inp.value is None:
            return
        self._categories.append(self._category_inp.key)
        self._amounts.append(self._category_inp.value)
        self.plot()

    def plot(self) -> None:
        """Draw/redraw data. """
        self._canvas.figure.axes[0].cla()
        if len(self._categories) == 0:
            return
        self._wedges, *_ = self._canvas.figure.axes[0].pie(
            self._amounts,
            autopct='%.1f%%',
            colors=self.get_wedge_colors(),
            counterclock=False,
            labels=self._categories,
            labeldistance=1.1,
            pctdistance=0.85,
            startangle=180,
            wedgeprops={
                'edgecolor': 'white',
                'linewidth': 2,
                'width': 0.3
            },
        )
        for idx, wedge in enumerate(self._wedges):
            wedge.idx = idx
            wedge.set_picker(True)
            wedge.set_zorder(0)
        self._canvas.draw()

    def select(self, event: PickEvent) -> None:
        """Highlight selected artist on graph and enable live updates.

        Args:
            event (PickEvent): click event and selected artist data
        """
        if self._selected is None:
            event.artist.set_edgecolor('black')
            event.artist.set_zorder(1)
            self._selected = event.artist
            self._enter_update_mode()
        elif self._selected is event.artist:
            self._selected.set_edgecolor('white')
            self._selected.set_zorder(0)
            self._selected = None
            self._enter_add_mode()
        else:
            self._selected.set_edgecolor('white')
            self._selected.set_zorder(0)
            event.artist.set_edgecolor('black')
            event.artist.set_zorder(1)
            self._selected = event.artist
        self._canvas.draw()

    def update_selected(self) -> None:
        """Update the selected artist. """
        pass

    def delete_selected(self) -> None:
        """Delete the selected artist. """
        if self._selected is None:
            return
        del self._categories[self._selected.idx]
        del self._amounts[self._selected.idx]
        self._selected = None
        self.plot()

    def get_wedge_colors(self) -> List[str]:
        """Determine wedge colors for current budget categories.

        Returns:
            List[str]: wedge colors
        """
        if self._grayscale:
            wedge_colors = ['#777'] * len(self._categories)
        else:
            wedge_colors = [
                COLORS[idx % len(COLORS)]
                for idx in range(len(self._categories))
            ]
        return wedge_colors

    def toggle_colors(self) -> None:
        """Redraw donut after toggling color versus no color setting. """
        self._grayscale = not self._grayscale
        wedge_colors = self.get_wedge_colors()
        for wedge, color in zip(self._wedges, wedge_colors):
            wedge.set_facecolor(color)
        self._canvas.draw()

    def _enter_add_mode(self) -> None:
        assert self._selected is None
        self._add_button.config(state=tk.NORMAL)

    def _enter_update_mode(self) -> None:
        assert self._selected is not None
        self._add_button.config(state=tk.DISABLED)
