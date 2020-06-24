"""Radar Environment Visualizer"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import common

def worldview(pf, th):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #flight path
    pfColor = 'b'
    totalFpNodePoints =  pf.flight_path.size

    for node in range(totalFpNodePoints):
        ##nodes
        if(node == 0):
            ax.scatter(pf.flight_path[node][common.XCOORD], pf.flight_path[node][common.YCOORD], pf.flight_path[node][common.ZCOORD], c=pfColor, marker='o', s=30)
        elif(node == totalFpNodePoints-1):
            ax.scatter(pf.flight_path[node][common.XCOORD], pf.flight_path[node][common.YCOORD], pf.flight_path[node][common.ZCOORD], c=pfColor, marker='X', s=30)
        else:
            ax.scatter(pf.flight_path[node][common.XCOORD], pf.flight_path[node][common.YCOORD], pf.flight_path[node][common.ZCOORD], c=pfColor, marker='>', s=30)

        ##lines
        if node is not 0:
            ax.plot([pf.flight_path[node-1][common.XCOORD], pf.flight_path[node][common.XCOORD]],[pf.flight_path[node-1][common.YCOORD], pf.flight_path[node][common.YCOORD]],zs=[pf.flight_path[node-1][common.ZCOORD], pf.flight_path[node][common.ZCOORD]], c=pfColor)

    #threats
    thColor = 'r'
    totalThreatNodePoints = th.__len__()

    for thNode in range(totalThreatNodePoints):
    #nodes
        ax.scatter(th[thNode].location[common.XCOORD], th[thNode].location[common.YCOORD], th[thNode].location[common.ZCOORD], c=thColor, marker='*', s=150)
    #areas
        totalModes = th[thNode].emitters[0].size
        for mode in range(totalModes):
            modeColor = None

            [x,y,z] = domeCreate(th[0].emitters[0][mode][common.THREAT_RANGE], th[0].emitters[0][mode][common.THREAT_ALT], th[thNode].location[common.XCOORD], th[thNode].location[common.YCOORD], th[thNode].location[common.ZCOORD])
            modeColor = domeColor(th[0].emitters[0][mode][2])

            ax.plot_wireframe(x, y, z, rstride = 3, cstride = 3, linewidth = 1, color = modeColor, alpha=0.5)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    ax.view_init(azim=30)

    plt.show()

def domeCreate(range, altitude, locX,locY,locz):
    u, v = np.mgrid[0:0.5*np.pi:50j, 0:2*np.pi:50j]

    x = range * np.sin(u)*np.cos(v) + locX
    y = range * np.sin(u)*np.sin(v) + locY
    z = altitude * np.cos(u) + locz

    return [x,y,z]

def domeColor(modeType):
    if(modeType == common.SEARCH):
        return 'darkslateblue'
    elif(modeType == common.ACQUISITION):
        return 'y'
    elif(modeType == common.TRACKING):
        return 'r'
    elif(modeType == common.MISSILE_GUIDANCE):
        return 'k'
