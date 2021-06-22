from io import BytesIO

import matplotlib
from matplotlib.figure import Figure

# Matplotlib configuration
matplotlib.rc("figure", dpi=150, autolayout=True)
matplotlib.rc("savefig", edgecolor="k", facecolor="w")
matplotlib.rc("font", family="serif")
matplotlib.rc("axes.spines", top=False, right=False)
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
