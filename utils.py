"""Widget support code, mostly backend data structures and math. """
from matplotlib import pyplot as plt


class LineGraph:
    """Multi-line graph with CRUD operations. """
    def __init__(self, max_lines: int = 5):
        self.max_lines = max_lines
        self.fig, self.axes = plt.subplots()
        self.lines = []            # lines on graph
        self.selected: int = None  # index of selected line

    def plot(self, *args, **kwargs) -> bool:
        """Plot a new line.

        Args:
            (see matplotlib.axes.Axes.plot)

        Returns:
            bool: whether a new line was plotted
        """
        if len(self.lines) == self.max_lines:
            return False
        self.lines.append(self.axes.plot(*args, **kwargs)[0])
        self.select(self.num_lines - 1)
        return True

    def remove(self) -> bool:
        """Remove the active line.

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

        return True

    @property
    def num_lines(self) -> int:
        """int: the number of lines on the graph """
        return len(self.lines)
