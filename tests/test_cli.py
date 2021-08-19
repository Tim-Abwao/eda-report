from eda_report.gui import EDAGUI
from pandas import DataFrame
from eda_report.cli import run_from_cli
import sys
import pytest


@pytest.fixture(scope="session")
def temp_data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("data")


class TestCLIArgumentParsing:
    def test_with_all_args(self, temp_data_dir, monkeypatch):

        csv_file = temp_data_dir / "data.csv"
        csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n")

        # Simulate supplying all args
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "eda-report",
                "-i",
                f"{csv_file}",
                "-o",
                f"{temp_data_dir}/cli-test-1.docx",
                "-t",
                "CLI Test",
                "-c",
                "teal",
                "-T",
                "a",
            ],
        )

        report = run_from_cli()

        # Check whether the supplied arguments were set
        assert isinstance(report.variables.data, DataFrame)
        assert report.OUTPUT_FILENAME == f"{temp_data_dir}/cli-test-1.docx"
        assert report.TITLE == "CLI Test"
        assert report.GRAPH_COLOR == "teal"
        assert report.TARGET_VARIABLE.name == "a"

    def test_with_default_args(self, temp_data_dir, monkeypatch):

        excel_file = temp_data_dir / "data.xlsx"
        DataFrame([1, 2, 3]).to_excel(
            excel_file, index=False, engine="openpyxl"
        )

        # Supply the input file it has no default.
        monkeypatch.setattr(sys, "argv", ["eda-report", "-i", f"{excel_file}"])
        report = run_from_cli()

        # Check if the default arguments were set
        assert isinstance(report.variables.data, DataFrame)
        assert report.OUTPUT_FILENAME == "eda-report.docx"
        assert report.TITLE == "Exploratory Data Analysis Report"
        assert report.GRAPH_COLOR == "cyan"
        assert report.TARGET_VARIABLE is None

    def test_without_optional_args(self, tmp_path, monkeypatch, capsys):

        cli_test_dir = tmp_path / "cli-tests"
        cli_test_dir.mkdir()
        csv_file = cli_test_dir / "data.csv"
        csv_file.write_text("1, 2, 3\n")

        def test_gui(gui):
            # Ensure that gui is an instance of eda_report.gui.EDAGUI
            assert isinstance(gui, EDAGUI)
            print("Graphical user interface running in Tk mainloop.")

        monkeypatch.setattr(EDAGUI, "mainloop", test_gui)

        monkeypatch.setattr(sys, "argv", ["eda-report"])

        run_from_cli()

        captured = capsys.readouterr()
        assert (
            "Graphical user interface running in Tk mainloop." in captured.out
        )
