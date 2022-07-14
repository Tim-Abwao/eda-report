import sys
from pathlib import Path

from eda_report.cli import run_from_cli
from eda_report.gui import EDAGUI


class TestCLIArgumentParsing:
    def test_with_all_args(self, temp_data_dir, monkeypatch):
        # Simulate supplying all args
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "eda-report",
                "-i",
                f"{temp_data_dir / 'data.csv'}",
                "-o",
                f"{temp_data_dir}/cli-test-1.docx",
                "-t",
                "CLI Test",
                "-c",
                "teal",
                "-T",
                "A",
            ],
        )
        report = run_from_cli()
        assert report.OUTPUT_FILENAME == f"{temp_data_dir}/cli-test-1.docx"
        assert report.TITLE == "CLI Test"
        assert report.GRAPH_COLOR == "teal"
        assert report.TARGET_VARIABLE.name == "A"

    def test_with_only_input_file(self, temp_data_dir, monkeypatch):
        # Supply the input file it has no default.
        monkeypatch.setattr(
            sys, "argv", ["eda-report", "-i", f"{temp_data_dir / 'data.xlsx'}"]
        )
        report = run_from_cli()

        # Check if the default arguments were set
        assert report.OUTPUT_FILENAME == "eda-report.docx"
        assert report.TITLE == "Exploratory Data Analysis Report"
        assert report.GRAPH_COLOR == "cyan"
        assert report.TARGET_VARIABLE is None

        Path("eda-report.docx").unlink()  # Remove resultant report

    def test_without_optional_args(self, monkeypatch, capsys):
        # Simulate launching the GUI
        def mock_gui_init(gui):
            """Simulate GUI initialization."""
            pass

        def mock_gui_mainloop(gui):
            """Simulate running GUI."""
            print("Graphical user interface running in Tk mainloop.")

        monkeypatch.setattr(EDAGUI, "__init__", mock_gui_init)
        monkeypatch.setattr(EDAGUI, "mainloop", mock_gui_mainloop)

        # Simulate running with no args
        monkeypatch.setattr(sys, "argv", ["eda-report"])
        run_from_cli()

        captured = capsys.readouterr()
        assert (
            "Graphical user interface running in Tk mainloop." in captured.out
        )
