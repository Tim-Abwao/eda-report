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
    """Save a matplotlib figure in a file-like object, and return it."""
    graph = BytesIO()
    figure.savefig(graph)
    return graph
