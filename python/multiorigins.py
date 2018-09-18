from PyQt5 import QtGui  # Added to be able to import ovito
from matplotlib import pyplot as pl
from scipy import stats as st
from single import analize

import pandas as pd
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
    names[count] = name.split('.lammpstrj')[0]
    count += 1

for item in names:

    string = 'Starting multiple origins method'
    print('+'*len(string))
    print(string)
    print('+'*len(string))

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

    # Split the relevant region in half
    N = 2
    newhold3 = hold3//N

    # Gather the MSD data for different time lengths
    msdmulti = {}
    diffmulti = {}
    timemulti = {}
    startpoints = []
    count = 0
    while count <= newhold3:

        points = [hold1, hold1+hold2+count, hold1+hold2+newhold3+count]

        printtext = 'Start and end points: '
        printtext += str((count*timestep, (newhold3+count)*timestep))
        printtext += ' [ps]'
        print('='*len(printtext))
        print(printtext)
        print('='*len(printtext))

        # Do averaging for files
        value = analize(
                       item,
                       points[1],
                       points[2],
                       timestep,
                       dumprate,
                       [points[0], points[1], points[2]],
                       10,
                       50
                       )

        data = value.calculate()
        msd = data['msd']
        diffusion = data['diffusion']
        time = data['time']

        # The beggining time for a diffusion calculation
        startpoints.append(count*timestep)

        # Grab diffusion values for each averaged for different times
        for key in msd:

            if msdmulti.get(key) is None:
                msdmulti[key] = []
                timemulti[key] = []

            msdmulti[key].append(msd[key])
            timemulti[key].append(time)

        for key in diffusion:
            if diffmulti.get(key) is None:
                diffmulti[key] = []

            diffmulti[key].append(diffusion[key])

        count += dumprate

    # Define the frequency of errorbars
    errorfreq = newhold3//10
    if errorfreq == 0:
        errorfreq = 1

    for key in msdmulti:

        if '_EIM' not in key:
            for i in list(range(0, len(msdmulti[key]))):
                pl.errorbar(
                            timemulti[key][i],
                            msdmulti[key][i],
                            yerr=msdmulti[key+'_EIM'][i],
                            ecolor='r',
                            errorevery=errorfreq,
                            )

    pl.xlabel('Time [ps]')
    pl.ylabel('MSD [A^2]')
    pl.grid(b=True, which='both')
    pl.tight_layout()
    pl.savefig('../images/msd/'+item+'_origins')
    pl.clf()

    fmt = ''
    nh = ''
    for key in diffmulti:

        fmt += '%f '
        nh += key+' '

        if '_Err' not in key:
            for i in list(range(0, len(diffmulti[key]))):
                pl.errorbar(
                            startpoints[i],
                            diffmulti[key][i],
                            yerr=diffmulti[key+'_Err'][i],
                            linestyle='dotted',
                            color='b',
                            ecolor='r',
                            marker='.',
                            errorevery=errorfreq,
                            )

    pl.xlabel('Time [ps]')
    pl.ylabel('Diffusion [*10^-4 cm^2 s^-1]')
    pl.grid(b=True, which='both')
    pl.tight_layout()
    pl.savefig('../images/diffusion/'+item+'_origins')
    pl.clf()

    output = '../datacalculated/diffusion/'+item+'_origins'

    df = pd.DataFrame(data=diffmulti)
    df.insert(0, 'time', startpoints)

    df.to_csv(output, sep=' ', index=False)

    print('\n')