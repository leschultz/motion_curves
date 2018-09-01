from PyQt5 import QtGui  # Added to be able to import ovito
from matplotlib import pyplot as pl
from diffusion import diffusion
from averages import avg

import numpy as np
import os
import re

# Directories
firstdir = os.getcwd()
lammpstrjdir = firstdir+'/../data/lammpstrj/'

# Grab the file names from the lammpstrj directory
names = os.listdir(lammpstrjdir)

# Grab the names of runs to be averaged
count = 0
for name in names:
    names[count] = name.split('_run')[0]
    count += 1

# Remove repeated items
runs = list(set(names))

for item in runs:

    # Parameters from the naming convention
    value = item.split('_')
    system = value[0]
    side = value[1].split('-')[1]
    hold1 = int(value[2].split('-')[1])
    hold2 = int(value[3].split('-')[1])
    hold3 = int(value[4].split('-')[1])
    dumprate = int(value[6].split('-')[1])
    inittemp = int(value[7].split('K-')[0])
    finaltemp = int(value[7].split('K-')[1][:-1])

    timestep = ''
    ptimestep = value[5].split('-')[1]
    for letter in ptimestep:
        if letter == 'p':
            letter = '.'
        timestep += letter

    timestep = float(timestep)

    # Grab the MSD for N points
    N = 10
    newhold3 = []
    for i in range(hold3//N, hold3+1, hold3//N):
        newhold3.append(i)

    # Gather the MSD data for different time lengths
    timediff = []
    time = []
    for hold in newhold3:

        # Do averaging for files
        msd = avg(
                  item,
                  hold1+hold2,
                  hold1+hold2+hold,
                  timestep,
                  dumprate,
                  [hold1, hold1+hold2, hold1+hold2+hold],
                  10,
                  50
                  )

        # Grab diffusion with maximum number of points
        labels, diff, nh, fmt = diffusion(item, 0, int(hold/dumprate)+1)

        diff.insert(0, hold*timestep)
        timediff.append(diff)
        fmt += '%f '
        nh = 'Time[ps] '+nh


    timediff = np.transpose(np.array(timediff))

    count = 0
    for i in timediff[1:]:
        pl.plot(timediff[0], i, '.', label=labels[count])
        count += 1

    pl.xlabel('Time [ps]')
    pl.ylabel('Diffusion [*10^-4 cm^2 s^-1]')
    pl.grid(b=True, which='both')
    pl.tight_layout()
    pl.legend(loc='best')
    pl.savefig('../images/averaged/diffusion/'+item) 
    pl.clf()

    output = '../datacalculated/diffusion/'+item

    np.savetxt(output, np.column_stack(timediff), header=nh, fmt=fmt)
