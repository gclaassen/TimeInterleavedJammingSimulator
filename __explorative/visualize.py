import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

def set_size(width, fraction=1, subplots=(1, 1)):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float or string
            Document width in points, or string of predined document type
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    if width == 'thesis':
        width_pt = 426.79135
    elif width == 'beamer':
        width_pt = 307.28987
    else:
        width_pt = width

    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)

# Using seaborn's style
plt.style.use('seaborn')
# With LaTex fonts
# plt.style.use('tex')
width = 345

tex_fonts = {
    # Use LaTeX to write all text
    "text.usetex": True,
    "font.family": "serif",
    # Use 10pt font in plots, to match 10pt font in document
    "axes.labelsize": 14,
    "font.size": 14,
    # Make the legend/label fonts a little smaller
    "legend.fontsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14
}

plt.rcParams.update(tex_fonts)

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

X = np.load(file_path)
file_name = os.path.basename(os.path.normpath(file_path))

[file_name_wo_ext, ext] = os.path.splitext(file_name)

if(file_name == "modesChangeLog.npy"):
    fig,ax = plt.subplots(1,1,figsize=set_size('thesis'))

    my_colors=['#008000', '#fdb827', '#D11919', '#2a3439']
    # my_colors=['#008000', '#fdb827']
    sb.heatmap(X, cmap=my_colors, square=True, linewidth=1, linecolor='w')
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0, 1, 2, 3])
    colorbar.set_ticklabels(['TS', 'TA', 'TT', 'MG'])
    ax.collections[0].colorbar.remove()

    plt.savefig(file_name_wo_ext + '.pdf', orientation='landscape')
    plt.show()

else:
    fig,ax = plt.subplots(1,1,figsize=set_size('thesis'))
    sb.heatmap(X, cmap="rocket_r", square=True, linewidth=1, linecolor='w')
    colorbar = ax.collections[0].colorbar
    plt.savefig(file_name_wo_ext + '.pdf', orientation='landscape')
    plt.show()