import logging
from typing import Iterable, Optional, Sequence, Union

from docx import Document
from docx.shared import Inches, Pt
from docx.text.parfmt import ParagraphFormat
from pandas.core.frame import DataFrame
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.plotting import PlotMultiVariable, PlotVariable
from eda_report.univariate import Variable
from eda_report.validate import validate_target_variable

logging.basicConfig(
    format="[%(levelname)s %(asctime)s.%(msecs)03d] %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


class ReportContent:
    """Analyses data, then prepares textual summaries and graphs.

    Args:
        data (Iterable): The data to analyse.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        target_variable (Optional[Union[str, int]], optional): The column to
            use to group values. Defaults to None.
    """

    def __init__(
        self,
        data: Iterable,
        *,
        title: str = "Exploratory Data Analysis Report",
        graph_color: str = "cyan",
        target_variable: Optional[Union[str, int]] = None,
    ) -> None:
        self.variables = MultiVariable(data)
        self.GRAPH_COLOR = graph_color
        self.TARGET_VARIABLE = validate_target_variable(
            data=self.variables.data, target_variable=target_variable
        )
        self.TITLE = title
        self.intro_text = self._get_introductory_summary()
        self.multivariate_graphs = PlotMultiVariable(
            self.variables,
            graph_color=self.GRAPH_COLOR,
            hue=self.TARGET_VARIABLE,
        ).graphs
        self.variable_descriptions = self._get_variable_descriptions()
        self.bivariate_summaries = self._get_bivariate_summaries()

    def _get_introductory_summary(self) -> str:
        """Get an overview of the number of rows and the nature of columns.

        Returns:
            str: Introduction
        """
        num_rows, num_cols = self.variables.data.shape

        if num_rows == 1:
            rows = "1 row (observation)"
        else:
            rows = f"{num_rows:,} rows (observations)"

        if num_cols == 1:
            cols = "1 column (feature)"
        else:
            cols = f"{num_cols:,} columns (features)"

        # Get numeric column info
        if self.variables.numeric_cols is None:
            numeric = ""
        elif self.variables.numeric_cols.shape[1] == 1:
            numeric = ", 1 of which is numeric"
        else:
            numeric = (
                f", {self.variables.numeric_cols.shape[1]} of which are"
                " numeric"
            )

        return f"The dataset consists of {rows} and {cols}{numeric}."

    def _describe_variable(self, variable: Variable) -> dict:
        """Get summary statistics for a variable.

        Args:
            variable (Variable): The data to analyse.

        Returns:
            dict: Summary statistics
        """
        var = variable.contents
        if variable.num_unique == 1:
            unique_vals = "1 unique value"
        else:
            unique_vals = f"{variable.num_unique:,} unique values"

        return {
            "description": (
                f"{variable.name.capitalize()} is a {variable.var_type} "
                f"variable with {unique_vals}. {variable.missing} of its "
                "values are missing."
            ),
            "graphs": PlotVariable(
                variable,
                graph_color=self.GRAPH_COLOR,
                hue=self.TARGET_VARIABLE,
            ).graphs,
            "statistics": var._get_summary_statistics().to_frame(),
            "normality_tests": (
                var._test_for_normality()
                if variable.var_type == "numeric"
                else None
            ),
        }

    def _get_variable_descriptions(self) -> dict:
        """Get brief descriptions of all columns present in the data.

        Returns:
            dict: Summaries of columns present.
        """
        return {
            var.name: self._describe_variable(var)
            for var in tqdm(
                self.variables.iter_variables(),
                bar_format="{desc}: {percentage:3.0f}%|{bar:35}| "
                + "{n_fmt}/{total_fmt} features.",
                desc="Univariate analysis",
                dynamic_ncols=True,
                total=self.variables.data.shape[1],
            )
        }

    def _get_bivariate_summaries(self) -> dict:
        """Get descriptions of the nature of correlation between numeric
        column pairs.

        Returns:
            dict: Correlation info.
        """
        if hasattr(self.variables, "var_pairs"):
            return {
                var_pair: (
                    f"{var_pair[0].title()} and {var_pair[1].title()} have"
                    f" {self.variables.correlation_descriptions[var_pair]}."
                )
                for var_pair in self.variables.var_pairs
            }
        else:
            return None


class ReportDocument(ReportContent):
    """Creates a :class:`~docx.document.Document`  with analysis results.

    The :class:`ReportContent` class is used to analyse the data and
    generate text and graph content. Then the :class:`~docx.document.Document`
    class from the `python-docx`_ package is used to publish the results as a
    *Word* document.

    The report consists of 3 main sections:

    #. An *Overview* of the data and its features.
    #. *Univariate Analysis*: Summary statistics and graphs for each feature.
    #. *Bivariate Analysis*: Pairwise comparisons of numerical features.

    .. _python-docx: https://python-docx.readthedocs.io/en/latest/

    Args:
        data (Iterable): The data to analyse.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        target_variable (Optional[Union[str, int]], optional): The column to
            use to group values. Defaults to None.
        output_filename (str, optional): The file name or path to save the
            document to. Defaults to "eda-report.docx".
        table_style (str, optional): The style to apply to the tables created.
            Defaults to "Table Grid".
    """

    def __init__(
        self,
        data: Iterable,
        *,
        title: str = "Exploratory Data Analysis Report",
        graph_color: str = "cyan",
        target_variable: Optional[Union[str, int]] = None,
        output_filename: str = "eda-report.docx",
        table_style: str = "Table Grid",
    ) -> None:
        super().__init__(
            data,
            title=title,
            graph_color=graph_color,
            target_variable=target_variable,
        )
        self.OUTPUT_FILENAME = output_filename
        self.TABLE_STYLE = table_style
        self.document = Document()
        self._get_report()

    def _get_report(self) -> None:
        """Calculate summary statistics, plot graphs, and save the results as
        a .docx file.
        """
        self._create_title_page()
        self._get_univariate_analysis()

        if hasattr(self.variables, "var_pairs"):
            self._get_bivariate_analysis()

        self._to_file()
        logging.info(f"Done. Results saved as {self.OUTPUT_FILENAME!r}")

    def _create_title_page(self) -> None:
        """Add a title and a brief summary of the data."""
        self.document.add_heading(self.TITLE, level=0)

        self.document.add_paragraph(self.intro_text)

        self._get_numeric_overview_table()
        self._get_categorical_overview_table()
        self.document.add_page_break()

    def _format_heading_spacing(
        self, format: ParagraphFormat, before: int = 21, after: int = 7
    ) -> None:
        """Set the spacing above or below a heading.

        Args:
            format (ParagraphFormat): The heading's format.
            before (int, optional): Size of spacing above the heading in pt.
                Defaults to 21.
            after (int, optional): Size of spacing below the heading in pt.
                Defaults to 7.
        """
        format.space_before = Pt(before)
        format.space_after = Pt(after)

    def _get_numeric_overview_table(self) -> None:
        """Create a table with an overview of the numeric features present."""
        if self.variables.numeric_cols is not None:
            heading = self.document.add_heading(
                "Overview of Numeric Features", level=1
            )
            self._format_heading_spacing(heading.paragraph_format)
            # count | mean | std | min | 25% | 50% | 75% | max
            self._create_table(
                data=self.variables.numeric_stats,
                header=True,
                column_widths=(1.2,) + (0.7,) * 8,
                font_size=8.5,
                style="Normal Table",
            )

    def _get_categorical_overview_table(self) -> None:
        """Create a table with an overview of the categorical features
        present.
        """
        if self.variables.categorical_cols is not None:
            heading = self.document.add_heading(
                "Overview of Categorical Features", level=1
            )
            self._format_heading_spacing(heading.paragraph_format)
            # column-name | count | unique | top | freq | relative freq
            self._create_table(
                data=self.variables.categorical_stats,
                header=True,
                column_widths=(1.2,) + (0.9,) * 5,
                font_size=8.5,
                style="Normal Table",
            )

    def _get_univariate_analysis(self) -> None:
        """Get a brief introduction, summary statistics, and graphs for each
        individual variable.
        """
        univariate_heading = self.document.add_heading(
            "1. Univariate Analysis", level=1
        )
        self._format_heading_spacing(
            univariate_heading.paragraph_format, before=0, after=0
        )
        for idx, var_name in enumerate(self.variable_descriptions, start=1):
            var_info = self.variable_descriptions[var_name]

            heading = self.document.add_heading(
                f"1.{idx}. {var_name}".title(), level=2
            )
            self._format_heading_spacing(
                heading.paragraph_format, before=20, after=5
            )
            self.document.add_paragraph(var_info["description"])

            self.document.add_heading("Summary Statistics", level=4)
            self._create_table(var_info["statistics"], column_widths=[2.5, 2])

            for graph in var_info["graphs"].values():
                self.document.add_picture(graph, width=Inches(4.4))

            if (norm_tests := var_info["normality_tests"]) is not None:

                self.document.add_heading("Tests for Normality", level=4)
                # type | p-value | conclusion
                self._create_table(
                    data=norm_tests,
                    header=True,
                    column_widths=(2.2, 1, 2),
                    font_size=8.5,
                    style="Normal Table",
                )

        self.document.add_page_break()

    def _get_bivariate_analysis(self) -> None:
        """Get comparisons, scatterplots and ecdf plots for pairs of numeric
        variables.
        """
        bivariate_heading = self.document.add_heading(
            "2. Bivariate Analysis (Correlation)", level=1
        )
        self._format_heading_spacing(
            bivariate_heading.paragraph_format, before=0
        )

        self.document.add_picture(
            self.multivariate_graphs["correlation_heatmap"], width=Inches(6.7)
        )
        self.document.add_page_break()

        for idx, var_pair in enumerate(self.bivariate_summaries, start=1):
            heading = self.document.add_heading(
                f"2.{idx} {var_pair[0]} vs {var_pair[1]}".title(), level=2
            )
            self._format_heading_spacing(
                heading.paragraph_format, before=20, after=5
            )
            self.document.add_paragraph(self.bivariate_summaries[var_pair])
            self.document.add_picture(
                self.multivariate_graphs["scatterplots"][var_pair],
                width=Inches(6),
            )

            # Add a page break after every 2 pairs
            if idx % 2 == 0:
                self.document.add_page_break()

    def _create_table(
        self,
        data: DataFrame,
        column_widths: Sequence = (),
        font_face: str = "Courier New",
        font_size: float = 10,
        style: Optional[str] = None,
        header: bool = False,
    ) -> None:
        """Generates a table for the supplied ``data``.

        Args:
            data (DataFrame): The data to tabulate.
            column_widths (Sequence, optional): Column specifications.
                Defaults to ().
            font_face (str, optional): Font typeface for cell text. Defaults
                to "Courier New".
            font_size (float, optional): Font size. Defaults to 10.
            style (Optional[str], optional): A `Word` table style. Defaults to
                None.
            header (bool, optional): Whether or not to include column names.
                Defaults to False.
        """
        if header:
            # Add a row of column labels
            data_with_header = data.copy()
            data_with_header.loc["", :] = data.columns

            # Ensure that column labels are in the first row
            data = data_with_header.sort_index()

        table = self.document.add_table(
            rows=len(data),
            cols=len(column_widths),
        )
        table.style = style or self.document.styles[self.TABLE_STYLE]

        # Set column dimensions
        for idx, width in enumerate(column_widths):
            table.columns[idx].width = Inches(width)

        # Populate the rows
        for idx, row_data in enumerate(data.itertuples()):
            for cell, value in zip(table.rows[idx].cells, row_data):
                cell.text = f"{value}"

                # Font size and type-face have to be set at `run` level
                run = cell.paragraphs[0].runs[0]
                font = run.font
                font.size = Pt(font_size)
                font.name = font_face

        self.document.add_paragraph()

    def _to_file(self) -> None:
        """Save the report as a file."""
        # Set page margins
        for section in self.document.sections:
            section.left_margin = Inches(1.2)
            section.right_margin = Inches(1.2)

        self.document.save(self.OUTPUT_FILENAME)
