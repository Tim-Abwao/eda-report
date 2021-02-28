from eda_report.document import ReportDocument


__version__ = '0.0.3'


def get_word_report(data, *, title='Exploratory Data Analysis Report',
                    graph_colour='orangered',
                    output_filename='basic-report.docx'):
    """Get an EDA report in .docx format."""
    ReportDocument(data, title=title, graph_colour=graph_colour,
                   output_filename=output_filename)
