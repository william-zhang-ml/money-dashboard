"""Code for easily-creating HTML reports w/a pre-defined figure style. """
import base64
import io
from pathlib import Path
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

    def write(self, report_path: str = './report.html') -> None:
        """Compile report and write to disk. """
        report = self._template.render(some_text='Hello world!')
        with open(report_path, mode='w', encoding='utf-8') as report_file:
            report_file.write(report)
