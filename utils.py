"""Widget support code, mostly backend data structures and math. """
from copy import deepcopy
from typing import Dict, Iterable, List, Tuple, Union
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt


Numeric = Union[int, float]


class LineGraph:
    """Multi-line graph with CRUD operations. """
    def __init__(self, max_lines: int = 5):
        self.max_lines = max_lines
        self.fig, self.axes = plt.subplots()
        self.lines = []  # lines on graph

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
            metadata (dict): user-defined metadata
            (also see matplotlib.axes.Axes.plot)

        Returns:
            bool: whether a new line was plotted
        """
        if len(self.lines) == self.max_lines:
            return False
        self.lines.append(self.axes.plot(*args, **kwargs)[0])
        self.unselect(self.num_lines - 1)  # force styling
        if metadata is not None:
            self.lines[-1].metadata = deepcopy(metadata)
        self.fig.canvas.draw()
        return True

    def update(
        self,
        which: int,
        xdata: Iterable[Numeric],
        ydata: Iterable[Numeric],
        metadata: dict
    ) -> bool:
        """Update a line in the graph.

        Args:
            which (int): index of line to update
            xdata (Iterable[Numeric]): new line x data
            ydata (Iterable[Numeric]): new line y data
            metadata (dict): user-defined metadata

        Returns:
            bool: whether a line was updated
        """
        if not 0 <= which < self.num_lines:
            return False
        self.lines[which].set_data(xdata, ydata)
        self.lines[which].metadata = deepcopy(metadata)
        self.axes.relim()
        self.axes.autoscale()
        self.fig.canvas.draw()
        return True

    def remove(self, which: int) -> bool:
        """Remove a line in the graph

        Args:
            which (int): index of line to remove

        Returns:
            bool: whether a line was removed
        """
        if not 0 <= which < self.num_lines:
            return False
        self.lines.pop(which).remove()
        self.fig.canvas.draw()
        return True

    def select(self, which: int) -> bool:
        """Visually select a line in the graph.

        Args:
            which (int): index of line to select

        Returns:
            bool: whether a line was selected
        """
        if not 0 <= which < self.num_lines:
            return False
        self.lines[which].set_marker('.')
        self.lines[which].set_linestyle('--')
        self.lines[which].set_color('r')
        self.fig.canvas.draw()
        return True

    def unselect(self, which: int) -> bool:
        """Visually unselect a line in the graph.

        Args:
            which (int): index of line to unselect

        Returns:
            bool: whether a line was unselected
        """
        if not 0 <= which < self.num_lines:
            return False
        self.lines[which].set_marker('')
        self.lines[which].set_linestyle('-')
        self.lines[which].set_color('k')
        self.fig.canvas.draw()
        return True

    @property
    def num_lines(self) -> int:
        """int: the number of lines on the graph """
        return len(self.lines)


class DonutGraph:
    """Donut graph w/utility functions. """
    def __init__(self):
        self.fig, self.axes = plt.subplots(figsize=(6, 6))

    def plot(
        self,
        data: Dict[str, float],
        colors: Dict[str, str] = None
    ) -> None:
        """Plot a donut chart (pie chart but cooler).

        Args:
            data (Dict[str, float]): data to plot ... label -> size
            colors (Dict[str, str]): wedge color map ... label -> color
        """
        self.axes.cla()
        plot_donut(data, self.axes, colors)
        self.fig.canvas.draw()


def plot_donut(
    data: Dict[str, float],
    axes: plt.Axes = None,
    colors: Dict[str, str] = None
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot a donut chart (pie chart but cooler).

    Args:
        data (Dict[str, float]): data to plot ... label -> size
        colors (Dict[str, str]): wedge color map ... label -> color

    Returns:
        Tuple[plt.Figure, plt.Axes]: plot handles
    """
    if colors is None:
        colors = ['#f99', '#6cf', '#ff9', '#9f9', '#fc9',  '#ccf']
        wedge_colors = [colors[idx % len(colors)] for idx in range(len(data))]
    else:
        wedge_colors = map(lambda k: colors[k], data)

    fig = None
    if axes is None:
        fig, axes = plt.subplots()
    axes.pie(
        data.values(),
        autopct='%.1f%%',
        colors=wedge_colors,
        counterclock=False,
        labels=data.keys(),
        labeldistance=1.1,
        pctdistance=0.85,
        startangle=180,
        wedgeprops={
            'edgecolor': 'white',
            'linewidth': 4,
            'width': 0.3
        }
    )
    return fig, axes


def calc_time_until_cleared(
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
        int, np.ndarray: months until paid off, running monthly balance
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


def calc_time_until_fire(
    income: float = 3000,
    balance: float = 1000,
    deposit: float = 100,
    rate: float = 7,
    safe_rate: float = None
) -> Tuple[int, List[float]]:
    """Calculate how long it takes to build a passive income stream.

    Args:
        income (float): desired amount of monthly passive income
        balance (float): initial portfolio balance
        deposit (float): monthly investment deposit into portfolio
        rate (float): annual portfolio yield in growth phase
        safe_rate (float): annual portfolio yield in maintain phase

    Returns:
        int, np.ndarray: years until FIRE, running annual balance
    """
    safe_rate = rate if safe_rate is None else safe_rate
    target = 1200 * income / safe_rate
    if target <= balance:
        raise RuntimeError('already at FIRE')
    running_balance = []
    while balance < target:
        running_balance.append(balance)
        gain = rate * balance / 100
        balance = balance + gain + 12 * deposit
    running_balance.append(balance)
    return len(running_balance) - 1, running_balance
