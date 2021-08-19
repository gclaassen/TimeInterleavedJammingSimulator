import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import *
from matplotlib import colors


RESULTMODESLOG = 'modesChangeLog'
RESULTRANGELOG = 'rangeLog'
RESULTLETHALRANGELOG = 'lethalrangeLog'
RESULTCOINCIDENCEPERCENTAGELOG = 'coincidenePercLog'
RESULTJAMMINGLOG = 'resultJammingLog'
DETECTIONSLOG = 'deceptionsLog'
CPILOG = 'cpiLog'

RESULTFILEEXT = '.npy'

def plotModes(folder_selected):
    modes = np.load(folder_selected+'/'+RESULTMODESLOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(modes)+1, 1)
    plt.figure()
    ax1 = plt.gca()
    my_colors=colors.ListedColormap(['#008000', '#fdb827', '#D11919', '#2a3439'])
    sb.set(font_scale=0.4)
    sb.heatmap(modes, cmap=my_colors, square=True, linewidth=0.1, linecolor='w', ax=ax1, vmin=0, vmax=3, yticklabels=yticklabels, cbar_kws={"shrink": 0.35, "pad":0.01})
    colorbar = ax1.collections[0].colorbar
    colorbar.set_ticks([0.375, 1.125, 1.875, 2.625])
    colorbar.set_ticklabels(['TS', 'TA', 'TT', 'MG'])
    plt.xticks(fontsize= 5)
    plt.yticks(fontsize= 5)
    plt.xlabel('Intervals', fontsize = 5)
    plt.ylabel('Radars', fontsize = 5)
    plt.savefig('__modes.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def plotCoincidenceRate(folder_selected):
    coincidences = np.load(folder_selected+'/'+RESULTCOINCIDENCEPERCENTAGELOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(coincidences)+1, 1)
    plt.figure()
    ax2 = plt.gca()
    sb.set(font_scale=0.4)
    sb.set_style("ticks")
    sb.heatmap(coincidences, cmap="flare", square=True, linewidth=0.1, linecolor='w', ax=ax2, xticklabels = 3, yticklabels = yticklabels, cbar_kws={"shrink": 0.35, "pad":0.01})
    colorbar = ax2.collections[0].colorbar
    plt.xticks(fontsize= 5)
    plt.yticks(fontsize= 5)
    plt.xlabel('Intervals', fontsize = 5)
    plt.ylabel('Radars', fontsize = 5)
    plt.savefig('__coincRate.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)


def plotJammingPercRate(folder_selected):
    jamming = np.load(folder_selected+'/'+RESULTJAMMINGLOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(jamming)+1, 1)
    plt.figure()
    ax3 = plt.gca()
    sb.set(font_scale=0.4)
    sb.set_style("ticks")
    sb.heatmap(jamming, cmap="coolwarm", square=True, linewidth=0.1, linecolor='w', ax=ax3, vmin=0, xticklabels = 3, yticklabels=yticklabels, cbar_kws={"shrink": 0.35, "pad":0.01})
    colorbar = ax3.collections[0].colorbar
    plt.xticks(fontsize= 5)
    plt.yticks(fontsize= 5)
    plt.xlabel('Intervals', fontsize = 5)
    plt.ylabel('Radars', fontsize = 5)
    plt.savefig('__jammingPerc.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def plotZA(folder_selected):
    za = np.load(folder_selected+'/'+RESULTRANGELOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(za)+1, 1)
    plt.figure()
    ax4 = plt.gca()
    sb.set(font_scale=0.4)
    sb.set_style("ticks")
    za_colors=['#329932', '#236B23', '#ffa700', '#b37400', '#fb4340', '#962826']
    sb.heatmap(za, cmap=za_colors, square=True, linewidth=0.1, linecolor='w', ax=ax4, vmin=0.7, xticklabels = 3, yticklabels=yticklabels, cbar_kws={"shrink": 0.35, "pad":0.01})
    colorbar = ax4.collections[0].colorbar
    plt.xticks(fontsize= 5)
    plt.yticks(fontsize= 5)
    plt.xlabel('Intervals', fontsize = 5)
    plt.ylabel('Radars', fontsize = 5)
    plt.savefig('__za.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def plotWS(folder_selected):
    Rws = np.load(folder_selected+'/'+RESULTLETHALRANGELOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(Rws)+1, 1)
    plt.figure()
    ax5 = plt.gca()
    sb.set(font_scale=0.4)
    sb.set_style("ticks")
    Rws_colors=['#008000', '#D11919']
    sb.heatmap(Rws, cmap=Rws_colors, square=True, linewidth=0.1, linecolor='w', ax=ax5, vmin=0, vmax=1, xticklabels = 3, yticklabels=yticklabels, cbar_kws={"shrink": 0.35, "pad":0.01})
    colorbar = ax5.collections[0].colorbar
    colorbar.set_ticks([0.25, 0.75])
    colorbar.set_ticklabels(["Outside WS range", "Within WS range"])
    plt.xticks(fontsize= 5)
    plt.yticks(fontsize= 5)
    plt.xlabel('Intervals', fontsize = 5)
    plt.ylabel('Radars', fontsize = 5)
    plt.savefig('__ws.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def main():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    plotCoincidenceRate(folder_selected)
    plotJammingPercRate(folder_selected)
    plotZA(folder_selected)
    plotWS(folder_selected)
    plotModes(folder_selected)

if __name__ == "__main__":
    main()