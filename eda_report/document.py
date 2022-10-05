import logging
from typing import Iterable, Sequence, Union

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.text.parfmt import ParagraphFormat
from pandas.core.frame import DataFrame

from eda_report.content import _ReportContent

logging.basicConfig(
    format="[%(levelname)s %(asctime)s.%(msecs)03d] %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


class ReportDocument(_ReportContent):
    """Creates a :class:`~docx.document.Document` with analysis results
    using `python-docx`_.

    The report consists of 3 main sections:

    #. An **Overview** of the data and its features.
    #. **Univariate Analysis**: Summary statistics and graphs for each feature.
    #. **Bivariate Analysis**: Pairwise comparisons of numerical features.

    .. _python-docx: https://python-docx.readthedocs.io/en/latest/

    Args:
        data (Iterable): The data to analyze.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        groupby_data (Union[str, int], optional): The column to
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
        groupby_data: Union[str, int] = None,
        output_filename: str = "eda-report.docx",
        table_style: str = "Table Grid",
    ) -> None:
        super().__init__(
            data,
            title=title,
            graph_color=graph_color,
            groupby_data=groupby_data,
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

        if hasattr(self.multivariable, "var_pairs"):
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
        self, format: ParagraphFormat, before: int = 15, after: int = 7
    ) -> None:
        """Set the spacing above or below a heading.

        Args:
            format (ParagraphFormat): The heading's format.
            before (int, optional): Size of spacing above the heading in pt.
                Defaults to 15.
            after (int, optional): Size of spacing below the heading in pt.
                Defaults to 7.
        """
        format.space_before = Pt(before)
        format.space_after = Pt(after)

    def _get_numeric_overview_table(self) -> None:
        """Create a table with an overview of the numeric features present."""
        if self.multivariable.numeric_cols is not None:
            heading = self.document.add_heading(
                "Overview of Numeric Features", level=1
            )
            self._format_heading_spacing(heading.paragraph_format)
            # count | mean | std | min | 25% | 50% | 75% | max
            self._create_table(
                data=self.multivariable.numeric_stats,
                header=True,
                column_widths=(1.2,) + (0.7,) * 8,
                font_size=8.5,
                style="Normal Table",
            )

    def _get_categorical_overview_table(self) -> None:
        """Create a table with an overview of the categorical features
        present.
        """
        if self.multivariable.categorical_cols is not None:
            heading = self.document.add_heading(
                "Overview of Categorical Features", level=1
            )
            self._format_heading_spacing(heading.paragraph_format)
            # column-name | count | unique | top | freq | relative freq
            self._create_table(
                data=self.multivariable.categorical_stats,
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
        for idx, var_name in enumerate(self.variable_info, start=1):
            var_info = self.variable_info[var_name]

            heading = self.document.add_heading(
                f"1.{idx}. {var_name}".title(), level=2
            )
            self._format_heading_spacing(
                heading.paragraph_format, before=12, after=5
            )
            self.document.add_paragraph(var_info["description"])

            stats_heading = self.document.add_heading(
                "Summary Statistics", level=4
            )
            stats_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

            self._create_table(var_info["statistics"], column_widths=[2.5, 2])

            for graph in (var_info["graphs"]).values():
                self.document.add_picture(graph, width=Inches(4.4))
                picture_paragraph = self.document.paragraphs[-1]
                picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if (norm_tests := var_info["normality_tests"]) is not None:

                norm_test_heading = self.document.add_heading(
                    "Tests for Normality", level=4
                )
                norm_test_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

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
        """Get comparisons and regression-plots for pairs of numeric
        variables.
        """
        bivariate_heading = self.document.add_heading(
            "2. Bivariate Analysis (Correlation)", level=1
        )
        self._format_heading_spacing(
            bivariate_heading.paragraph_format, before=0
        )

        self.document.add_picture(
            self.bivariate_graphs["correlation_plot"],
            width=Inches(6.7),
        )
        picture_paragraph = self.document.paragraphs[-1]
        picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self.document.add_page_break()

        for idx, var_pair in enumerate(self.bivariate_summaries, start=1):
            heading = self.document.add_heading(
                f"2.{idx} {var_pair[0]} vs {var_pair[1]}".title(), level=2
            )
            self._format_heading_spacing(
                heading.paragraph_format, before=16, after=5
            )
            self.document.add_paragraph(self.bivariate_summaries[var_pair])
            self.document.add_picture(
                self.bivariate_graphs["regression_plots"][var_pair],
                width=Inches(3.5),
            )
            picture_paragraph = self.document.paragraphs[-1]
            picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _create_table(
        self,
        data: DataFrame,
        column_widths: Sequence = (),
        font_face: str = "Courier New",
        font_size: float = 10,
        style: str = None,
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
            style (str, optional): A `Word` table style. Defaults to
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
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Set column dimensions
        for idx, width in enumerate(column_widths):
            table.columns[idx].width = Inches(width)

        # Populate the rows
        for idx, row_data in enumerate(data.itertuples()):
            for cell, value in zip(table.rows[idx].cells, row_data):
                cell.text = f"{value}".rstrip("0").rstrip(".")

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
