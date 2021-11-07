import logging
from typing import Iterable, Optional, Sequence, Union

from docx import Document
from docx.shared import Inches, Pt
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
    """This defines objects that analyse data and store results as textual
    summaries and graphs.

    Parameters
    ----------
    data : Iterable
        The data to analyse.
    target_variable : Optional[Union[str, int]]
        The column to use to group values and color-code graphs.
    title : str, optional
        The title to assign the report, by default "Exploratory Data Analysis
        Report"
    graph_color : str, optional
        The color to apply to the graphs, by default "cyan"
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
        """Get a brief overview of the number of rows and the nature of
        columns.

        Returns
        -------
        str
            An overview of the input data.
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

    def _describe_variable(self, name: str) -> dict:

        # Perform univariate analysis using the Variable class
        var = Variable(self.variables.data[name])

        if var.num_unique == 1:
            unique_vals = "1 unique value"
        else:
            unique_vals = f"{var.num_unique:,} unique values"

        return {
            "description": (
                f"{name.capitalize()} is a {var.var_type} variable with"
                f" {unique_vals}. {var.missing} of its values are missing."
            ),
            "graphs": PlotVariable(
                variable=var,
                graph_color=self.GRAPH_COLOR,
                hue=self.TARGET_VARIABLE,
            ).graphs,
            "statistics": var.statistics,
            "most_common_items": (
                var.most_common_items
                if hasattr(var, "most_common_items")
                else None
            ),
        }

    def _get_variable_descriptions(self) -> dict:
        """Get brief descriptions of all columns present in the data.

        Returns
        -------
        dict[str, str]
            Summaries of columns present.
        """
        return {
            col: self._describe_variable(col)
            for col in tqdm(
                self.variables.data.columns,
                bar_format="{desc}: {percentage:3.0f}%|{bar:35}| "
                + "{n_fmt}/{total_fmt} features.",
                desc="Univariate analysis",
                dynamic_ncols=True,
            )
        }

    def _get_bivariate_summaries(self) -> dict:
        """Get descriptions of the nature of correlation between numeric
        column pairs.

        Returns
        -------
        dict[str, str]
            Correlation info.
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
    """This defines objects that produce *Word* documents with analysis
    results.

    The :class:`ReportContent` class is used to analyse the data and
    generate text and graph content. Then the :class:`~docx.document.Document`
    class from the `python-docx`_ package is used to publish the results as a
    *Word* document.

    The report is consists of 3 main sections:

    #. An *Overview* of the data and its features.
    #. *Univariate Analysis*: Summary statistics and graphs for each feature.
    #. *Bivariate Analysis*: Pairwise comparisons of all numerical features.

    .. _python-docx: https://python-docx.readthedocs.io/en/latest/

    Parameters
    ----------
    data : Iterable
        The data to analyse.
    target_variable : Optional[Union[str, int]]
        The column to use to group values and color-code graphs.
    title : str, optional
        The title to assign the report, by default "Exploratory Data Analysis
        Report"
    graph_color : str, optional
        The color to apply to the graphs, by default "cyan"
    output_filename : str, optional
        The file name or path to save the document to, by default
        "eda-report.docx"
    table_style : str, optional
        The style to apply to the tables created, by default "Table Grid"
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

    def _get_report(self):
        """Calculate summary statistics, plot graphs, and save the results as
        a .docx file.
        """
        self._create_title_page()
        self._get_variable_info()

        if hasattr(self.variables, "var_pairs"):
            self._get_bivariate_analysis()

        self._save_file()
        logging.info(f"Done. Results saved as {self.OUTPUT_FILENAME!r}")

    def _create_title_page(self) -> None:
        """Add a title and a brief summary of the data."""
        self.document.add_heading(self.TITLE, level=0)

        self.document.add_paragraph(self.intro_text)
        self.document.add_paragraph()

        self._get_numeric_overview_table()
        self._get_categorical_overview_table()

    def _get_numeric_overview_table(self) -> None:
        """Create a table with an overview of the numeric features present."""
        if self.variables.numeric_cols is not None:
            self.document.add_heading("Overview of Numeric Features", level=2)
            self.document.add_paragraph()

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
            self.document.add_heading(
                "Overview of Categorical Features", level=2
            )
            self.document.add_paragraph()

            # column-name | count | unique | top | freq | relative freq
            self._create_table(
                data=self.variables.categorical_stats,
                header=True,
                column_widths=(1.2,) + (0.9,) * 5,
                font_size=8.5,
                style="Normal Table",
            )

    def _get_variable_info(self) -> None:
        """Get a brief introduction, summary statistics, and graphs for each
        individual variable.
        """
        self.document.add_heading("A. Univariate Analysis", level=1)

        for idx, var_name in enumerate(self.variable_descriptions, start=1):
            var_info = self.variable_descriptions[var_name]

            self.document.add_heading(f"{idx}. {var_name}".title(), level=2)
            self.document.add_paragraph(var_info["description"])

            self.document.add_heading("Summary Statistics", level=4)
            self._create_table(var_info["statistics"], column_widths=[2.5, 2])

            # Add most-common-items table, if present
            if var_info.get("most_common_items") is not None:
                self.document.add_heading("Most Common Values", level=4)
                self._create_table(
                    var_info["most_common_items"], column_widths=(2.5, 2)
                )

            for graph in var_info["graphs"].values():
                self.document.add_picture(graph, width=Inches(5.4))

        self.document.add_page_break()

    def _get_bivariate_analysis(self) -> None:
        """Get comparisons, scatterplots and ecdf plots for pairs of numeric
        variables.
        """
        bivariate_heading = self.document.add_heading(
            "B. Bivariate Analysis (Correlation)", level=1
        )
        bivariate_heading.paragraph_format.space_before = Pt(0)
        self.document.add_paragraph()

        self.document.add_picture(
            self.multivariate_graphs["correlation_heatmap"], width=Inches(6.7)
        )
        self.document.add_page_break()

        for idx, var_pair in enumerate(self.bivariate_summaries, start=1):
            self.document.add_heading(
                f"{idx}. {var_pair[0]} vs {var_pair[1]}".title(), level=2
            )
            self.document.add_paragraph(self.bivariate_summaries[var_pair])
            self.document.add_picture(
                self.multivariate_graphs["scatterplots"][var_pair],
                width=Inches(6),
            )
            self.document.add_paragraph()

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
        """Generates a table for the supplied `data` with

        Parameters
        ----------
        data : DataFrame
            The data to tabulate.
        column_widths : Sequence, optional
            The desired number and widths of columns, by default ().
        font_face : str, optional
            The font typeface for cell text, by default "Courier New".
        font_size : float, optional
            The font size for cell text, by default 10.
        style : Optional[str], optional
            A Word table style, by default None.
        header : bool, optional
            Flags whether the first row is a header, by default False.
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

    def _save_file(self) -> None:
        """Save the document as a file."""
        self.document.save(self.OUTPUT_FILENAME)
