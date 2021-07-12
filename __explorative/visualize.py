import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import *
import os
import matplotlib.gridspec as gridspec

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
# plt.style.use('seaborn')
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

# plt.rcParams.update(tex_fonts)

root = Tk()
root.withdraw()
folder_selected = filedialog.askdirectory()

RESULTMODESLOG = 'modesChangeLog'
RESULTRANGELOG = 'rangeLog'
RESULTLETHALRANGELOG = 'lethalrangeLog'
RESULTCOINCIDENCEPERCENTAGELOG = 'coincidenePercLog'
RESULTJAMMINGLOG = 'resultJammingLog'

RESULTFILEEXT = '.npy'

# Here we create a figure instance, and multiple subplots
# fig = plt.figure(figsize=set_size('thesis'))
fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(3, 2)
ax1 = fig.add_subplot(gs[0, :])
ax1 = plt.subplot2grid((3,2), (0,0), colspan = 1, rowspan = 1)
ax1.set_title('Mode change per interval')

ax2 = plt.subplot2grid((3,2), (1,0), colspan = 1, rowspan = 1)
ax2.set_title('Coincidences percentage per interval')

ax3 = plt.subplot2grid((3,2), (2,0), colspan = 1, rowspan = 1)
ax3.set_title('Percentage minimum jamming pulses per CPI')

ax4 = plt.subplot2grid((3,2), (1,1), colspan = 1, rowspan = 1)
ax4.set_title('Zone assessment per interval')

ax5 = plt.subplot2grid((3,2), (2,1), colspan = 1, rowspan = 1)
ax5.set_title('Lethal range flag')

modes = np.load(folder_selected+'/'+RESULTMODESLOG+RESULTFILEEXT)
# the content of labels of these yticks
yticklabels = np.arange(1, len(modes)+1, 1)

my_colors=['#008000', '#fdb827', '#D11919', '#2a3439']
# my_colors=['#008000', '#fdb827']
sb.heatmap(modes, cmap=my_colors, square=True, linewidth=0.1, linecolor='w', ax=ax1, vmin=0, vmax=3, yticklabels=yticklabels)
colorbar = ax1.collections[0].colorbar
colorbar.set_ticks([0, 1, 2, 3])
colorbar.set_ticklabels(['TS', 'TA', 'TT', 'MG'])
# ax.collections[0].colorbar.remove()

coincidences = np.load(folder_selected+'/'+RESULTCOINCIDENCEPERCENTAGELOG+RESULTFILEEXT)
sb.heatmap(coincidences, cmap="coolwarm", square=True, linewidth=0.1, linecolor='w', ax=ax2, vmin=0, yticklabels=yticklabels)

colorbar = ax2.collections[0].colorbar

jamming = np.load(folder_selected+'/'+RESULTJAMMINGLOG+RESULTFILEEXT)
sb.heatmap(jamming, cmap="coolwarm", square=True, linewidth=0.1, linecolor='w', ax=ax3, vmin=0, yticklabels=yticklabels)
colorbar = ax3.collections[0].colorbar

za = np.load(folder_selected+'/'+RESULTRANGELOG+RESULTFILEEXT)
sb.heatmap(za, cmap="coolwarm", square=True, linewidth=0.1, linecolor='w', ax=ax4, vmin=0.7, yticklabels=yticklabels)
colorbar = ax4.collections[0].colorbar

Rws = np.load(folder_selected+'/'+RESULTLETHALRANGELOG+RESULTFILEEXT)
Rws_colors=['#008000', '#D11919']
sb.heatmap(Rws, cmap=Rws_colors, square=True, linewidth=0.1, linecolor='w', ax=ax5, vmin=0, vmax=1, yticklabels=yticklabels)
colorbar = ax5.collections[0].colorbar
colorbar.set_ticks([0, 1])

coincidences_avg = np.round(np.average(coincidences, axis=1), decimals=3)
coincidences_med = np.round(np.median(coincidences, axis=1), decimals=3)

za_avg = np.round(np.average(za, axis=1), decimals=3)
za_med = np.round(np.median(za, axis=1), decimals=3)
za_min = np.round(np.min(za, axis=1), decimals=3)
za_max = np.round(np.max(za, axis=1), decimals=3)

plt.show()