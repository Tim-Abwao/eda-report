import logging

from docx import Document
from docx.shared import Inches
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.univariate import Variable


logging.basicConfig(
    format='[%(levelname)s %(asctime)s.%(msecs)03d] %(message)s',
    level=logging.INFO, datefmt='%H:%M:%S'
)


class ReportDocument:
    """The blueprint for objects with methods to create and populate *.docx*
    files.

    The *input data as a whole* is processed as an instance of
    :class:`~eda_report.multivariate.MultiVariable` to get *group statistics
    and plots*. *Individual columns/features* are processed as instances of
    :class:`~eda_report.univariate.Variable` to get statistics and plots for
    *each feature*.

    The `python-docx`_ module is then used to write the results as a *Word*
    document.

    .. _python-docx: https://python-docx.readthedocs.io/en/latest/
    """
    def __init__(self, data, title='Exploratory Data Analysis Report',
                 output_filename='eda-report.docx',
                 graph_color='orangered', table_style='Table Grid'):
        """Initialise an instance of
        :class:`~eda_report.document.ReportDocument`.

        :param data: The data to analyse.
        :type data: Array-like, sequence, iterable
        :param title: The top level heading for the report, defaults to
            'Exploratory Data Analysis Report'.
        :type title: str, optional
        :param output_filename: The name to give the generated report file,
            defaults to 'eda-report.docx'.
        :type output_filename: str, optional
        :param graph_color: A valid matplotlib color specifier, defaults
            to 'orangered'.
        :type graph_color: str, optional
        :param table_style: *Microsoft Word* table style to apply to the
            created tables, defaults to 'Table Grid'.
        :type table_style: str, optional
        """
        self.data = data
        self.TITLE = title
        self.GRAPH_COLOR = graph_color
        self.TABLE_STYLE = table_style
        self.OUTPUT_FILENAME = output_filename
        self.document = Document()
        self._get_report()

    def _get_report(self):
        """Calculate summary statistics, plot graphs, and save the results as
        a .docx file.
        """
        logging.info('Assessing correlation in numeric variables...')
        self.variables = MultiVariable(self.data,
                                       graph_color=self.GRAPH_COLOR)
        logging.info('Done. Summarising each variable...')
        self._create_title_page()  # begin the report document
        self._get_variable_info()  # summarise each variable

        if hasattr(self.variables, 'var_pairs'):
            self._get_bivariate_analysis()  # summarise variable pairs

        self._save_file()
        logging.info(f'Done. Results saved as {self.OUTPUT_FILENAME!r}')

    def _create_title_page(self):
        """Add a title and a brief summary of the data.
        """
        # Title
        self.document.add_heading(self.TITLE, level=0)

        # Brief summary
        num_rows, num_cols = self.data.shape
        num_numeric = self.data.select_dtypes(include='number').columns.size

        if num_rows > 1:
            rows = f'{num_rows} rows (observations)'
        else:
            rows = '1 row (observation)'

        if num_cols > 1:
            cols = f'{num_cols} columns (features)'
        else:
            cols = '1 column (feature)'

        if num_numeric > 1:
            numeric = f', {num_numeric} of which are numeric'
        elif num_numeric == 1:
            numeric = ', 1 of which is numeric'
        else:
            numeric = ''

        intro = f'The dataset consists of {rows} and {cols}{numeric}.'

        self.document.add_paragraph(intro)
        self.document.add_paragraph()

        # Add overview of the data
        self._get_numeric_overview_table()
        self._get_categorical_overview_table()

        if hasattr(self.variables, 'joint_scatterplot'):
            # Add a joint scatterplot of the numeric features
            self.document.add_heading(
                'Joint Scatter-plot of Numeric Columns', level=2)
            self.document.add_picture(self.variables.joint_scatterplot,
                                      width=Inches(6.5))
            self.document.add_page_break()

    def _get_numeric_overview_table(self):
        """Create a table with the overview for numeric features.
        """
        if self.variables.numeric_cols is not None:
            self.document.add_heading('Overview of Numeric Features', level=2)
            self.document.add_paragraph()
            # Get summary statistics for all columns, round the values to 4
            # decimal places, and set the feature names as the index by
            # transposing.
            summary = self.variables.numeric_cols.describe([0.5]).round(4).T
            # Create a table with 9 columns
            self._create_table(
                data=summary, header=True,
                column_widths=(1.5,) + (0.9,)*6, style='Normal Table'
            )

    def _get_categorical_overview_table(self):
        """Create a table with the overview for categorical features.
        """
        if self.variables.categotical_cols is not None:
            self.document.add_heading(
                'Overview of Categorical Features', level=2
            )
            self.document.add_paragraph()
            # Get summary statistics for all columns, round the values to 4
            # decimal places, and set the feature names as the index by
            # transposing.
            summary = self.variables.categotical_cols.describe().round(4).T
            # Create a table with 5 columns
            self._create_table(
                data=summary, header=True,
                column_widths=(1.2,) + (0.8,)*4, style='Normal Table'
            )

    def _get_variable_info(self):
        """Get a brief introduction, summary statistics, and graphs for each
        individual variable.
        """
        self.document.add_heading('A. Univariate Analysis', level=1)
        for idx, col in enumerate(tqdm(self.data.columns, ncols=79),
                                  start=1):
            var = Variable(self.data[col], graph_color=self.GRAPH_COLOR)
            # Heading
            self.document.add_heading(f'{idx}. {col}'.title(), level=2)
            # Introduction
            p = self.document.add_paragraph()
            p.add_run(f'{col}'.capitalize()).bold = True
            p.add_run(f' is a {var.var_type} variable ')
            p.add_run(f'with {var.num_unique} unique values. ')
            p.add_run(f'{var.missing} of its values are missing.')
            # Summary statistics
            self.document.add_heading('Summary Statistics', level=4)
            self._create_table(var.statistics, column_widths=[2.5, 2])
            if hasattr(var, 'most_common_items'):
                self.document.add_heading('Most Common Values', level=4)
                self._create_table(var.most_common_items,
                                   column_widths=(2.5, 2))
            # Graphs
            for graph in var._graphs.values():  # var._graphs is a dict
                self.document.add_picture(graph, width=Inches(5.4))

            self.document.add_page_break()

    def _get_bivariate_analysis(self):
        """Get comparisons and scatterplots for pairs of numeric variables.
        """
        self.document.add_heading(
            'B. Bivariate Analysis (Correlation)', level=1)
        self.document.add_paragraph()
        self.document.add_picture(self.variables.joint_correlation_plot,
                                  width=Inches(6.7))
        self.document.add_page_break()

        for idx, var_pair in enumerate(self.variables.var_pairs, start=1):
            # Heading
            self.document.add_heading(
                f'{idx}. {var_pair[0]} vs {var_pair[1]}'.title(),
                level=2)
            # Introductory text
            p = self.document.add_paragraph()
            p.add_run(f'{var_pair[0]}'.capitalize()).bold = True
            p.add_run(' and ')
            p.add_run(f'{var_pair[1]}'.capitalize()).bold = True
            p.add_run(f' have {self.variables.corr_type[var_pair]}.')
            # Scatter-plot
            self.document.add_picture(
                self.variables.bivariate_scatterplots[var_pair],
                width=Inches(6)
            )
            self.document.add_paragraph()

            if idx % 2 == 0:
                # Add page break after every 2 pairs
                self.document.add_page_break()

    def _create_table(self, data, column_widths=(), style=None, header=False):
        """Create a table from the given data and add it to the document.


        :param data: The data to put into a table.
        :type data: ``pandas.DataFrame``
        :param column_widths: The desired table column widths, defaults to ().
        :type column_widths: tuple, optional
        :param style: *Word* table style to apply, defaults to None.
        :type style: str, optional
        :param header: Whether or not to include column names as the first row
            in the table, defaults to False.
        :type header: bool, optional
        """
        if header:
            # Add the column names as a row.
            data.loc['', :] = data.columns
            # Sort the index in ascending order. Placing the column names at
            # index '' takes them to the top after sorting.
            data.sort_index(inplace=True)

        # Create the table
        table = self.document.add_table(
            rows=len(data),  # A row for each row in the data
            cols=len(column_widths)  # As many columns as column-widths given
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
            table_row = table.rows[idx]
            # Populate the row's cells
            for cell, datum in zip(table_row.cells, row_data):
                cell.text = f'{datum}'

        self.document.add_paragraph()

    def _save_file(self):
        """Save the document as a .docx file.
        """
        self.document.save(self.OUTPUT_FILENAME)
