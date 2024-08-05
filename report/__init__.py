"""Code for easily-creating HTML reports w/a pre-defined figure style. """
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


MY_DIR = Path(__file__).parent


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
