"""Code for easily-creating HTML reports w/a pre-defined figure style. """
import base64
import io
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt


MY_DIR = Path(__file__).parent


def fig_to_base64(fig: plt.Figure) -> str:
    """Convert a figure to a Base64-encoded JPEG.

    Args:
        fig (plt.Figure): figure to convert

    Returns:
        str: HTML-embeddable Base64 JPEG
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format='jpeg')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


class Report:
    """Utility class to build HTML reports. """
    def __init__(self) -> None:
        environment = Environment(loader=FileSystemLoader(MY_DIR))
        self._template = environment.get_template('template.html')
        self._images: List[str] = []

    def add_figure(self, fig: plt.Figure) -> None:
        """Convert and add a new figure to the report.

        Args:
            fig (plt.Figure): figure to add
        """
        self._images.append(fig_to_base64(fig))

    def write(self, report_path: str = './report.html') -> None:
        """Compile report and write to disk.

        Args:
            report_path (str): where to write report
        """
        report = self._template.render(images=self._images)
        with open(report_path, mode='w', encoding='utf-8') as report_file:
            report_file.write(report)
