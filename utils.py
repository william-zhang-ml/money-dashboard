"""Widget support code, mostly backend data structures and math. """
from copy import deepcopy
from typing import Iterable, List, Tuple, Union
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt


Numeric = Union[int, float]


class LineGraph:
    """Multi-line graph with CRUD operations. """
    def __init__(self, max_lines: int = 5):
        self.max_lines = max_lines
        self.fig, self.axes = plt.subplots()
        self.lines = []            # lines on graph
        self.selected: int = None  # index of selected line

    def __iter__(self) -> Iterable[Tuple[int, Line2D]]:
        """Loop over graph lines.

        Returns:
            Iterable[Tuple[int, Line2D]]: index of line, line
        """
        for i_line, line in enumerate(self.lines):
            yield i_line, line

    def plot(self, *args, metadata: dict = None, **kwargs) -> bool:
        """Plot a new line.

        Args:
            (see matplotlib.axes.Axes.plot)

        Returns:
            bool: whether a new line was plotted
        """
        if len(self.lines) == self.max_lines:
            return False
        self.lines.append(self.axes.plot(*args, **kwargs)[0])
        if metadata is not None:
            self.lines[-1].metadata = deepcopy(metadata)
        self.select(self.num_lines - 1)
        return True

    def update(
        self,
        xdata: Iterable[Numeric],
        ydata: Iterable[Numeric],
        metadata: dict
    ) -> bool:
        """Update the currently-selected line.

        Args:
            xdata (Iterable[Numeric]): new line x data
            ydata (Iterable[Numeric]): new line y data

        Returns:
            bool: whether currently-selected line was updated
        """
        if self.num_lines == 0:
            return False
        self.lines[self.selected].set_data(xdata, ydata)
        self.lines[self.selected].metadata = deepcopy(metadata)
        self.axes.relim()
        self.axes.autoscale()
        self.fig.canvas.draw()
        return True

    def remove(self) -> bool:
        """Remove the currently-selected line.

        Returns:
            bool: whether a line was removed
        """
        if self.num_lines == 0:
            return False
        self.lines.pop(self.selected).remove()
        self.selected = None
        if self.num_lines > 0:
            self.select(self.num_lines - 1)
        return True

    def select(self, which: int) -> bool:
        """Change which line is selected in the graph.

        Args:
            which (int): index of line to select

        Returns:
            bool: whether the index was selected
        """
        if not 0 <= which < self.num_lines:
            return False

        # deactivate current
        if self.selected is not None:
            self.lines[self.selected].set_marker('')
            self.lines[self.selected].set_linestyle('-')

        # activate selection
        self.selected = which
        self.lines[self.selected].set_marker('.')
        self.lines[self.selected].set_linestyle('--')

        self.fig.canvas.draw()
        return True

    @property
    def num_lines(self) -> int:
        """int: the number of lines on the graph """
        return len(self.lines)


def calc_balance_over_time(
    balance: float = 1000,
    payment: float = 25,
    apr: float = 25
) -> Tuple[int, List[float]]:
    """Calculate how long it takes to payoff a balance.

    Args:
        balance (float): initial balance amount
        payment (float): monthly payment amount
        apr (float): annual percentage rate

    Returns:
        int, np.ndarray: months until paid off, running balance over months
    """
    interest = apr * balance / 1200
    if payment <= interest:
        raise RuntimeError('interest exceeds payment')
    running_balance = []
    while balance > 0:
        running_balance.append(balance)
        balance = balance + interest - payment
        interest = apr * balance / 1200
    running_balance.append(0)
    return len(running_balance) - 1, running_balance
