from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

def worldview(pf, th):
    
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    #flight path
    pfColor = 'b'
    totalFpNodePoints,_ = pf.flight_path.shape

    for node in range(totalFpNodePoints):
        ##nodes
        if(node == 0):
            ax.scatter(pf.flight_path[node][0], pf.flight_path[node][1], pf.flight_path[node][2], c=pfColor, marker='o', s=30)
        elif(node == totalFpNodePoints-1):
            ax.scatter(pf.flight_path[node][0], pf.flight_path[node][1], pf.flight_path[node][2], c=pfColor, marker='X', s=30)
        else:
            ax.scatter(pf.flight_path[node][0], pf.flight_path[node][1], pf.flight_path[node][2], c=pfColor, marker='>', s=30)
        
        ##lines
        if node is not 0:
            ax.plot([pf.flight_path[node-1][0], pf.flight_path[node][0]],[pf.flight_path[node-1][1], pf.flight_path[node][1]],zs=[pf.flight_path[node-1][2], pf.flight_path[node][2]], c=pfColor)
        
    #threats
    thColor = 'r'
    totalThreatNodePoints = th.__len__()

    for thNode in range(totalThreatNodePoints):
    #nodes
        ax.scatter(th[thNode].location[0], th[thNode].location[1], th[thNode].location[2], c=thColor, marker='*', s=150)
    #areas
        totalModes,_ = th[thNode].emitters[0].shape
        for mode in range(totalModes):
            # Make data
            u, v = np.mgrid[0:2*np.pi:200j, 0:np.pi:100j]
            
            x = th[0].emitters[0][mode][9] * np.cos(v) + th[thNode].location[0]
            y = th[0].emitters[0][mode][9] * np.sin(u)*np.sin(v) + th[thNode].location[1]
            z = th[0].emitters[0][mode][9] * np.cos(u)*np.sin(v) + th[thNode].location[2]

            # Plot the surface
            ax.plot_wireframe(x, y, z, rstride = 5, cstride = 5, linewidth = 1)
    
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()
