from io import BytesIO

import matplotlib
from matplotlib.figure import Figure

# Matplotlib configuration
matplotlib.rcParams["figure.dpi"] = 150  # resolution (dots per inch)
matplotlib.rcParams["figure.autolayout"] = True  # tight layout
matplotlib.rcParams["savefig.transparent"] = False
matplotlib.rcParams["savefig.edgecolor"] = "k"  # black frame
matplotlib.rcParams["savefig.facecolor"] = "w"  # white background
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["axes.spines.top"] = False  # remove top spine
matplotlib.rcParams["axes.spines.right"] = False  # remove left spine
matplotlib.use("agg")  # use non-interactive matplotlib back-end


Fig = Figure


def savefig(figure):
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG format,
    as bytes in a file-like object.

    This is a utility function helpful in by-passing the *filesystem*. Created
    graphs are stored in :class:`io.BytesIO` objects, and can then be read
    directly as *attributes*. This allows convenient, rapid in-memory access.

    :param figure: A *matplotlib Figure* with plotted axes.
    :type figure: :class:`matplotlib.figure.Figure`
    :return: A file-like object with the figure's contents.
    :rtype: :class:`io.BytesIO`
    """
    graph = BytesIO()
    figure.savefig(graph)

    return graph
