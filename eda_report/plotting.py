import matplotlib
from io import BytesIO
from matplotlib.figure import Figure


# Matplotlib configuration
matplotlib.rcParams['figure.dpi'] = 150  # resolution (dots per inch)
matplotlib.rcParams['figure.autolayout'] = True  # tight layout
matplotlib.rcParams['savefig.transparent'] = False   # transparent background
matplotlib.rcParams["savefig.edgecolor"] = 'k'  # black frame
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['axes.spines.top'] = False  # remove top spine
matplotlib.rcParams['axes.spines.right'] = False  # remove left spine
matplotlib.use('agg')  # use non-interactive matplotlib back-end

Fig = Figure


def savefig(figure):
    """Saves the contents of a matplotlib figure, in PNG format, as bytes in a
    file-like object.

    :param figure: A matplotlib figure with plotted axes.
    :type figure: ``matplotlib.figure.Figure``
    :return: A file-like object with the figure's contents.
    :rtype: ``io.BytesIo``
    """
    graph = BytesIO()
    figure.savefig(graph)
    return graph
