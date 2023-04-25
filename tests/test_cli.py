import sys
from pathlib import Path

from eda_report._cli import run_from_cli
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
                "-g",
                "A",
            ],
        )
        run_from_cli()
        expected_output = temp_data_dir / "cli-test-1.docx"
        assert expected_output.is_file()

    def test_with_only_input_file(self, temp_data_dir, monkeypatch):
        # Supply the input file it has no default.
        monkeypatch.setattr(
            sys, "argv", ["eda-report", "-i", f"{temp_data_dir / 'data.xlsx'}"]
        )
        run_from_cli()
        expected_output = Path("eda-report.docx")
        assert expected_output.is_file()

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
