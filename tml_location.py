import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

tml = pd.read_csv("atm_tml.csv")

x = tml.longitude
y = tml.latitude
tmlcod = tml.tmlcod

# colors = [x if tml.tmltyp == "hub"]

colors = []
for i in tml.tmltyp:
    if i == 'sub':
        colors.append('blue')
    elif i == 'hub':
        colors.append('red')

plt.xlabel('longitude')
plt.ylabel('latitude')
plt.scatter(x, y, c = colors, marker = '+')
plt.axis([0, 100, 0, 300])
plt.xticks(np.arange(0, 101, 20))
plt.yticks(np.arange(0, 301, 20))
plt.grid(True)
plt.show()

