import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import NullFormatter  # useful for `logit` scale

# Fixing random state for reproducibility
np.random.seed(19680801)

# make up some data in the interval ]0, 1[
y = np.random.normal(loc=0.5, scale=0.4, size=1000)
y = y[(y > 0) & (y < 1)]
y.sort()
x = np.arange(len(y))

# plot with various axes scales
plt.figure(1)

# linear
plt.subplot(211)
plt.plot(x, y)
plt.yscale('linear')
plt.title('linear')
plt.grid(True)


# log
plt.subplot(212)
plt.plot(x, y)
plt.yscale('log')
plt.title('log')
plt.grid(True)


## symmetric log
#plt.subplot(223)
#plt.plot(x, y - y.mean())
#plt.yscale('symlog', linthreshy=0.01)
#plt.title('symlog')
#plt.grid(True)
#
## logit
#plt.subplot(224)
#plt.plot(x, y)
#plt.yscale('logit')
#plt.title('logit')
#plt.grid(True)