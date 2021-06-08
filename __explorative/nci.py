import numpy as np
import numpy.matlib
import matplotlib.pyplot as plt

# Non coherent integration
def pulsint(x):
    return np.sqrt(np.sum(np.power(np.absolute(x),2),0)) 

npulse = 10

# Random data (100x10 vector)
x = numpy.matlib.repmat(np.sin(2*np.pi*np.arange(0,100)/100),npulse,1)+0.1*np.random.randn(npulse,100)

# Plot the result
plt.plot(pulsint(x))
plt.ylabel('Magnitude')
plt.show()