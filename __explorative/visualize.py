import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import *
from matplotlib import colors
import os


RESULTMODESLOG = 'modesChangeLog'
RESULTRANGELOG = 'rangeLog'
RESULTLETHALRANGELOG = 'lethalrangeLog'
RESULTCOINCIDENCEPERCENTAGELOG = 'coincidenePercLog'
RESULTJAMMINGLOG = 'resultJammingLog'
DETECTIONSLOG = 'deceptionsLog'
CPILOG = 'cpiLog'

RESULTFILEEXT = '.npy'

fontSize_tics = 8

def plotModes(folder_selected, testName):
    modes = np.load(folder_selected+'/'+RESULTMODESLOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(modes)+1, 2)
    plt.figure()
    ax1 = plt.gca()
    my_colors=colors.ListedColormap(['#008000', '#fdb827', '#D11919', '#2a3439'])
    sb.set(font_scale=0.6)
    sb.heatmap(modes, cmap= my_colors, square= True, linewidth= 0.1, linecolor= 'w', ax= ax1, vmin= 0, vmax= 3, xticklabels= 3, yticklabels= 2, cbar_kws= {"shrink": 0.35, "pad":0.01})
    ax1.set_yticklabels(yticklabels, rotation='horizontal')
    colorbar = ax1.collections[0].colorbar
    colorbar.set_ticks([0.375, 1.125, 1.875, 2.625])
    colorbar.set_ticklabels(['TS', 'TA', 'TT', 'MG'])
    plt.xticks(fontsize= fontSize_tics)
    plt.yticks(fontsize= fontSize_tics)
    plt.xlabel('Interval', fontsize = fontSize_tics)
    plt.ylabel('Radars', fontsize = fontSize_tics)
    plt.savefig(testName + '__modes.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def plotCoincidenceRate(folder_selected, testName):
    coincidences = np.load(folder_selected+'/'+RESULTCOINCIDENCEPERCENTAGELOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(coincidences)+1, 2)
    ___, totIntervals = coincidences.shape
    xtickLables = np.arange(1, totIntervals, 3)
    plt.figure()
    ax2 = plt.gca()
    sb.set(font_scale=0.6)
    sb.set_style("ticks")
    sb.heatmap(coincidences, cmap="flare", square=True, linewidth=0.1, linecolor='w', ax=ax2, xticklabels = 3, yticklabels = 2, cbar_kws={"shrink": 0.35, "pad":0.01})
    ax2.set_yticklabels(yticklabels, rotation='horizontal')
    ax2.set_xticklabels(xtickLables)
    colorbar = ax2.collections[0].colorbar
    plt.xticks(fontsize= fontSize_tics)
    plt.yticks(fontsize= fontSize_tics)
    plt.xlabel('Interval', fontsize= fontSize_tics)
    plt.ylabel('Radars', fontsize= fontSize_tics)
    plt.savefig(testName + '__coincRate.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)


def plotJammingPercRate(folder_selected, testName):
    jamming = np.load(folder_selected+'/'+RESULTJAMMINGLOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(jamming)+1, 2)
    ___, totIntervals = jamming.shape
    xtickLables = np.arange(1, totIntervals, 3)
    plt.figure()
    ax3 = plt.gca()
    sb.set(font_scale=0.6)
    sb.set_style("ticks")
    sb.heatmap(jamming, cmap="coolwarm", square=True, linewidth=0.1, linecolor='w', ax=ax3, vmin=0, xticklabels = 3, yticklabels= 2, cbar_kws={"shrink": 0.35, "pad":0.01})
    ax3.set_yticklabels(yticklabels, rotation='horizontal')
    ax3.set_xticklabels(xtickLables)
    colorbar = ax3.collections[0].colorbar
    plt.xticks(fontsize= fontSize_tics)
    plt.yticks(fontsize= fontSize_tics)
    plt.xlabel('Interval', fontsize= fontSize_tics)
    plt.ylabel('Radars', fontsize= fontSize_tics)
    plt.savefig(testName + '__jammingPerc.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def plotZA(folder_selected, testName):
    za = np.load(folder_selected+'/'+RESULTRANGELOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(za)+1, 2)
    ___, totIntervals = za.shape
    xtickLables = np.arange(1, totIntervals, 3)
    plt.figure()
    ax4 = plt.gca()
    sb.set(font_scale=0.6)
    sb.set_style("ticks")
    za_colors=['#329932', '#236B23', '#ffa700', '#b37400', '#fb4340', '#962826']
    sb.heatmap(za, cmap=za_colors, square=True, linewidth=0.1, linecolor='w', ax=ax4, vmin=0.7, xticklabels = 3, yticklabels= 2, cbar_kws={"shrink": 0.35, "pad":0.01})
    ax4.set_yticklabels(yticklabels, rotation='horizontal')
    ax4.set_xticklabels(xtickLables)
    colorbar = ax4.collections[0].colorbar
    plt.xticks(fontsize= fontSize_tics)
    plt.yticks(fontsize= fontSize_tics)
    plt.xlabel('Interval', fontsize= fontSize_tics)
    plt.ylabel('Radars', fontsize= fontSize_tics)
    plt.savefig(testName + '__za.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def plotWS(folder_selected, testName):
    Rws = np.load(folder_selected+'/'+RESULTLETHALRANGELOG+RESULTFILEEXT)
    yticklabels = np.arange(1, len(Rws)+1, 2)
    ___, totIntervals = Rws.shape
    xtickLables = np.arange(1, totIntervals, 3)
    plt.figure()
    ax5 = plt.gca()
    sb.set(font_scale=0.6)
    sb.set_style("ticks")
    Rws_colors=['#008000', '#D11919']
    sb.heatmap(Rws, cmap=Rws_colors, square=True, linewidth=0.1, linecolor='w', ax=ax5, vmin=0, vmax=1, xticklabels = 3, yticklabels= 2, cbar_kws={"shrink": 0.35, "pad":0.01})
    ax5.set_yticklabels(yticklabels, rotation='horizontal')
    ax5.set_xticklabels(xtickLables)
    colorbar = ax5.collections[0].colorbar
    colorbar.set_ticks([0.25, 0.75])
    colorbar.set_ticklabels(["Out range", "In range"])
    plt.xticks(fontsize= fontSize_tics)
    plt.yticks(fontsize= fontSize_tics)
    plt.xlabel('Interval', fontsize= fontSize_tics)
    plt.ylabel('Radars', fontsize= fontSize_tics)
    plt.savefig(testName + '__ws.pdf', bbox_inches='tight',pad_inches = 0, dpi = 600)

def calculateStats(folder_selected):
    modes = np.load(folder_selected+'/'+RESULTMODESLOG+RESULTFILEEXT)
    lethalRange = np.load(folder_selected+'/'+RESULTLETHALRANGELOG+RESULTFILEEXT)

    for radarIdx, radar in enumerate(modes):
        # count the total times the mode is active over the scenario
        unique, counts = np.unique(radar, return_counts=True)
        
        
        # print("{0} \n\n".format(dict(zip(unique, counts))))
        # count the total times a mode is in lethal range
        countModes = np.zeros((4), dtype=int)

        listLrIdx = np.where(lethalRange[radarIdx] == 1)
        if listLrIdx[0].size > 0:
            for __, lrIdx in enumerate(listLrIdx[0]):
                if(radar[lrIdx] == 0):
                    countModes[0] = countModes[0] + 1
                elif(radar[lrIdx] == 1):
                    countModes[1] = countModes[1] + 1
                elif(radar[lrIdx] == 2):
                    countModes[2] = countModes[2] + 1
                elif(radar[lrIdx] == 3):
                    countModes[3] = countModes[3] + 1
        
        print("Radar {0}".format(radarIdx + 1))
        print("{0}".format(counts))
        print("{0} \n\n".format(countModes))


def main():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()

    testName = os.path.basename(folder_selected)

    print("Test: {0}".format(folder_selected))

    calculateStats(folder_selected)

    plotCoincidenceRate(folder_selected, testName)
    plotJammingPercRate(folder_selected, testName)
    plotZA(folder_selected, testName)
    plotWS(folder_selected, testName)
    plotModes(folder_selected, testName)

if __name__ == "__main__":
    main()