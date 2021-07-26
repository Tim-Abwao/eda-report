from pandas import DataFrame
from eda_report.cli import process_cli_args
import sys


class TestCLIArgumentParsing:
    def test_with_all_args(self, tmp_path):

        cli_test_dir = tmp_path / "cli-tests"
        cli_test_dir.mkdir()
        csv_file = cli_test_dir / "data.csv"
        csv_file.write_text("1, 2, 3\n")

        args = process_cli_args(
            f"{csv_file}",
            "-o",
            "cli-test-1.docx",
            "-t",
            "CLI Test",
            "-c",
            "teal",
            "-T",
            "0",
        )
        # Check whether the supplied arguments were set
        assert isinstance(args.infile, DataFrame)
        assert args.outfile == "cli-test-1.docx"
        assert args.title == "CLI Test"
        assert args.color == "teal"
        assert args.target == "0"

    def test_with_default_args(self, tmp_path):

        cli_test_dir = tmp_path / "cli-tests"
        cli_test_dir.mkdir()
        excel_file = cli_test_dir / "data.xlsx"
        DataFrame([1, 2, 3]).to_excel(
            excel_file, index=False, engine="openpyxl"
        )

        args = process_cli_args(f"{excel_file}")

        # Check if the default arguments were set
        assert isinstance(args.infile, DataFrame)
        assert args.outfile == "eda-report.docx"
        assert args.title == "Exploratory Data Analysis Report"
        assert args.color == "cyan"
        assert args.target is None

    def test_with_args_from_stdin(self, tmp_path, monkeypatch):

        cli_test_dir = tmp_path / "cli-tests"
        cli_test_dir.mkdir()
        csv_file = cli_test_dir / "data.csv"
        csv_file.write_text("1, 2, 3\n")

        monkeypatch.setattr(sys, "argv", ["eda_cli", f"{csv_file}"])

        args = process_cli_args()

        assert args.outfile == "eda-report.docx"
        assert args.title == "Exploratory Data Analysis Report"
        assert args.color == "cyan"
        assert args.target is None
