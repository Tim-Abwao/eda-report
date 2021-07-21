import logging

from docx import Document
from docx.shared import Inches, Pt
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.univariate import Variable
from eda_report.plotting import PlotMultiVariate, PlotUnivariate

logging.basicConfig(
    format="[%(levelname)s %(asctime)s.%(msecs)03d] %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


class ReportContent:
    """ """

    def __init__(
        self,
        data,
        *,
        title="Exploratory Data Analysis Report",
        graph_color="cyan",
        target_variable=None,
    ):
        """"""
        self.data = data
        self.variables = MultiVariable(data, target_variable=target_variable)
        self.GRAPH_COLOR = graph_color
        self.TITLE = title
        self._get_content()

    def _get_content(self):
        """"""
        self._create_introductory_summary()
        self._get_numeric_variables_summary_table()
        self._get_categorical_variables_summary_table()
        self._get_variable_descriptions()
        self._get_bivariate_analysis_results()

    def _create_introductory_summary(self):
        """"""
        # Get row and column info
        num_rows, num_cols = self.data.shape

        if num_rows == 1:
            rows = "1 row (observation)"
        else:
            rows = f"{num_rows} rows (observations)"

        if num_cols == 1:
            cols = "1 column (feature)"
        else:
            cols = f"{num_cols} columns (features)"

        # Get numeric column info
        num_numeric = self.data.select_dtypes(include="number").columns.size
        if num_numeric > 1:
            numeric = f", {num_numeric} of which are numeric"
        elif num_numeric == 1:
            numeric = ", 1 of which is numeric"
        else:
            numeric = ""

        self.intro_text = (
            f"The dataset consists of {rows} and {cols}{numeric}."
        )

    def _get_numeric_variables_summary_table(self):
        """"""
        if self.variables.numeric_cols is not None:
            self.numeric_variables_summary = (
                # Get summary statistics for numeric columns
                self.variables.numeric_cols.describe(percentiles=[0.5])
                # Transpose to set the feature names as the index, and summary
                # statistics as columns.
                .round(4).T
            )
        else:
            self.numeric_variables_summary = None

    def _get_categorical_variables_summary_table(self):
        """"""
        if self.variables.categorical_cols is not None:
            self.categorical_variables_summary = (
                # Get summary statistics for categorical columns
                self.variables.categorical_cols.describe().round(4)
                # Transpose to set the feature names as the index, and summary
                # statistics as columns.
                .T
            )
        else:
            self.categorical_variables_summary = None

    def _get_variable_descriptions(self):
        """"""
        self.variable_descriptions = {}
        for col in tqdm(
            self.data.columns,
            bar_format="{desc}: {percentage:3.0f}%|{bar:35}| "
            + "{n_fmt}/{total_fmt} features.",
            desc="Univariate analysis",
            dynamic_ncols=True,
        ):
            # Perform univariate analysis using the Variable class
            var = Variable(
                self.data[col],
                target_data=self.data.get(self.variables.TARGET_VARIABLE),
            )

            # Add a brief introduction of the feature/column
            if var.num_unique == 1:
                unique_vals = "1 unique value"
            elif var.num_unique == 0:
                unique_vals = "no unique values"
            else:
                unique_vals = f"{var.num_unique} unique values"

            self.variable_descriptions[col] = {
                "description": (
                    f"{col.capitalize()} is a {var.var_type} variable with"
                    f" {unique_vals}. {var.missing} of its values are missing."
                ),
                "graphs": PlotUnivariate(
                    variable=var, graph_color=self.GRAPH_COLOR
                ).plot_graphs(),
                "statistics": var.statistics,
                "most_common_items": var.most_common_items
                if hasattr(var, "most_common_items")
                else None,
            }

    def _get_bivariate_analysis_results(self):
        self.multivariate_graphs = PlotMultiVariate(
            multivariable=self.variables, graph_color=self.GRAPH_COLOR
        ).plot_graphs()
        self.bivariate_summaries = {}
        # Compare numeric variable pairs
        for var_pair in self.variables.var_pairs:
            # Add introductory text
            self.bivariate_summaries[var_pair] = (
                f"{var_pair[0].capitalize()} and {var_pair[1].capitalize()}"
                f" have {self.variables.corr_type[var_pair]}."
            )


class ReportDocument(ReportContent):
    """The blueprint for objects that create and populate report documents,
    in *Word (.docx) format*.

    The *input data as a whole* is analysed as an instance of
    :class:`~eda_report.multivariate.MultiVariable`. *Descriptive statistics*,
    *graphs*, and other details can then be obtained as attributes.
    *Individual columns/features* are likewise processed as instances of
    :class:`~eda_report.univariate.Variable`.

    The  :class:`~docx.document.Document` object from the `python-docx`_
    package is then used to publish the results as a *Word*
    document.

    The report is organised into 3 sections:

    #. An *Overview* of the data and its features.
    #. *Univariate Analysis*: Summary statistics and graphs for each
        feature.
    #. *Bivariate Analysis*: Pairwise comparisons of all numerical features.

    .. _python-docx: https://python-docx.readthedocs.io/en/latest/
    """

    def __init__(
        self,
        data,
        *,
        title="Exploratory Data Analysis Report",
        graph_color="orangered",
        target_variable=None,
        output_filename="eda-report.docx",
        table_style="Table Grid",
    ):
        """Initialise an instance of
        :class:`~eda_report.document.ReportDocument`.

        :param data: The data to analyse.
        :type data: array-like, sequence, iterable
        :param title: The top level heading for the report, defaults to
            'Exploratory Data Analysis Report'.
        :type title: str, optional
        :param graph_color: The color to apply to the generated graphs,
            defaults to 'orangered'. See the *matplotlib* `list of named
            colors`_ for all available options.
        :type graph_color: str, optional
        :param output_filename: The name and path for the generated report
            file, defaults to 'eda-report.docx'.
        :type output_filename: str, optional
        :param table_style: *Microsoft Word* table style to apply to the
            created tables, defaults to 'Table Grid'.
        :type table_style: str, optional
        :param target_variable: The dependent feature. Used to color-code
            plotted values. An *integer value* is treated as a *column index*,
            whereas a *string* is treated as a *column label*.
        :type target_variable: int, str, optional

        .. _`list of named colors`:
            https://matplotlib.org/stable/gallery/color/named_colors.html
        """
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
        self._create_title_page()  # begin the report document
        self._get_variable_info()  # summarise each variable

        if hasattr(self.variables, "var_pairs"):
            self._get_bivariate_analysis()  # summarise variable pairs

        self._save_file()
        logging.info(f"Done. Results saved as {self.OUTPUT_FILENAME!r}")

    def _create_title_page(self):
        """Add a title and a brief summary of the data."""
        # Main title
        self.document.add_heading(self.TITLE, level=0)

        # Add introductory paragraph
        self.document.add_paragraph(self.intro_text)
        self.document.add_paragraph()

        # Add an overview of the data
        self._get_numeric_overview_table()
        self._get_categorical_overview_table()

        if hasattr(self.variables, "var_pairs"):
            # Add a joint scatterplot of the numeric features
            self.document.add_heading(
                "Joint Scatter-plot of Numeric Columns", level=2
            )
            self.document.add_picture(
                self.multivariate_graphs["joint_scatterplot"],
                width=Inches(6.5),
            )
            self.document.add_page_break()

    def _get_numeric_overview_table(self):
        """Create a table with an overview of numeric features."""
        if self.variables.numeric_cols is not None:
            self.document.add_heading("Overview of Numeric Features", level=2)
            self.document.add_paragraph()

            self._create_table(
                data=self.numeric_variables_summary,
                header=True,
                column_widths=(1.5,) + (0.9,) * 6,
                style="Normal Table",
            )

    def _get_categorical_overview_table(self):
        """Create a table with an overview of categorical features."""
        if self.variables.categorical_cols is not None:
            self.document.add_heading(
                "Overview of Categorical Features", level=2
            )
            self.document.add_paragraph()

            # Create a table with column-names and summary statistics - count,
            # unique, top and freq
            self._create_table(
                data=self.categorical_variables_summary,
                header=True,
                column_widths=(1.4,) + (1,) * 4,
                style="Normal Table",
            )

    def _get_variable_info(self):
        """Get a brief introduction, summary statistics, and graphs for each
        individual variable.
        """
        # Univariate section heading
        univariate_heading = self.document.add_heading(
            "A. Univariate Analysis", level=1
        )
        univariate_heading.paragraph_format.space_before = Pt(0)

        for idx, var_name in enumerate(self.variable_descriptions):
            var_info = self.variable_descriptions[var_name]
            # Add a heading for the feature/column
            self.document.add_heading(f"{idx}. {var_name}".title(), level=2)

            # Add a brief introduction of the feature/column
            self.document.add_paragraph(var_info["description"])

            # Add a table of summary statistics
            self.document.add_heading("Summary Statistics", level=4)
            self._create_table(var_info["statistics"], column_widths=[2.5, 2])

            # Add most-common-items, if they were recorded
            if var_info.get("most_common_items") is not None:
                self.document.add_heading("Most Common Values", level=4)
                self._create_table(
                    var_info["most_common_items"], column_widths=(2.5, 2)
                )

            # Add graphs
            for graph in var_info["graphs"].values():  # var._graphs is a dict
                self.document.add_picture(graph, width=Inches(5.4))

            self.document.add_page_break()

    def _get_bivariate_analysis(self):
        """Get comparisons, scatterplots and ecdf plots for pairs of numeric
        variables.
        """
        # Bivariate section heading
        bivariate_heading = self.document.add_heading(
            "B. Bivariate Analysis (Correlation)", level=1
        )
        bivariate_heading.paragraph_format.space_before = Pt(0)
        self.document.add_paragraph()

        # Add joint correlation heatmap of all numeric columns
        self.document.add_picture(
            self.multivariate_graphs["correlation_heatmap"], width=Inches(6.7)
        )
        self.document.add_page_break()

        # Compare numeric variable pairs
        for idx, var_pair in enumerate(self.bivariate_summaries, start=1):
            # Add heading
            self.document.add_heading(
                f"{idx}. {var_pair[0]} vs {var_pair[1]}".title(), level=2
            )
            # Add introductory text
            self.document.add_paragraph(self.bivariate_summaries[var_pair])

            # Add graphs
            self.document.add_picture(
                self.multivariate_graphs["scatterplots"][var_pair],
                width=Inches(6),
            )
            self.document.add_paragraph()

            # Add page break after every 2 pairs
            if idx % 2 == 0:
                self.document.add_page_break()

    def _create_table(self, data, column_widths=(), style=None, header=False):
        """Create a table from the given data and add it to the document.

        :param data: The data to put into a table.
        :type data: :class:`pandas.DataFrame`
        :param column_widths: The desired table column widths, defaults to ().
        :type column_widths: tuple, optional
        :param style: *Word* table style to apply, defaults to None.
        :type style: str, optional
        :param header: Whether or not to include column names as the first row
            in the table, defaults to False.
        :type header: bool, optional
        """
        if header:
            # Add the column names as a row at index ''
            data.loc["", :] = data.columns
            # Sort the index in ascending order, so that the column names end
            # up at the top, in true header fashion.
            # The column names will be the first row of the table created.
            data.sort_index(inplace=True)

        # Create the table
        table = self.document.add_table(
            rows=len(data),  # A row for each row in the data
            cols=len(column_widths),  # As many columns as column-widths given
        )

        # Set table style
        if style is None:
            table.style = self.document.styles[self.TABLE_STYLE]
        else:
            table.style = self.document.styles[style]

        # Set column dimensions
        for idx, width in enumerate(column_widths):
            table.columns[idx].width = Inches(width)

        # Populate the table with the data
        for idx, row_data in enumerate(data.itertuples()):
            # Populate the row's cells
            for cell, datum in zip(table.rows[idx].cells, row_data):
                cell.text = f"{datum}"

        self.document.add_paragraph()

    def _save_file(self):
        """Save the document as a .docx file."""
        self.document.save(self.OUTPUT_FILENAME)


if __name__ == "__main__":
    import seaborn as sns

    data = sns.load_dataset("iris")
    rep = ReportDocument(data)
    print(
        dir(
            rep
        )
    )
    rep._save_file()
